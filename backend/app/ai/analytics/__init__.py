"""
EMBIP Analytics Package (Phase 11).
Exposes AnalyticsService, AnalyticsAgent, models, and operation registry.
"""

from app.ai.analytics.agent import AnalyticsAgent, analytics_agent
from app.ai.analytics.exceptions import (
    AnalyticsError,
    CalculationError,
    InsufficientDataError,
    InvalidOperationError,
    ValidationError,
)
from app.ai.analytics.models import (
    AnalyticsGroupResult,
    AnalyticsInput,
    AnalyticsProvenance,
    AnalyticsResult,
    AnalyticsSeriesPoint,
    AnalyticsSummary,
)
from app.ai.analytics.registry import ANALYTICS_OPERATIONS, get_operation_function
from app.ai.analytics.service import AnalyticsService, analytics_service

__all__ = [
    "AnalyticsService",
    "analytics_service",
    "AnalyticsAgent",
    "analytics_agent",
    "AnalyticsInput",
    "AnalyticsResult",
    "AnalyticsSummary",
    "AnalyticsProvenance",
    "AnalyticsGroupResult",
    "AnalyticsSeriesPoint",
    "ANALYTICS_OPERATIONS",
    "get_operation_function",
    "AnalyticsError",
    "ValidationError",
    "InvalidOperationError",
    "CalculationError",
    "InsufficientDataError",
]
