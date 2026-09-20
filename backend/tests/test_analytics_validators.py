"""
Unit Tests for EMBIP Analytics Validators (Phase 11).
Verifies input contract validation, boundary enforcement, column matching,
and unauthorized operation rejection.
"""

import pytest

from app.ai.analytics.exceptions import InsufficientDataError, ValidationError
from app.ai.analytics.models import AnalyticsInput
from app.ai.analytics.validators import ANALYTICS_MAX_INPUT_ROWS, analytics_validator


def test_validator_empty_dataset_rejected():
    inp = AnalyticsInput(columns=["val"], rows=[], operation="sum")
    with pytest.raises(InsufficientDataError):
        analytics_validator.validate_and_prepare(inp)


def test_validator_oversized_dataset_rejected():
    oversized_rows = [{"val": i} for i in range(ANALYTICS_MAX_INPUT_ROWS + 1)]
    inp = AnalyticsInput(columns=["val"], rows=oversized_rows, operation="sum")
    with pytest.raises(ValidationError) as excinfo:
        analytics_validator.validate_and_prepare(inp)
    assert "exceeds maximum allowed" in str(excinfo.value)


def test_validator_unauthorized_operation_rejected():
    inp = AnalyticsInput(
        columns=["val"],
        rows=[{"val": 10}],
        operation="arbitrary_python_eval",
    )
    with pytest.raises(ValidationError) as excinfo:
        analytics_validator.validate_and_prepare(inp)
    assert "Invalid or unauthorized analytics operation" in str(excinfo.value)


def test_validator_missing_metric_column_rejected():
    inp = AnalyticsInput(
        columns=["val1"],
        rows=[{"val1": 10}],
        operation="sum",
        metric_column="non_existent_column",
    )
    with pytest.raises(ValidationError) as excinfo:
        analytics_validator.validate_and_prepare(inp)
    assert "Specified metric_column 'non_existent_column' not found" in str(excinfo.value)


def test_validator_case_insensitive_column_matching():
    inp = AnalyticsInput(
        columns=["TOTAL_AMOUNT"],
        rows=[{"TOTAL_AMOUNT": 100}],
        operation="sum",
        metric_column="total_amount",
    )
    df, op_name = analytics_validator.validate_and_prepare(inp)
    assert op_name == "sum"
    assert inp.metric_column == "TOTAL_AMOUNT"


def test_validator_top_n_parameter_bounding():
    inp = AnalyticsInput(
        columns=["val"],
        rows=[{"val": i} for i in range(5)],
        operation="top_n",
        metric_column="val",
        parameters={"n": 5000},
    )
    df, op_name = analytics_validator.validate_and_prepare(inp)
    assert inp.parameters["n"] == 100
