"""
Custom Exceptions for EMBIP Visualization Agent (Phase 12).
"""


class VisualizationError(Exception):
    """Base exception for all visualization layer errors."""

    pass


class ChartTypeError(VisualizationError):
    """Raised when an invalid or unsupported chart type is specified."""

    pass


class SpecValidationError(VisualizationError):
    """Raised when a generated Recharts JSON spec fails validation."""

    pass


class DataIncompatibilityError(VisualizationError):
    """Raised when dataset structure cannot be formatted into a valid chart spec."""

    pass
