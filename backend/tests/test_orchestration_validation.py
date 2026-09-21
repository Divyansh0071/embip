"""
Integration Tests for LangGraph Multi-Agent Orchestration with Validation & Retry Loop (Phase 13).
"""

import pytest
from app.ai.orchestration.graph import orchestration_graph
from app.ai.orchestration.router import orchestration_router
from app.ai.orchestration.state import OrchestrationState


def test_orchestration_router_validation_node():
    state: OrchestrationState = {
        "question": "What is our Q3 revenue?",
        "plan": {
            "intent": "sql_query",
            "requires_sql": True,
            "requires_rag": False,
            "requires_analytics": False,
            "requires_visualization": False,
        }
    }

    # route_after_sql should route to validation_node when no analytics/viz required
    next_node = orchestration_router.route_after_sql(state)
    assert next_node == "validation_node"


def test_orchestration_router_retry_loop():
    # Test retry routing when validation requests retry and retry_count < 2
    state_retry: OrchestrationState = {
        "question": "Show metrics",
        "validation_result": {"action": "retry"},
        "retry_count": 0,
    }
    assert orchestration_router.route_after_validation(state_retry) == "planner"

    # Test report_node routing when retry threshold reached (retry_count = 2)
    state_max: OrchestrationState = {
        "question": "Show metrics",
        "validation_result": {"action": "retry"},
        "retry_count": 2,
    }
    assert orchestration_router.route_after_validation(state_max) == "report_node"



@pytest.mark.asyncio
async def test_orchestration_graph_with_validation_execution():
    initial_state: OrchestrationState = {
        "request_id": "req-val-123",
        "workspace_id": "00000000-0000-0000-0000-000000000000",
        "question": "What is the capital of France?",
        "retry_count": 0,
    }

    final_state = await orchestration_graph.ainvoke(initial_state)

    assert final_state is not None
    assert "merged_results" in final_state
    merged = final_state["merged_results"]
    assert "validation" in merged
    assert final_state["status"] in ["completed", "partial", "failed"]

