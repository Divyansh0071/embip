"""
Unit Tests for EMBIP Chart Decision Matrix (Phase 12).
Verifies deterministic chart selection based on dataset dimensions, cardinality, and feature types.
"""

import pytest
from app.ai.visualization.decision_matrix import chart_decision_matrix
from app.ai.visualization.models import ChartType


def test_decision_matrix_scalar_value_returns_metric_card():
    analytics_res = {"status": "success", "operation": "sum", "value": 1500.0}
    selected = chart_decision_matrix.select_chart_type(rows=[], columns=[], analytics_result=analytics_res)
    assert selected == ChartType.METRIC_CARD


def test_decision_matrix_single_row_returns_metric_card():
    rows = [{"total_revenue": 10000.0}]
    selected = chart_decision_matrix.select_chart_type(rows=rows, columns=["total_revenue"])
    assert selected == ChartType.METRIC_CARD


def test_decision_matrix_time_series_returns_area_or_line_chart():
    analytics_res = {
        "status": "success",
        "operation": "monthly_trend",
        "series": [
            {"period": "2025-01", "value": 100},
            {"period": "2025-02", "value": 200},
            {"period": "2025-03", "value": 300},
        ],
    }
    selected = chart_decision_matrix.select_chart_type(rows=[], columns=[], analytics_result=analytics_res)
    assert selected == ChartType.AREA_CHART


def test_decision_matrix_small_grouping_returns_pie_chart():
    analytics_res = {
        "status": "success",
        "operation": "group_sum",
        "groups": [
            {"group": "Cat A", "value": 100},
            {"group": "Cat B", "value": 200},
            {"group": "Cat C", "value": 300},
        ],
    }
    selected = chart_decision_matrix.select_chart_type(rows=[], columns=[], analytics_result=analytics_res)
    assert selected == ChartType.PIE_CHART


def test_decision_matrix_large_grouping_returns_horizontal_bar_chart():
    analytics_res = {
        "status": "success",
        "operation": "group_sum",
        "groups": [{"group": f"Cat {i}", "value": i * 10} for i in range(10)],
    }
    selected = chart_decision_matrix.select_chart_type(rows=[], columns=[], analytics_result=analytics_res)
    assert selected == ChartType.HORIZONTAL_BAR_CHART


def test_decision_matrix_grouped_multiple_metrics_returns_grouped_bar_chart():
    rows = [
        {"store_name": "Store A", "rev_2024": 100, "rev_2025": 120},
        {"store_name": "Store B", "rev_2024": 200, "rev_2025": 240},
    ]
    columns = ["store_name", "rev_2024", "rev_2025"]
    selected = chart_decision_matrix.select_chart_type(rows=rows, columns=columns)
    assert selected == ChartType.GROUPED_BAR_CHART


def test_decision_matrix_explicit_preference_override():
    rows = [{"cat": "A", "val": 10}]
    selected = chart_decision_matrix.select_chart_type(
        rows=rows,
        columns=["cat", "val"],
        preferred_type=ChartType.LINE_CHART,
    )
    assert selected == ChartType.LINE_CHART
