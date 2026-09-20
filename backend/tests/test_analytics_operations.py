"""
Unit Tests for EMBIP Analytics Operations (Phase 11).
Verifies deterministic calculation functions across descriptive statistics,
business metrics, growth rates, CAGRs, rankings, grouped operations, and time-series.
"""

import pytest
import pandas as pd

from app.ai.analytics.exceptions import CalculationError
from app.ai.analytics.operations import (
    op_absolute_difference,
    op_average_order_value,
    op_bottom_n,
    op_cagr,
    op_count,
    op_daily_aggregation,
    op_gross_margin_percentage,
    op_gross_profit,
    op_group_average,
    op_group_count,
    op_group_sum,
    op_growth_rate,
    op_max,
    op_mean,
    op_median,
    op_min,
    op_monthly_trend,
    op_percentage_difference,
    op_percentile,
    op_quantile,
    op_rolling_average,
    op_std,
    op_sum,
    op_top_n,
    op_total_revenue,
    op_units_sold,
)
from app.ai.analytics.registry import ANALYTICS_OPERATIONS, get_operation_function


@pytest.fixture
def sample_sales_df():
    return pd.DataFrame([
        {"id": 1, "store_name": "Store A", "total_amount": 100.0, "quantity": 2, "cost_price": 30.0, "total_price": 100.0, "transaction_date": "2025-01-15"},
        {"id": 2, "store_name": "Store A", "total_amount": 200.0, "quantity": 4, "cost_price": 25.0, "total_price": 200.0, "transaction_date": "2025-01-20"},
        {"id": 3, "store_name": "Store B", "total_amount": 300.0, "quantity": 5, "cost_price": 40.0, "total_price": 300.0, "transaction_date": "2025-02-10"},
        {"id": 4, "store_name": "Store B", "total_amount": 400.0, "quantity": 10, "cost_price": 20.0, "total_price": 400.0, "transaction_date": "2025-02-25"},
        {"id": 5, "store_name": "Store C", "total_amount": 500.0, "quantity": 1, "cost_price": 100.0, "total_price": 500.0, "transaction_date": "2025-03-05"},
    ])


def test_registry_lookup():
    assert "sum" in ANALYTICS_OPERATIONS
    assert "monthly_trend" in ANALYTICS_OPERATIONS
    fn = get_operation_function("growth_rate")
    assert fn == op_growth_rate


def test_op_count(sample_sales_df):
    res, w = op_count(sample_sales_df, metric_col="total_amount")
    assert res["value"] == 5


def test_op_sum(sample_sales_df):
    res, w = op_sum(sample_sales_df, metric_col="total_amount")
    assert res["value"] == 1500.0


def test_op_mean(sample_sales_df):
    res, w = op_mean(sample_sales_df, metric_col="total_amount")
    assert res["value"] == 300.0


def test_op_median(sample_sales_df):
    res, w = op_median(sample_sales_df, metric_col="total_amount")
    assert res["value"] == 300.0


def test_op_min_max(sample_sales_df):
    res_min, _ = op_min(sample_sales_df, metric_col="total_amount")
    res_max, _ = op_max(sample_sales_df, metric_col="total_amount")
    assert res_min["value"] == 100.0
    assert res_max["value"] == 500.0


def test_op_std(sample_sales_df):
    res, w = op_std(sample_sales_df, metric_col="total_amount")
    assert res["value"] == 158.1139


def test_op_total_revenue(sample_sales_df):
    res, w = op_total_revenue(sample_sales_df)
    assert res["value"] == 1500.0


def test_op_average_order_value(sample_sales_df):
    res, w = op_average_order_value(sample_sales_df)
    assert res["value"] == 300.0


def test_op_units_sold(sample_sales_df):
    res, w = op_units_sold(sample_sales_df)
    assert res["value"] == 22


def test_op_gross_profit(sample_sales_df):
    # item 1 profit: 100 - 2*30 = 40
    # item 2 profit: 200 - 4*25 = 100
    # item 3 profit: 300 - 5*40 = 100
    # item 4 profit: 400 - 10*20 = 200
    # item 5 profit: 500 - 1*100 = 400
    # total profit = 40 + 100 + 100 + 200 + 400 = 840
    res, w = op_gross_profit(sample_sales_df)
    assert res["value"] == 840.0


def test_op_gross_margin_percentage(sample_sales_df):
    # gross_profit = 840, revenue = 1500 -> margin % = (840 / 1500) * 100 = 56.0%
    res, w = op_gross_margin_percentage(sample_sales_df)
    assert res["value"] == 56.0


def test_op_growth_rate_and_percentage_change():
    df = pd.DataFrame([{"val": 100.0}, {"val": 150.0}])
    res, w = op_growth_rate(df, metric_col="val")
    assert res["value"] == 50.0

    # With parameters
    res_param, w = op_growth_rate(df, parameters={"val1": 200, "val2": 250})
    assert res_param["value"] == 25.0


def test_op_growth_rate_zero_denominator():
    df = pd.DataFrame([{"val": 0.0}, {"val": 100.0}])
    res, w = op_growth_rate(df, metric_col="val")
    assert res["value"] is None
    assert len(w) == 1
    assert "beginning value is zero" in w[0]


def test_op_cagr():
    # beg = 100, end = 144, years = 2 -> (144/100)^(1/2) - 1 = 1.2 - 1 = 20.0%
    res, w = op_cagr(pd.DataFrame(), parameters={"beginning_value": 100, "ending_value": 144, "years": 2})
    assert res["value"] == 20.0


def test_op_cagr_invalid_inputs():
    res, w = op_cagr(pd.DataFrame(), parameters={"beginning_value": 0, "ending_value": 100, "years": 2})
    assert res["value"] is None
    assert len(w) == 1
    assert "beginning value must be greater than zero" in w[0]


def test_op_top_n(sample_sales_df):
    res, w = op_top_n(sample_sales_df, metric_col="total_amount", parameters={"n": 2})
    assert len(res["rows"]) == 2
    assert res["rows"][0]["total_amount"] == 500.0
    assert res["rows"][1]["total_amount"] == 400.0


def test_op_bottom_n(sample_sales_df):
    res, w = op_bottom_n(sample_sales_df, metric_col="total_amount", parameters={"n": 2})
    assert len(res["rows"]) == 2
    assert res["rows"][0]["total_amount"] == 100.0
    assert res["rows"][1]["total_amount"] == 200.0


def test_op_group_sum(sample_sales_df):
    res, w = op_group_sum(sample_sales_df, metric_col="total_amount", group_by="store_name")
    assert len(res["groups"]) == 3
    # Store A sum = 300, Store B sum = 700, Store C sum = 500
    group_map = {g["group"]: g["value"] for g in res["groups"]}
    assert group_map["Store A"] == 300.0
    assert group_map["Store B"] == 700.0
    assert group_map["Store C"] == 500.0


def test_op_monthly_trend(sample_sales_df):
    res, w = op_monthly_trend(sample_sales_df, metric_col="total_amount", time_col="transaction_date")
    assert len(res["series"]) == 3
    # 2025-01: 300, 2025-02: 700, 2025-03: 500
    series_map = {s["period"]: s["value"] for s in res["series"]}
    assert series_map["2025-01"] == 300.0
    assert series_map["2025-02"] == 700.0
    assert series_map["2025-03"] == 500.0


def test_op_rolling_average(sample_sales_df):
    res, w = op_rolling_average(sample_sales_df, metric_col="total_amount", parameters={"window": 2})
    vals = res["rolling_values"]
    assert vals[0] == 100.0
    assert vals[1] == 150.0  # (100+200)/2
    assert vals[2] == 250.0  # (200+300)/2


def test_op_missing_values_and_nan_handling():
    df = pd.DataFrame([
        {"val": 10.0},
        {"val": None},
        {"val": "invalid"},
        {"val": 30.0},
    ])
    res, w = op_mean(df, metric_col="val")
    assert res["value"] == 20.0
    assert res["rows_used"] == 2
    assert len(w) == 1
