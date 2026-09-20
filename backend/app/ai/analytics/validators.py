"""
Input Validation Engine for EMBIP Analytics Agent (Phase 11).
Prevents unsafe inputs, bounded memory overflow, and missing column errors.
"""

from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

from app.ai.analytics.exceptions import InsufficientDataError, ValidationError
from app.ai.analytics.models import AnalyticsInput
from app.ai.analytics.registry import ANALYTICS_OPERATIONS

ANALYTICS_MAX_INPUT_ROWS = 10000
ANALYTICS_MAX_TOP_N = 100


class AnalyticsValidator:
    """Validates input datasets and parameters prior to computation."""

    def validate_and_prepare(self, input_data: AnalyticsInput) -> Tuple[pd.DataFrame, str]:
        """
        Validates AnalyticsInput, enforces limits, checks column existence,
        and constructs a clean Pandas DataFrame.
        """
        if not input_data.rows:
            raise InsufficientDataError("Input dataset is empty (0 rows). Cannot perform analytical calculation.")

        if len(input_data.rows) > ANALYTICS_MAX_INPUT_ROWS:
            raise ValidationError(
                f"Input dataset size ({len(input_data.rows)} rows) exceeds maximum allowed "
                f"analytics limit ({ANALYTICS_MAX_INPUT_ROWS} rows)."
            )

        op_name = (input_data.operation or "").strip().lower()
        if op_name not in ANALYTICS_OPERATIONS:
            raise ValidationError(
                f"Invalid or unauthorized analytics operation '{input_data.operation}'. "
                f"Must be one of: {sorted(list(ANALYTICS_OPERATIONS.keys()))}"
            )

        # Build DataFrame
        df = pd.DataFrame(input_data.rows)
        
        # Verify specified columns exist
        if input_data.metric_column and input_data.metric_column not in df.columns:
            # Check if column case-mismatched
            matches = [c for c in df.columns if c.lower() == input_data.metric_column.lower()]
            if matches:
                input_data.metric_column = matches[0]
            else:
                raise ValidationError(f"Specified metric_column '{input_data.metric_column}' not found in dataset columns: {list(df.columns)}")

        if input_data.group_by and input_data.group_by not in df.columns:
            matches = [c for c in df.columns if c.lower() == input_data.group_by.lower()]
            if matches:
                input_data.group_by = matches[0]
            else:
                raise ValidationError(f"Specified group_by column '{input_data.group_by}' not found in dataset columns: {list(df.columns)}")

        if input_data.time_column and input_data.time_column not in df.columns:
            matches = [c for c in df.columns if c.lower() == input_data.time_column.lower()]
            if matches:
                input_data.time_column = matches[0]
            else:
                raise ValidationError(f"Specified time_column '{input_data.time_column}' not found in dataset columns: {list(df.columns)}")

        # Enforce parameter bounds (e.g. top_n limit)
        if "n" in input_data.parameters:
            try:
                n = int(input_data.parameters["n"])
                input_data.parameters["n"] = max(1, min(n, ANALYTICS_MAX_TOP_N))
            except (ValueError, TypeError):
                input_data.parameters["n"] = 5

        return df, op_name


# Singleton Instance
analytics_validator = AnalyticsValidator()
