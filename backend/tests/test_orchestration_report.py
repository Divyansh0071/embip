"""
Integration Tests for LangGraph Multi-Agent Orchestration with Report Generator Agent (Phase 14).
"""

import pytest
from app.ai.orchestration.graph import orchestration_graph
from app.ai.orchestration.router import orchestration_router
from app.ai.orchestration.state import OrchestrationState


def test_orchestration_router_report_node():
    state: OrchestrationState = {
        "question": "What is our quarterly profit?",
        "validation_result": {"action": "pass"},
        "retry_count": 0,
    }

    # route_after_validation should route to report_node when validation passes
    next_node = orchestration_router.route_after_validation(state)
    assert next_node == "report_node"


@pytest.mark.asyncio
async def test_orchestration_graph_with_report_execution():
    initial_state: OrchestrationState = {
        "request_id": "req-rep-123",
        "workspace_id": "00000000-0000-0000-0000-000000000000",
        "question": "Summarize company revenue for last year.",
        "retry_count": 0,
    }

    final_state = await orchestration_graph.ainvoke(initial_state)

    assert final_state is not None
    assert "merged_results" in final_state
    merged = final_state["merged_results"]
    assert "report" in merged
    assert final_state["status"] in ["completed", "partial", "failed"]
