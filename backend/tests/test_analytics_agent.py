"""
Unit Tests for EMBIP Analytics Agent & Service (Phase 11).
Verifies intent classification, deterministic service execution,
and explanation generation with mocked LLM responses.
"""

from unittest.mock import AsyncMock, patch
import pytest

from app.ai.analytics.agent import analytics_agent
from app.ai.analytics.models import AnalyticsInput, AnalyticsIntentClassification
from app.ai.analytics.service import analytics_service


@pytest.mark.asyncio
async def test_analytics_agent_intent_classification():
    mock_classification = AnalyticsIntentClassification(
        operation="monthly_trend",
        metric_column="total_amount",
        time_column="transaction_date",
        reasoning="User asked for monthly sales breakdown",
    )
    with patch("app.ai.analytics.agent.llm_service.generate_structured", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = mock_classification

        res = await analytics_agent.classify_intent(
            question="What is the monthly revenue trend?",
            columns=["total_amount", "transaction_date"],
            sample_rows=[{"total_amount": 100, "transaction_date": "2025-01-01"}],
        )

        assert res is not None
        assert res.operation == "monthly_trend"
        assert res.metric_column == "total_amount"


@pytest.mark.asyncio
async def test_analytics_service_execution_success():
    inp = AnalyticsInput(
        columns=["store_name", "revenue"],
        rows=[
            {"store_name": "Store A", "revenue": 1000},
            {"store_name": "Store B", "revenue": 2000},
        ],
        operation="group_sum",
        metric_column="revenue",
        group_by="store_name",
    )

    res = await analytics_service.analyze(
        input_data=inp,
        sql_request_id="req-123",
        workspace_id="ws-456",
    )

    assert res.status == "success"
    assert res.operation == "group_sum"
    assert len(res.groups) == 2
    assert res.groups[0].group == "Store A"
    assert res.groups[0].value == 1000.0
    assert res.provenance.sql_request_id == "req-123"


@pytest.mark.asyncio
async def test_analytics_service_auto_classification_fallback():
    inp = AnalyticsInput(
        columns=["total_amount"],
        rows=[{"total_amount": 100}, {"total_amount": 200}],
        operation="",  # Empty operation triggers classification/fallback
        metric_column="total_amount",
    )

    with patch("app.ai.analytics.agent.analytics_agent.classify_intent", new_callable=AsyncMock) as mock_classify:
        mock_classify.return_value = None  # Force fallback to default 'sum'

        res = await analytics_service.analyze(input_data=inp, question="What is total amount?")

        assert res.status == "success"
        assert res.operation == "sum"
        assert res.value == 300.0
