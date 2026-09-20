"""
Integration Tests for LangGraph Multi-Agent Orchestration with Visualization Agent (Phase 12).
Verifies state machine execution flow from SQL/Analytics -> Visualization Agent.
"""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.ai.orchestration.models import PlannerPlan
from app.ai.orchestration.nodes import visualization_node
from app.ai.orchestration.router import orchestration_router
from app.ai.orchestration.service import orchestration_service


@pytest.mark.asyncio
async def test_orchestration_router_sequential_visualization_routing():
    state = {
        "question": "Show a bar chart of monthly revenue",
        "plan": {
            "intent": "combined",
            "requires_sql": True,
            "requires_rag": False,
            "requires_analytics": True,
            "requires_visualization": True,
            "reason": "Needs SQL, Analytics, and Visualization",
        },
    }

    initial_routes = orchestration_router.route(state)
    assert initial_routes == ["sql_node"]

    after_sql_route = orchestration_router.route_after_sql(state)
    assert after_sql_route == "analytics_node"

    after_analytics_route = orchestration_router.route_after_analytics(state)
    assert after_analytics_route == "visualization_node"


@pytest.mark.asyncio
async def test_visualization_node_execution():
    state = {
        "question": "Show revenue by store name",
        "workspace_id": "ws-123",
        "sql_result": {
            "status": "success",
            "columns": ["store_name", "total_amount"],
            "rows": [
                {"store_name": "Store A", "total_amount": 1000.0},
                {"store_name": "Store B", "total_amount": 2000.0},
            ],
        },
    }

    res = await visualization_node(state)

    assert "visualization_result" in res
    viz_res = res["visualization_result"]
    assert viz_res["status"] == "success"
    assert viz_res["spec"]["chartType"] == "bar_chart"


@pytest.mark.asyncio
async def test_orchestration_service_full_pipeline_to_visualization():
    mock_db = AsyncMock()

    mock_plan = PlannerPlan(
        intent="visualization",
        requires_sql=True,
        requires_rag=False,
        requires_analytics=True,
        requires_visualization=True,
        reason="Full pipeline execution",
    )

    mock_sql_response = MagicMock()
    mock_sql_response.model_dump.return_value = {
        "request_id": "sql-999",
        "status": "success",
        "sql": "SELECT store_name, total_amount FROM sales_transactions;",
        "explanation": "Query store sales",
        "tables_used": ["sales_transactions"],
        "columns": ["store_name", "total_amount"],
        "rows": [
            {"store_name": "Store A", "total_amount": 1000.0},
            {"store_name": "Store B", "total_amount": 2000.0},
        ],
        "row_count": 2,
        "execution_time_ms": 10.0,
    }

    with patch("app.ai.orchestration.nodes.planner_agent.plan", new_callable=AsyncMock) as mock_planner, \
         patch("app.ai.orchestration.nodes.sql_service.execute_question", new_callable=AsyncMock) as mock_sql:

        mock_planner.return_value = mock_plan
        mock_sql.return_value = mock_sql_response

        res = await orchestration_service.ask(
            question="Show a bar chart of store revenue",
            workspace_id="00000000-0000-0000-0000-000000000001",
            user_id="00000000-0000-0000-0000-000000000001",
            db=mock_db,
        )

        assert res.status == "completed"
        assert res.plan.requires_visualization is True
        assert res.results["sql"] is not None
        assert res.results["analytics"] is not None
        assert res.results["visualization"] is not None
        assert res.results["visualization"]["status"] == "success"
        assert res.results["visualization"]["spec"]["chartType"] == "grouped_bar_chart" or res.results["visualization"]["spec"]["chartType"] == "bar_chart" or res.results["visualization"]["spec"]["chartType"] == "pie_chart"
