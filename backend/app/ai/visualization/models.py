"""
Pydantic Schemas for EMBIP Visualization Agent (Phase 12).
Defines chart types, Recharts JSON specification contracts, and result models.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ChartType(str, Enum):
    """Supported Recharts visual presentation types."""

    BAR_CHART = "bar_chart"
    HORIZONTAL_BAR_CHART = "horizontal_bar_chart"
    LINE_CHART = "line_chart"
    AREA_CHART = "area_chart"
    PIE_CHART = "pie_chart"
    GROUPED_BAR_CHART = "grouped_bar_chart"
    METRIC_CARD = "metric_card"
    SCATTER_PLOT = "scatter_plot"


class AxisConfig(BaseModel):
    """Axis configuration schema for Recharts."""

    dataKey: str = Field(..., description="Data key mapping to dataset property.")
    label: Optional[str] = Field(None, description="Human-readable axis title.")
    type: str = Field(default="category", description="'category' or 'number'")
    tickFormat: Optional[str] = Field(None, description="'currency', 'percentage', 'number', 'date'")


class SeriesConfig(BaseModel):
    """Data series configuration for Recharts charts."""

    dataKey: str = Field(..., description="Value property key in data rows.")
    name: str = Field(..., description="Display label for series legend.")
    color: str = Field(..., description="Hex or HSL color code.")
    type: Optional[str] = Field(None, description="Series mark type e.g. 'monotone', 'linear'")


class RechartsSpec(BaseModel):
    """Full Recharts JSON Specification payload consumed by frontend rendering engine."""

    chartType: ChartType = Field(..., description="Target Recharts chart component type.")
    title: str = Field(..., description="Executive chart title.")
    subtitle: Optional[str] = Field(None, description="Subheading context or date range description.")
    data: List[Dict[str, Any]] = Field(default_factory=list, description="Structured row array for Recharts component.")
    xAxis: Optional[AxisConfig] = Field(None, description="X-axis configuration object.")
    yAxis: Optional[AxisConfig] = Field(None, description="Y-axis configuration object.")
    series: List[SeriesConfig] = Field(default_factory=list, description="Configured data series array.")
    colors: List[str] = Field(default_factory=list, description="Theme color palette array.")
    showLegend: bool = Field(default=True, description="Whether to display series legend.")
    showTooltip: bool = Field(default=True, description="Whether to display hover tooltip.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution and source metadata.")


class VisualizationRequest(BaseModel):
    """Input request parameters for Visualization Service."""

    question: str = Field(..., description="User natural language question.")
    sql_result: Optional[Dict[str, Any]] = Field(None, description="SQL Agent output dict.")
    analytics_result: Optional[Dict[str, Any]] = Field(None, description="Analytics Agent output dict.")
    preferred_chart_type: Optional[ChartType] = Field(None, description="Optional forced chart type preference.")


class VisualizationResult(BaseModel):
    """Output result returned by Visualization Service."""

    status: str = Field(..., description="'success', 'warning', or 'error'")
    spec: Optional[RechartsSpec] = Field(None, description="Validated Recharts JSON spec object.")
    explanation: Optional[str] = Field(None, description="1-sentence visual summary or highlight note.")
    error: Optional[str] = Field(None, description="Error message string if status is 'error'.")


class VisualizationMetadata(BaseModel):
    """Structured output format for LLM chart metadata generation."""

    title: str = Field(..., description="Executive chart title.")
    subtitle: str = Field(..., description="Concise chart subtitle.")
    insight: str = Field(..., description="Key visual takeaway or highlight.")
