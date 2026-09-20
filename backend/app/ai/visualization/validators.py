"""
Recharts Spec Server-Side Validator for EMBIP (Phase 12).
Ensures generated Recharts JSON specifications adhere strictly to schema rules
and data key presence constraints before returning to frontend.
"""

from typing import List
from app.ai.visualization.exceptions import SpecValidationError
from app.ai.visualization.models import RechartsSpec

MAX_CHART_POINTS = 50


class VisualizationValidator:
    """Server-side validation engine for RechartsSpec objects."""

    def validate_spec(self, spec: RechartsSpec) -> None:
        """
        Validates RechartsSpec object. Raises SpecValidationError on invalid specs.
        """
        if not spec.title:
            raise SpecValidationError("Recharts spec must include a title.")

        if not spec.data and spec.chartType.value != "metric_card":
            raise SpecValidationError(f"Chart type '{spec.chartType.value}' requires non-empty data rows.")

        if len(spec.data) > MAX_CHART_POINTS:
            raise SpecValidationError(
                f"Chart dataset size ({len(spec.data)} points) exceeds maximum allowed "
                f"visualization limit ({MAX_CHART_POINTS} points)."
            )

        if spec.chartType.value == "metric_card":
            return  # Metric card does not require X/Y axis data keys

        # Verify X-Axis dataKey exists in data rows
        if spec.xAxis:
            x_key = spec.xAxis.dataKey
            for idx, row in enumerate(spec.data):
                if x_key not in row:
                    raise SpecValidationError(
                        f"X-Axis dataKey '{x_key}' is missing in data row index {idx}: {list(row.keys())}"
                    )

        # Verify Series dataKeys exist in data rows
        if not spec.series:
            raise SpecValidationError("Recharts spec must contain at least one series config.")

        for series in spec.series:
            s_key = series.dataKey
            for idx, row in enumerate(spec.data):
                if s_key not in row:
                    raise SpecValidationError(
                        f"Series dataKey '{s_key}' is missing in data row index {idx}: {list(row.keys())}"
                    )


# Singleton Instance
visualization_validator = VisualizationValidator()
