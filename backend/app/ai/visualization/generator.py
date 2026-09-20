"""
Recharts JSON Specification Generator for EMBIP (Phase 12).
Formats raw SQL rows and Analytics outputs into structured Recharts spec payloads.
"""

import logging
from typing import Any, Dict, List, Optional
from app.ai.visualization.models import (
    AxisConfig,
    ChartType,
    RechartsSpec,
    SeriesConfig,
)

logger = logging.getLogger(__name__)

THEME_COLORS = [
    "#06b6d4",  # Cyan-500
    "#6366f1",  # Indigo-500
    "#a855f7",  # Purple-500
    "#10b981",  # Emerald-500
    "#f59e0b",  # Amber-500
    "#ec4899",  # Pink-500
    "#3b82f6",  # Blue-500
    "#8b5cf6",  # Violet-500
]


class RechartsSpecGenerator:
    """Generates valid RechartsSpec JSON payloads from structured data."""

    def generate_spec(
        self,
        chart_type: ChartType,
        rows: List[Dict[str, Any]],
        columns: List[str],
        title: str = "Data Visualization",
        subtitle: Optional[str] = None,
        analytics_result: Optional[Dict[str, Any]] = None,
    ) -> RechartsSpec:
        """
        Constructs RechartsSpec object matching target chartType.
        """
        # 1. Handle Metric Card (Scalar Value)
        if chart_type == ChartType.METRIC_CARD:
            value = None
            metric_name = "Metric"
            if analytics_result and analytics_result.get("value") is not None:
                value = analytics_result["value"]
                metric_name = analytics_result.get("metric") or "Calculated Metric"
            elif rows and len(rows) > 0:
                first_row = rows[0]
                num_keys = [k for k, v in first_row.items() if isinstance(v, (int, float)) and not isinstance(v, bool)]
                if num_keys:
                    metric_name = num_keys[0]
                    value = first_row[metric_name]
                else:
                    metric_name = list(first_row.keys())[0]
                    value = first_row[metric_name]

            return RechartsSpec(
                chartType=ChartType.METRIC_CARD,
                title=title,
                subtitle=subtitle or f"Metric: {metric_name}",
                data=[{"metric": metric_name, "value": value}],
                series=[SeriesConfig(dataKey="value", name=metric_name, color=THEME_COLORS[0])],
                colors=THEME_COLORS,
                metadata={"metric_name": metric_name, "value": value},
            )

        # 2. Handle Analytics Outputs (groups / series)
        data_rows: List[Dict[str, Any]] = []
        x_key = "category"
        series_configs: List[SeriesConfig] = []
        tick_format = "number"

        if analytics_result and analytics_result.get("status") in ["success", "warning"]:
            if analytics_result.get("series"):
                # Time-series analytics output
                data_rows = analytics_result["series"]
                x_key = "period"
                val_key = "value"
                series_configs.append(
                    SeriesConfig(dataKey=val_key, name=analytics_result.get("metric") or "Metric", color=THEME_COLORS[0], type="monotone")
                )
            elif analytics_result.get("groups"):
                # Grouped analytics output
                data_rows = analytics_result["groups"]
                x_key = "group"
                val_key = "value"
                series_configs.append(
                    SeriesConfig(dataKey=val_key, name=analytics_result.get("metric") or "Metric", color=THEME_COLORS[0])
                )

        # 3. Fallback to SQL Rows if Analytics didn't populate data_rows
        if not data_rows and rows:
            data_rows = rows[:50]  # Limit to 50 rows max
            first_row = data_rows[0]

            # Detect X and Series data keys
            time_keys = [k for k in first_row.keys() if k.lower() in ["transaction_date", "sale_date", "date", "created_at", "month", "period", "year"]]
            str_keys = [k for k, v in first_row.items() if isinstance(v, str) and k not in time_keys and k.lower() not in ["id", "uuid"]]
            num_keys = [k for k, v in first_row.items() if isinstance(v, (int, float)) and not isinstance(v, bool) and k.lower() != "id"]

            if time_keys:
                x_key = time_keys[0]
            elif str_keys:
                x_key = str_keys[0]
            elif columns:
                x_key = columns[0]

            # Build Series Configs for numeric columns
            if num_keys:
                for idx, nk in enumerate(num_keys[:4]):  # Max 4 series
                    color = THEME_COLORS[idx % len(THEME_COLORS)]
                    series_configs.append(SeriesConfig(dataKey=nk, name=nk.replace("_", " ").title(), color=color))
            else:
                # Default fallback series if no numeric columns found
                first_non_x = next((k for k in first_row.keys() if k != x_key), columns[-1] if columns else "value")
                series_configs.append(SeriesConfig(dataKey=first_non_x, name=first_non_x.replace("_", " ").title(), color=THEME_COLORS[0]))

        # Detect Y-axis tick format based on metric names
        first_series_key = series_configs[0].dataKey if series_configs else "value"
        if any(w in first_series_key.lower() for w in ["revenue", "amount", "price", "profit", "spent", "cost", "sales"]):
            tick_format = "currency"
        elif any(w in first_series_key.lower() for w in ["margin", "rate", "percent", "pct", "growth"]):
            tick_format = "percentage"

        x_axis = AxisConfig(dataKey=x_key, label=x_key.replace("_", " ").title(), type="category")
        y_axis = AxisConfig(dataKey=first_series_key, label="Value", type="number", tickFormat=tick_format)

        return RechartsSpec(
            chartType=chart_type,
            title=title,
            subtitle=subtitle or f"Visualizing {first_series_key.replace('_', ' ')} across {x_key.replace('_', ' ')}",
            data=data_rows,
            xAxis=x_axis,
            yAxis=y_axis,
            series=series_configs,
            colors=THEME_COLORS,
            showLegend=len(series_configs) > 1 or chart_type == ChartType.PIE_CHART,
            showTooltip=True,
            metadata={
                "row_count": len(data_rows),
                "data_keys": [s.dataKey for s in series_configs],
                "x_key": x_key,
            },
        )


# Singleton Instance
recharts_spec_generator = RechartsSpecGenerator()
