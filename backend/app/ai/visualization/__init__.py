"""
EMBIP Visualization Package (Phase 12).
Exposes VisualizationService, VisualizationAgent, ChartDecisionMatrix, models, and validator.
"""

from app.ai.visualization.agent import VisualizationAgent, visualization_agent
from app.ai.visualization.decision_matrix import ChartDecisionMatrix, chart_decision_matrix
from app.ai.visualization.exceptions import (
    ChartTypeError,
    DataIncompatibilityError,
    SpecValidationError,
    VisualizationError,
)
from app.ai.visualization.generator import RechartsSpecGenerator, recharts_spec_generator
from app.ai.visualization.models import (
    AxisConfig,
    ChartType,
    RechartsSpec,
    SeriesConfig,
    VisualizationMetadata,
    VisualizationRequest,
    VisualizationResult,
)
from app.ai.visualization.service import VisualizationService, visualization_service
from app.ai.visualization.validators import VisualizationValidator, visualization_validator

__all__ = [
    "VisualizationService",
    "visualization_service",
    "VisualizationAgent",
    "visualization_agent",
    "ChartDecisionMatrix",
    "chart_decision_matrix",
    "RechartsSpecGenerator",
    "recharts_spec_generator",
    "VisualizationValidator",
    "visualization_validator",
    "ChartType",
    "RechartsSpec",
    "AxisConfig",
    "SeriesConfig",
    "VisualizationRequest",
    "VisualizationResult",
    "VisualizationMetadata",
    "VisualizationError",
    "ChartTypeError",
    "SpecValidationError",
    "DataIncompatibilityError",
]
