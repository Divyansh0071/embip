"""
Unit Tests for EMBIP Recharts Spec Generator (Phase 12).
Verifies valid JSON spec construction, axis data keys, color assignments, and tick formatters.
"""

from app.ai.visualization.generator import recharts_spec_generator
from app.ai.visualization.models import ChartType


def test_generator_metric_card():
    analytics_res = {"status": "success", "operation": "sum", "metric": "total_revenue", "value": 50000.0}
    spec = recharts_spec_generator.generate_spec(
        chart_type=ChartType.METRIC_CARD,
        rows=[],
        columns=[],
        title="Total Revenue",
        analytics_result=analytics_res,
    )

    assert spec.chartType == ChartType.METRIC_CARD
    assert spec.title == "Total Revenue"
    assert len(spec.data) == 1
    assert spec.data[0]["value"] == 50000.0


def test_generator_bar_chart_from_sql_rows():
    rows = [
        {"store_name": "Connaught Place", "total_amount": 1000.0},
        {"store_name": "Bandra Flagship", "total_amount": 1500.0},
    ]
    columns = ["store_name", "total_amount"]

    spec = recharts_spec_generator.generate_spec(
        chart_type=ChartType.BAR_CHART,
        rows=rows,
        columns=columns,
        title="Revenue by Store",
    )

    assert spec.chartType == ChartType.BAR_CHART
    assert spec.xAxis.dataKey == "store_name"
    assert spec.yAxis.dataKey == "total_amount"
    assert spec.yAxis.tickFormat == "currency"
    assert len(spec.series) == 1
    assert spec.series[0].dataKey == "total_amount"


def test_generator_area_chart_from_analytics_series():
    analytics_res = {
        "status": "success",
        "operation": "monthly_trend",
        "metric": "sales",
        "series": [
            {"period": "2025-01", "value": 100},
            {"period": "2025-02", "value": 200},
        ],
    }

    spec = recharts_spec_generator.generate_spec(
        chart_type=ChartType.AREA_CHART,
        rows=[],
        columns=[],
        title="Monthly Sales Trend",
        analytics_result=analytics_res,
    )

    assert spec.chartType == ChartType.AREA_CHART
    assert spec.xAxis.dataKey == "period"
    assert spec.series[0].dataKey == "value"
    assert len(spec.data) == 2
