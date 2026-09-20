"""
Unit Tests for EMBIP Visualization Agent & Service (Phase 12).
Verifies chart spec generation, decision matrix selection, and mocked LLM metadata enrichment.
"""

from unittest.mock import AsyncMock, patch
import pytest

from app.ai.visualization.agent import visualization_agent
from app.ai.visualization.models import ChartType, VisualizationMetadata
from app.ai.visualization.service import visualization_service


@pytest.mark.asyncio
async def test_visualization_agent_metadata_generation():
    mock_metadata = VisualizationMetadata(
        title="Top Store Sales Revenue",
        subtitle="Revenue performance comparison for 2025",
        insight="NovaMart Connaught Place is the top performing store.",
    )

    with patch("app.ai.visualization.agent.llm_service.generate_structured", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = mock_metadata

        res = await visualization_agent.generate_metadata(
            question="Which store generated the highest revenue?",
            chart_type=ChartType.BAR_CHART,
            data_sample=[{"store_name": "Connaught Place", "total_amount": 385000000}],
        )

        assert res is not None
        assert res.title == "Top Store Sales Revenue"
        assert "Connaught Place" in res.insight


@pytest.mark.asyncio
async def test_visualization_service_generate_spec_success():
    sql_res = {
        "columns": ["store_name", "total_amount"],
        "rows": [
            {"store_name": "Store A", "total_amount": 1000},
            {"store_name": "Store B", "total_amount": 2000},
        ],
    }

    res = await visualization_service.generate_spec(
        question="Show total revenue by store",
        sql_result=sql_res,
    )

    assert res.status == "success"
    assert res.spec is not None
    assert res.spec.chartType == ChartType.BAR_CHART
    assert res.spec.xAxis.dataKey == "store_name"
    assert res.spec.series[0].dataKey == "total_amount"


@pytest.mark.asyncio
async def test_visualization_service_skips_on_empty_data():
    res = await visualization_service.generate_spec(
        question="Show revenue trend",
        sql_result={"columns": [], "rows": []},
        analytics_result=None,
    )

    assert res.status == "skipped"
    assert "No dataset rows" in res.error
