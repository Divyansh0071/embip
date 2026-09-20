"""
Unit Tests for EMBIP Visualization Server-Side Validator (Phase 12).
Verifies data key validation, spec title presence, and row count bounds.
"""

import pytest

from app.ai.visualization.exceptions import SpecValidationError
from app.ai.visualization.models import AxisConfig, ChartType, RechartsSpec, SeriesConfig
from app.ai.visualization.validators import MAX_CHART_POINTS, visualization_validator


def test_validator_accepts_valid_spec():
    spec = RechartsSpec(
        chartType=ChartType.BAR_CHART,
        title="Valid Bar Chart",
        data=[{"category": "A", "val": 10}, {"category": "B", "val": 20}],
        xAxis=AxisConfig(dataKey="category"),
        yAxis=AxisConfig(dataKey="val"),
        series=[SeriesConfig(dataKey="val", name="Value", color="#06b6d4")],
    )
    visualization_validator.validate_spec(spec)  # Should not raise exception


def test_validator_missing_title_rejected():
    spec = RechartsSpec(
        chartType=ChartType.BAR_CHART,
        title="",
        data=[{"cat": "A", "val": 10}],
        series=[SeriesConfig(dataKey="val", name="Value", color="#06b6d4")],
    )
    with pytest.raises(SpecValidationError) as excinfo:
        visualization_validator.validate_spec(spec)
    assert "must include a title" in str(excinfo.value)


def test_validator_missing_xaxis_datakey_rejected():
    spec = RechartsSpec(
        chartType=ChartType.BAR_CHART,
        title="Invalid X-Key Chart",
        data=[{"category": "A", "val": 10}],
        xAxis=AxisConfig(dataKey="non_existent_key"),
        series=[SeriesConfig(dataKey="val", name="Value", color="#06b6d4")],
    )
    with pytest.raises(SpecValidationError) as excinfo:
        visualization_validator.validate_spec(spec)
    assert "X-Axis dataKey 'non_existent_key' is missing" in str(excinfo.value)


def test_validator_missing_series_datakey_rejected():
    spec = RechartsSpec(
        chartType=ChartType.BAR_CHART,
        title="Invalid Series Key Chart",
        data=[{"category": "A", "val": 10}],
        xAxis=AxisConfig(dataKey="category"),
        series=[SeriesConfig(dataKey="missing_val_key", name="Value", color="#06b6d4")],
    )
    with pytest.raises(SpecValidationError) as excinfo:
        visualization_validator.validate_spec(spec)
    assert "Series dataKey 'missing_val_key' is missing" in str(excinfo.value)


def test_validator_oversized_dataset_rejected():
    oversized_data = [{"cat": f"Cat {i}", "val": i} for i in range(MAX_CHART_POINTS + 1)]
    spec = RechartsSpec(
        chartType=ChartType.BAR_CHART,
        title="Oversized Chart",
        data=oversized_data,
        xAxis=AxisConfig(dataKey="cat"),
        series=[SeriesConfig(dataKey="val", name="Value", color="#06b6d4")],
    )
    with pytest.raises(SpecValidationError) as excinfo:
        visualization_validator.validate_spec(spec)
    assert "exceeds maximum allowed" in str(excinfo.value)
