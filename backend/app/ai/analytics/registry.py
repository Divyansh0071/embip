"""
Explicit Operation Registry for EMBIP Analytics Agent (Phase 11).
Strictly prevents dynamic/arbitrary code execution by mapping operation keys
to predefined pure Python functions.
"""

from typing import Any, Callable, Dict, List, Tuple
import pandas as pd

from app.ai.analytics.exceptions import InvalidOperationError
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
    op_quarterly_aggregation,
    op_quantile,
    op_rank_by_metric,
    op_rolling_average,
    op_std,
    op_sum,
    op_top_n,
    op_total_revenue,
    op_units_sold,
    op_weekly_aggregation,
)

# Operational Function Signature
OpFunc = Callable[..., Tuple[Dict[str, Any], List[str]]]

# Strictly Controlled Operational Map
ANALYTICS_OPERATIONS: Dict[str, OpFunc] = {
    # 1. Descriptive Statistics
    "count": op_count,
    "sum": op_sum,
    "mean": op_mean,
    "median": op_median,
    "min": op_min,
    "max": op_max,
    "std": op_std,
    
    # 2. Business Metrics
    "total_revenue": op_total_revenue,
    "average_order_value": op_average_order_value,
    "units_sold": op_units_sold,
    "gross_profit": op_gross_profit,
    "gross_margin_percentage": op_gross_margin_percentage,
    
    # 3. Comparisons & Growth
    "absolute_difference": op_absolute_difference,
    "percentage_difference": op_percentage_difference,
    "growth_rate": op_growth_rate,
    "cagr": op_cagr,
    
    # 4. Ranking
    "top_n": op_top_n,
    "bottom_n": op_bottom_n,
    "rank_by_metric": op_rank_by_metric,
    
    # 5. Grouped Aggregation
    "group_sum": op_group_sum,
    "group_average": op_group_average,
    "group_count": op_group_count,
    
    # 6. Time-Series
    "daily_aggregation": op_daily_aggregation,
    "weekly_aggregation": op_weekly_aggregation,
    "monthly_trend": op_monthly_trend,
    "quarterly_aggregation": op_quarterly_aggregation,
    "rolling_average": op_rolling_average,
    
    # 7. Distribution
    "percentile": op_percentile,
    "quantile": op_quantile,
}


def get_operation_function(operation_name: str) -> OpFunc:
    """
    Retrieves the registered operation function.
    Raises InvalidOperationError if operation_name is not in ANALYTICS_OPERATIONS.
    """
    op_key = (operation_name or "").strip().lower()
    if op_key not in ANALYTICS_OPERATIONS:
        raise InvalidOperationError(
            f"Operation '{operation_name}' is not permitted. "
            f"Allowed operations: {sorted(list(ANALYTICS_OPERATIONS.keys()))}"
        )
    return ANALYTICS_OPERATIONS[op_key]
