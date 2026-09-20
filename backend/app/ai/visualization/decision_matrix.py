"""
Algorithmic Chart Decision Matrix for EMBIP Visualization Agent (Phase 12).
Evaluates dataset dimensions, cardinality, data types, and temporal features
to select the most informative chart presentation type deterministically.
"""

import logging
from typing import Any, Dict, List, Optional
from app.ai.visualization.models import ChartType

logger = logging.getLogger(__name__)

TIME_COLUMN_KEYWORDS = {"date", "time", "month", "year", "quarter", "day", "period", "transaction_date", "sale_date", "created_at"}


class ChartDecisionMatrix:
    """Evaluates data structure and recommends optimal Recharts chart type."""

    def select_chart_type(
        self,
        rows: List[Dict[str, Any]],
        columns: List[str],
        analytics_result: Optional[Dict[str, Any]] = None,
        preferred_type: Optional[ChartType] = None,
    ) -> ChartType:
        """
        Calculates optimal ChartType using deterministic decision rules.
        """
        # 1. Override with preferred type if requested
        if preferred_type:
            logger.info(f"Using explicitly requested chart type: '{preferred_type.value}'")
            return preferred_type

        # 2. Analytics Result Evaluation
        if analytics_result and analytics_result.get("status") == "success":
            op = (analytics_result.get("operation") or "").lower()
            scalar_val = analytics_result.get("value")
            groups = analytics_result.get("groups")
            series = analytics_result.get("series")

            # Scalar Metric (Single KPI)
            if scalar_val is not None and not groups and not series:
                return ChartType.METRIC_CARD

            # Time Series Aggregation
            if series and isinstance(series, list):
                if len(series) <= 12:
                    return ChartType.AREA_CHART
                return ChartType.LINE_CHART

            # Grouped Aggregation
            if groups and isinstance(groups, list):
                if len(groups) <= 5:
                    return ChartType.PIE_CHART
                elif len(groups) <= 20:
                    return ChartType.HORIZONTAL_BAR_CHART
                return ChartType.BAR_CHART

            if op in ["top_n", "bottom_n", "rank_by_metric"]:
                return ChartType.HORIZONTAL_BAR_CHART

        # 3. Tabular SQL Dataset Evaluation
        if not rows:
            return ChartType.METRIC_CARD

        if len(rows) == 1:
            return ChartType.METRIC_CARD

        col_count = len(columns) if columns else (len(rows[0]) if rows else 0)

        # Detect Column Data Types
        first_row = rows[0]
        time_cols = [c for c in columns if c.lower() in TIME_COLUMN_KEYWORDS]
        num_cols = [k for k, v in first_row.items() if isinstance(v, (int, float)) and not isinstance(v, bool) and k.lower() != "id"]
        str_cols = [k for k, v in first_row.items() if isinstance(v, str) and k.lower() not in TIME_COLUMN_KEYWORDS and k.lower() not in ["id", "uuid"]]

        # Temporal Datasets -> Line or Area Chart
        if time_cols and num_cols:
            if len(rows) <= 15:
                return ChartType.AREA_CHART
            return ChartType.LINE_CHART

        # Multiple Numeric Series -> Grouped Bar Chart
        if len(num_cols) >= 2 and str_cols:
            return ChartType.GROUPED_BAR_CHART

        # Categorical Aggregations -> Bar or Pie or Horizontal Bar
        if len(num_cols) == 1 and str_cols:
            cardinality = len(rows)
            if cardinality <= 5:
                return ChartType.BAR_CHART
            elif cardinality <= 15:
                return ChartType.HORIZONTAL_BAR_CHART
            return ChartType.BAR_CHART

        # Fallback default
        return ChartType.BAR_CHART


# Singleton Instance
chart_decision_matrix = ChartDecisionMatrix()
