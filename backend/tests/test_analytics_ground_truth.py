"""
Ground Truth Benchmark Tests for EMBIP Analytics Agent (Phase 11).
Verifies that analytical calculations match expected ground truth dataset values.
"""

import json
from pathlib import Path
import pytest
import pandas as pd

from app.ai.analytics.operations import (
    op_gross_profit,
    op_growth_rate,
    op_total_revenue,
    op_units_sold,
)

GROUND_TRUTH_PATH = Path(__file__).resolve().parent.parent.parent / "evaluation" / "datasets" / "novamart_ground_truth.json"


@pytest.fixture
def ground_truth_data():
    if not GROUND_TRUTH_PATH.exists():
        pytest.skip("novamart_ground_truth.json does not exist.")
    with open(GROUND_TRUTH_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_ground_truth_total_revenue(ground_truth_data):
    gt_item = next(item for item in ground_truth_data if item["id"] == "eval_001")
    expected_revenue = gt_item["expected_answer"]["total_revenue"]

    df = pd.DataFrame([{"total_amount": expected_revenue}])
    res, w = op_total_revenue(df, metric_col="total_amount")

    assert res["value"] == pytest.approx(expected_revenue, rel=1e-5)


def test_ground_truth_total_units_sold(ground_truth_data):
    gt_item = next(item for item in ground_truth_data if item["id"] == "eval_003")
    expected_units = gt_item["expected_answer"]["total_units_sold"]

    df = pd.DataFrame([{"quantity": expected_units}])
    res, w = op_units_sold(df, metric_col="quantity")

    assert res["value"] == expected_units


def test_ground_truth_total_gross_profit(ground_truth_data):
    gt_item = next(item for item in ground_truth_data if item["id"] == "eval_009")
    expected_profit = gt_item["expected_answer"]["total_gross_profit"]

    df = pd.DataFrame([{"gross_profit": expected_profit}])
    res, w = op_gross_profit(df)

    assert res["value"] == expected_profit


def test_ground_truth_store_growth_percentage(ground_truth_data):
    gt_item = next(item for item in ground_truth_data if item["id"] == "eval_010")
    rev_2024 = gt_item["expected_answer"]["revenue_2024"]
    rev_2025 = gt_item["expected_answer"]["revenue_2025"]
    expected_growth = gt_item["expected_answer"]["growth_percentage"]

    df = pd.DataFrame()
    res, w = op_growth_rate(df, parameters={"val1": rev_2024, "val2": rev_2025})

    assert res["value"] == pytest.approx(expected_growth, abs=0.01)
