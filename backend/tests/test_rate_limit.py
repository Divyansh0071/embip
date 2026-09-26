"""
Focused Unit & Integration Test Suite for API Rate Limiting (Phase 16C - Step 5).
Covers under-limit requests, over-limit HTTP 429 enforcement, Retry-After headers,
User ID isolation, workspace independence, IP fallback for unauthenticated routes,
SSE stream handshake behavior, toggling RATE_LIMIT_ENABLED, and limiter state resets.
"""

import os
from unittest.mock import AsyncMock, patch
import jwt
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.rate_limit import limiter
from app.main import app

client = TestClient(app)


def create_token(user_id: str, workspace_id: str = "ws-123", role: str = "ANALYST") -> str:
    """Helper to generate JWT Bearer tokens for rate limit testing."""
    payload = {
        "sub": user_id,
        "email": f"{user_id}@novamart.com",
        "user_metadata": {
            "role": role,
            "org_id": "org-test-123",
            "workspace_id": workspace_id,
        },
    }
    return jwt.encode(payload, "secret-key", algorithm="HS256")


@pytest.fixture(autouse=True)
def reset_rate_limiter_state():
    """Reset limiter state before every test to ensure test isolation."""
    limiter.reset()
    original_enabled = settings.RATE_LIMIT_ENABLED
    settings.RATE_LIMIT_ENABLED = True
    yield
    limiter.reset()
    settings.RATE_LIMIT_ENABLED = original_enabled


# ------------------------------------------------------------------------------
# 1. UNDER-LIMIT & OVER-LIMIT HTTP 429 TESTS
# ------------------------------------------------------------------------------

def test_rate_limit_health_under_and_over_limit():
    """Verify requests under IP limit succeed and request exceeding limit returns HTTP 429 with Retry-After header."""
    with patch.object(settings, "RATE_LIMIT_HEALTH_PER_MINUTE", 3):
        # Requests 1..3 should succeed
        for i in range(3):
            resp = client.get("/health")
            assert resp.status_code == 200, f"Request {i+1} failed"

        # Request 4 should trigger 429
        resp = client.get("/health")
        assert resp.status_code == 429
        data = resp.json()
        assert "Rate limit exceeded" in data["detail"]
        assert data["retry_after_seconds"] == 60
        assert resp.headers.get("Retry-After") == "60"


# ------------------------------------------------------------------------------
# 2. USER ISOLATION & WORKSPACE CROSS-CONTEXT TESTS
# ------------------------------------------------------------------------------

@patch("app.ai.rag.service.rag_service.retrieve")
def test_rate_limit_user_isolation(mock_retrieve):
    """Verify User A hitting rate limit does NOT block User B."""
    mock_retrieve.return_value = AsyncMock(
        query="sales", workspace_id="ws-123", results=[], total_retrieved=0
    )

    token_a = create_token("user-alpha")
    token_b = create_token("user-beta")

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    with patch.object(settings, "RATE_LIMIT_SEARCH_PER_MINUTE", 2):
        # User A uses quota
        res1 = client.post("/api/v1/rag/search", json={"query": "sales"}, headers=headers_a)
        res2 = client.post("/api/v1/rag/search", json={"query": "sales"}, headers=headers_a)
        assert res1.status_code == 200
        assert res2.status_code == 200

        # User A request 3 fails with 429
        res3 = client.post("/api/v1/rag/search", json={"query": "sales"}, headers=headers_a)
        assert res3.status_code == 429

        # User B should still succeed
        res_b = client.post("/api/v1/rag/search", json={"query": "sales"}, headers=headers_b)
        assert res_b.status_code == 200


@patch("app.ai.rag.service.rag_service.retrieve")
def test_different_users_same_workspace_independently_limited(mock_retrieve):
    """Verify distinct users in the same workspace are limited independently."""
    mock_retrieve.return_value = AsyncMock(
        query="q", workspace_id="shared-ws", results=[], total_retrieved=0
    )

    token_u1 = create_token("user-1", workspace_id="shared-ws")
    token_u2 = create_token("user-2", workspace_id="shared-ws")

    with patch.object(settings, "RATE_LIMIT_SEARCH_PER_MINUTE", 1):
        r1 = client.post("/api/v1/rag/search", json={"query": "test"}, headers={"Authorization": f"Bearer {token_u1}"})
        assert r1.status_code == 200

        r1_blocked = client.post("/api/v1/rag/search", json={"query": "test"}, headers={"Authorization": f"Bearer {token_u1}"})
        assert r1_blocked.status_code == 429

        r2 = client.post("/api/v1/rag/search", json={"query": "test"}, headers={"Authorization": f"Bearer {token_u2}"})
        assert r2.status_code == 200


@patch("app.ai.rag.service.rag_service.retrieve")
def test_same_user_limited_across_different_workspace_contexts(mock_retrieve):
    """Verify rate limit is scoped to user_id even if the user switches workspace claims."""
    mock_retrieve.return_value = AsyncMock(
        query="q", workspace_id="ws-1", results=[], total_retrieved=0
    )

    token_ws1 = create_token("user-sam", workspace_id="ws-1")
    token_ws2 = create_token("user-sam", workspace_id="ws-2")

    with patch.object(settings, "RATE_LIMIT_SEARCH_PER_MINUTE", 1):
        # User Sam calls endpoint in ws-1
        r1 = client.post("/api/v1/rag/search", json={"query": "q"}, headers={"Authorization": f"Bearer {token_ws1}"})
        assert r1.status_code == 200

        # User Sam calling endpoint in ws-2 is blocked because rate limit is per user ID
        r2 = client.post("/api/v1/rag/search", json={"query": "q"}, headers={"Authorization": f"Bearer {token_ws2}"})
        assert r2.status_code == 429


# ------------------------------------------------------------------------------
# 3. UNAUTHENTICATED ROUTE IP FALLBACK TESTS
# ------------------------------------------------------------------------------

def test_unauthenticated_ip_fallback_rate_limiting():
    """Verify root and health endpoints fallback to client IP rate limiting."""
    with patch.object(settings, "RATE_LIMIT_HEALTH_PER_MINUTE", 2):
        r1 = client.get("/")
        r2 = client.get("/")
        assert r1.status_code == 200
        assert r2.status_code == 200

        r3 = client.get("/")
        assert r3.status_code == 429


# ------------------------------------------------------------------------------
# 4. SSE STREAM HANDSHAKE & STREAM INTEGRITY TESTS
# ------------------------------------------------------------------------------

async def fake_sse_generator():
    yield "event: message\ndata: chunk 1\n\n"
    yield "event: message\ndata: chunk 2\n\n"


@patch("app.ai.orchestration.service.orchestration_service.ask_stream")
def test_sse_stream_handshake_rate_limited(mock_ask_stream):
    """Verify rate limiting applies to initial SSE request handshake, and stream consumes without interruption once 200 OK."""
    mock_ask_stream.return_value = fake_sse_generator()

    token = create_token("user-sse")
    headers = {"Authorization": f"Bearer {token}"}

    with patch.object(settings, "RATE_LIMIT_ASK_PER_MINUTE", 1):
        # Request 1: Handshake succeeds
        resp1 = client.get("/api/v1/ask/stream?question=test", headers=headers)
        assert resp1.status_code == 200
        assert resp1.headers["content-type"].startswith("text/event-stream")
        assert "chunk 1" in resp1.text

        # Request 2: Handshake blocked
        resp2 = client.get("/api/v1/ask/stream?question=test", headers=headers)
        assert resp2.status_code == 429


# ------------------------------------------------------------------------------
# 5. CONFIGURATION TOGGLE TESTS (RATE_LIMIT_ENABLED=False)
# ------------------------------------------------------------------------------

def test_rate_limit_disabled_configuration():
    """Verify setting RATE_LIMIT_ENABLED=False disables enforcement completely."""
    settings.RATE_LIMIT_ENABLED = False
    limiter.enabled = False

    with patch.object(settings, "RATE_LIMIT_HEALTH_PER_MINUTE", 1):
        for _ in range(5):
            resp = client.get("/health")
            assert resp.status_code == 200
