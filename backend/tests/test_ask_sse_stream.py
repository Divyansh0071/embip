"""
Comprehensive Test Suite for Phase 15 SSE Real-Time Streaming Engine.
Covering:
- Authentication & Workspace Isolation
- Content-Type (text/event-stream)
- Strict Event Schema & Allowlist Enforcement
- No Raw Node Output Leakage
- No Prompt / Chain-of-thought / Secret Leakage
- Sanitized Error Response (No str(e) sent to client)
- Exactly One Graph Execution (astream_events call count = 1, ainvoke = 0)
- Stream Completion & Dynamic Routing
- Validation & Report Integration
- POST /api/v1/ask Regression Safety
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.security import get_current_user
from app.ai.orchestration.stream import orchestration_streamer, ALLOWLISTED_NODES

client = TestClient(app)


def mock_user_obj(user_id: str = "usr-sse-test", workspace_id: str = "ws-test-456"):
    """Helper mock User object matching User model attribute interface."""
    user = MagicMock()
    user.id = user_id
    user.active_workspace_id = workspace_id
    return user


# 1. Authentication Rejection Test
def test_ask_stream_unauthenticated_rejected():
    """Verify GET /api/v1/ask/stream without Authorization header returns HTTP 401."""
    app.dependency_overrides.pop(get_current_user, None)
    response = client.get("/api/v1/ask/stream?question=What is total revenue?")
    assert response.status_code == 401
    assert "detail" in response.json()


# 2. Workspace Isolation Test
def test_ask_stream_workspace_isolation():
    """Verify authenticated user workspace_id is derived from user object context."""
    user = mock_user_obj("usr-ws-1", "ws-test-456")
    app.dependency_overrides[get_current_user] = lambda: user
    
    try:
        with patch("app.ai.orchestration.service.orchestration_service.ask_stream") as mock_ask_stream:
            async def dummy_gen(*args, **kwargs):
                yield "data: {\"event\": \"stream_started\"}\n\n"

            mock_ask_stream.return_value = dummy_gen()
            response = client.get("/api/v1/ask/stream?question=Sales?")
            assert response.status_code == 200
            
            # Verify workspace_id passed to orchestration is the authenticated user's workspace
            mock_ask_stream.assert_called_once()
            _, kwargs = mock_ask_stream.call_args
            assert kwargs.get("workspace_id") == "ws-test-456"
            assert kwargs.get("user_id") == "usr-ws-1"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


# 3. Content-Type Header Test
def test_ask_stream_content_type():
    """Verify streaming response headers specify text/event-stream."""
    user = mock_user_obj()
    app.dependency_overrides[get_current_user] = lambda: user
    
    try:
        response = client.get("/api/v1/ask/stream?question=Show top products")
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        assert response.headers["cache-control"] == "no-cache"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


# 4. Streamer Yields Allowed Event Schema
@pytest.mark.asyncio
async def test_orchestration_streamer_event_schema_and_allowlist():
    """Verify streamer yields events conforming to strict allowlisted schema."""
    events = []
    async for chunk in orchestration_streamer.stream_events(
        question="What was total revenue?",
        workspace_id="ws-test-456",
        user_id="usr-123",
    ):
        events.append(chunk)

    assert len(events) >= 2
    assert "data: {" in events[0]
    
    # Parse first event (stream_started)
    first_payload = json.loads(events[0].replace("data: ", "").strip())
    assert first_payload["event"] == "stream_started"
    assert "request_id" in first_payload
    assert first_payload["question"] == "What was total revenue?"
    assert "status" in first_payload

    # Parse last event (stream_completed)
    last_payload = json.loads(events[-1].replace("data: ", "").strip())
    assert last_payload["event"] == "stream_completed"
    assert "request_id" in last_payload
    assert "plan" in last_payload
    assert "results" in last_payload
    assert "execution_time_ms" in last_payload


# 5 & 6. No Raw Node Output, Prompt, or Secret Leakage
@pytest.mark.asyncio
async def test_no_raw_output_or_secret_leakage_in_progress_events():
    """Verify progress events (node_start, node_complete) contain NO raw node outputs or sensitive data."""
    events = []
    async for chunk in orchestration_streamer.stream_events(
        question="Analyze sales",
        workspace_id="ws-test-456",
    ):
        if "data: {" in chunk:
            payload = json.loads(chunk.replace("data: ", "").strip())
            events.append(payload)

    for event in events:
        event_type = event.get("event")
        if event_type in ("node_start", "node_complete"):
            # Ensure allowlisted keys only
            assert "output" not in event, f"Raw node output leaked in {event_type}!"
            assert "state" not in event, f"Graph state leaked in {event_type}!"
            assert "prompt" not in event
            assert "secret" not in event
            assert "api_key" not in event
            assert event.get("node") in ALLOWLISTED_NODES


# 7. Sanitized Error Response (No str(e) Leakage)
@pytest.mark.asyncio
async def test_sanitized_error_response_on_exception():
    """Verify exceptions in streamer output generic error message without leaking internal trace/str(e)."""
    with patch("app.ai.orchestration.stream.orchestration_graph.astream_events") as mock_stream:
        mock_stream.side_effect = RuntimeError("Internal Database Secret Failure: postgresql://admin:secret123@db:5432/main")

        events = []
        async for chunk in orchestration_streamer.stream_events(
            question="Crash test",
            workspace_id="ws-test-456",
        ):
            if "data: {" in chunk:
                payload = json.loads(chunk.replace("data: ", "").strip())
                events.append(payload)

        # Verify stream_started followed by sanitized stream_error
        assert len(events) == 2
        assert events[0]["event"] == "stream_started"
        assert events[1]["event"] == "stream_error"
        assert events[1]["status"] == "failed"
        # Must be generic sanitized message, NOT internal exception string
        assert events[1]["error"] == "An unexpected error occurred during processing."
        assert "secret123" not in json.dumps(events[1])
        assert "postgresql://" not in json.dumps(events[1])


# 8 & 9. Exactly One Graph Execution
@pytest.mark.asyncio
async def test_exactly_one_graph_execution():
    """Verify graph is invoked exactly ONCE via astream_events and ainvoke is NEVER called."""
    with patch("app.ai.orchestration.stream.orchestration_graph.astream_events") as mock_astream, \
         patch("app.ai.orchestration.graph.orchestration_graph.ainvoke") as mock_ainvoke:

        async def mock_events(*args, **kwargs):
            yield {
                "event": "on_chain_end",
                "name": "LangGraph",
                "data": {
                    "output": {
                        "status": "completed",
                        "merged_results": {"sql": {}, "report": {}},
                        "plan": {"intent": "general"},
                    }
                }
            }

        mock_astream.side_effect = mock_events

        events = []
        async for chunk in orchestration_streamer.stream_events("Test question", "ws-123"):
            events.append(chunk)

        # Assert exactly ONE streaming call and ZERO invoke calls
        assert mock_astream.call_count == 1
        assert mock_ainvoke.call_count == 0


# 10. Report & Validation Integration in Stream Completion
@pytest.mark.asyncio
async def test_stream_completion_validation_report_integration():
    """Verify stream_completed event contains merged report and validation results."""
    events = []
    async for chunk in orchestration_streamer.stream_events(
        question="What was Q3 growth?",
        workspace_id="ws-test-456",
    ):
        if "stream_completed" in chunk:
            payload = json.loads(chunk.replace("data: ", "").strip())
            events.append(payload)

    assert len(events) == 1
    completed_event = events[0]
    assert completed_event["event"] == "stream_completed"
    results = completed_event.get("results") or {}
    assert "report" in results
    assert "validation" in results
    assert "sql" in results


# 11. POST /api/v1/ask Regression Test
def test_post_ask_endpoint_regression():
    """Verify existing POST /api/v1/ask endpoint functionality is preserved."""
    user = mock_user_obj()
    app.dependency_overrides[get_current_user] = lambda: user
    
    try:
        response = client.post(
            "/api/v1/ask",
            json={"question": "What is our total revenue?"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "request_id" in data
        assert "question" in data
        assert "status" in data
        assert "plan" in data
        assert "results" in data
        assert "execution_time_ms" in data
    finally:
        app.dependency_overrides.pop(get_current_user, None)
