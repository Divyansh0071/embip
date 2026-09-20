"""
Integration Tests for LangGraph Multi-Agent Orchestration with Analytics Agent (Phase 11).
Verifies state machine execution flow: Planner -> SQL Agent -> Analytics Agent -> Merge Node.
"""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.ai.orchestration.models import PlannerPlan
from app.ai.orchestration.nodes import analytics_node, planner_node, sql_node
from app.ai.orchestration.router import orchestration_router
from app.ai.orchestration.service import orchestration_service


@pytest.mark.asyncio
async def test_orchestration_router_sequential_analytics_routing():
    state = {
        "question": "What is the monthly revenue trend?",
        "plan": {
            "intent": "analytics_trend",
            "requires_sql": True,
            "requires_rag": False,
            "requires_analytics": True,
            "requires_visualization": False,
            "reason": "Needs SQL query and monthly trend calculation",
        },
    }

    initial_routes = orchestration_router.route(state)
    assert initial_routes == ["sql_node"]

    next_route = orchestration_router.route_after_sql(state)
    assert next_route == "analytics_node"


@pytest.mark.asyncio
async def test_analytics_node_with_sql_result():
    state = {
        "question": "What is the total revenue?",
        "workspace_id": "ws-123",
        "sql_result": {
            "status": "success",
            "request_id": "sql-456",
            "columns": ["total_amount"],
            "rows": [{"total_amount": 100.0}, {"total_amount": 200.0}],
        },
    }

    res = await analytics_node(state)

    assert "analytics_result" in res
    analytics_res = res["analytics_result"]
    assert analytics_res["status"] in ["success", "warning"]
    assert analytics_res["value"] == 300.0
    assert analytics_res["operation"] == "sum"


@pytest.mark.asyncio
async def test_analytics_node_skips_when_no_sql_data():
    state = {
        "question": "What is the total revenue?",
        "workspace_id": "ws-123",
        "sql_result": {
            "status": "error",
            "error": "Table sales_transactions does not exist",
        },
    }

    res = await analytics_node(state)

    assert "analytics_result" in res
    assert res["analytics_result"]["status"] == "skipped"
    assert "No SQL tabular data available" in res["analytics_result"]["error"]


@pytest.mark.asyncio
async def test_orchestration_service_sql_and_analytics_flow():
    mock_db = AsyncMock()

    mock_plan = PlannerPlan(
        intent="store_analytics",
        requires_sql=True,
        requires_rag=False,
        requires_analytics=True,
        requires_visualization=False,
        reason="Calculate store group sum",
    )

    mock_sql_response = MagicMock()
    mock_sql_response.model_dump.return_value = {
        "request_id": "sql-789",
        "status": "success",
        "sql": "SELECT store_name, total_amount FROM sales_transactions;",
        "explanation": "Select store_name and total_amount",
        "tables_used": ["sales_transactions"],
        "columns": ["store_name", "total_amount"],
        "rows": [
            {"store_name": "Store A", "total_amount": 150.0},
            {"store_name": "Store B", "total_amount": 350.0},
        ],
        "row_count": 2,
        "execution_time_ms": 12.5,
    }

    with patch("app.ai.orchestration.nodes.planner_agent.plan", new_callable=AsyncMock) as mock_planner, \
         patch("app.ai.orchestration.nodes.sql_service.execute_question", new_callable=AsyncMock) as mock_sql:

        mock_planner.return_value = mock_plan
        mock_sql.return_value = mock_sql_response

        res = await orchestration_service.ask(
            question="Calculate total revenue grouped by store name",
            workspace_id="00000000-0000-0000-0000-000000000001",
            user_id="00000000-0000-0000-0000-000000000001",
            db=mock_db,
        )

        assert res.status == "completed"
        assert res.plan.requires_analytics is True
        assert res.results["sql"] is not None
        assert res.results["analytics"] is not None
        assert res.results["analytics"]["status"] == "success"
        assert res.results["analytics"]["operation"] == "group_sum"
        assert len(res.results["analytics"]["groups"]) == 2
