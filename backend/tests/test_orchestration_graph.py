"""
Unit & Integration Test Suite for LangGraph Multi-Agent Orchestration (Phase 10).
"""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.ai.orchestration.graph import orchestration_graph
from app.ai.orchestration.models import PlannerPlan
from app.ai.orchestration.service import OrchestrationService, orchestration_service


@pytest.mark.asyncio
async def test_orchestration_service_sql_only_flow():
    """Verify orchestration executes SQL node when Planner selects SQL capability."""
    mock_plan = PlannerPlan(
        intent="sql_query",
        requires_sql=True,
        requires_rag=False,
        requires_analytics=False,
        requires_visualization=False,
        reason="Query asks for store sales data.",
    )

    mock_sql_response = MagicMock()
    mock_sql_response.model_dump.return_value = {
        "question": "Total sales by store?",
        "sql": "SELECT name, SUM(total_amount) FROM stores JOIN sales_transactions ON stores.id=sales_transactions.store_id GROUP BY name;",
        "explanation": "Calculates revenue per store.",
        "tables_used": ["stores", "sales_transactions"],
        "columns": ["name", "sum"],
        "rows": [{"name": "Downtown Store", "sum": 50000.0}],
        "row_count": 1,
        "execution_time_ms": 12.5,
        "status": "success",
    }

    service = OrchestrationService()

    with patch("app.ai.orchestration.nodes.planner_agent.plan", new_callable=AsyncMock) as mock_planner, \
         patch("app.ai.orchestration.nodes.sql_service.execute_question", new_callable=AsyncMock) as mock_sql:
        
        mock_planner.return_value = mock_plan
        mock_sql.return_value = mock_sql_response

        mock_db = AsyncMock()

        resp = await service.ask(
            question="Total sales by store?",
            workspace_id="ws-test-123",
            user_id="usr-test-123",
            db=mock_db,
        )

        assert resp.status == "completed"
        assert resp.plan.requires_sql is True
        assert resp.plan.requires_rag is False
        assert "sql" in resp.results
        assert resp.results["sql"]["row_count"] == 1
        assert resp.results["sql"]["rows"][0]["name"] == "Downtown Store"


@pytest.mark.asyncio
async def test_orchestration_service_rag_only_flow():
    """Verify orchestration executes RAG node when Planner selects RAG capability."""
    mock_plan = PlannerPlan(
        intent="rag_search",
        requires_sql=False,
        requires_rag=True,
        requires_analytics=False,
        requires_visualization=False,
        reason="Query asks for document policy information.",
    )

    mock_rag_response = MagicMock()
    mock_rag_response.model_dump.return_value = {
        "query": "What is return policy?",
        "workspace_id": "ws-test-123",
        "total_retrieved": 1,
        "results": [
            {
                "chunk_id": "chk-1",
                "filename": "return_policy.pdf",
                "chunk_index": 0,
                "content": "Items can be returned within 30 days.",
                "score": 0.95,
            }
        ],
    }

    service = OrchestrationService()

    with patch("app.ai.orchestration.nodes.planner_agent.plan", new_callable=AsyncMock) as mock_planner, \
         patch("app.ai.orchestration.nodes.rag_service.retrieve", new_callable=AsyncMock) as mock_rag:
        
        mock_planner.return_value = mock_plan
        mock_rag.return_value = mock_rag_response

        mock_db = AsyncMock()

        resp = await service.ask(
            question="What is return policy?",
            workspace_id="ws-test-123",
            user_id="usr-test-123",
            db=mock_db,
        )

        assert resp.status == "completed"
        assert resp.plan.requires_sql is False
        assert resp.plan.requires_rag is True
        assert "rag" in resp.results
        assert resp.results["rag"]["total_retrieved"] == 1


@pytest.mark.asyncio
async def test_orchestration_service_analytics_placeholder_flow():
    """Verify orchestration executes analytics placeholder adapter when selected by Planner."""
    mock_plan = PlannerPlan(
        intent="analytics",
        requires_sql=False,
        requires_rag=False,
        requires_analytics=True,
        requires_visualization=False,
        reason="Query requests complex statistical regression.",
    )

    service = OrchestrationService()

    with patch("app.ai.orchestration.nodes.planner_agent.plan", new_callable=AsyncMock) as mock_planner:
        mock_planner.return_value = mock_plan
        mock_db = AsyncMock()

        resp = await service.ask(
            question="Perform regression analysis on sales growth.",
            workspace_id="ws-test-123",
            user_id="usr-test-123",
            db=mock_db,
        )

        assert resp.results["analytics"]["status"] in ["skipped", "success", "warning"]
