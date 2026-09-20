"""
Custom Exceptions for EMBIP Analytics Agent (Phase 11).
"""


class AnalyticsError(Exception):
    """Base exception for all analytics errors."""

    pass


class ValidationError(AnalyticsError):
    """Raised when input dataset or parameters fail validation."""

    pass


class InvalidOperationError(AnalyticsError):
    """Raised when an operation requested is not present in the allowed registry."""

    pass


class CalculationError(AnalyticsError):
    """Raised when a numerical calculation encounters an unrecoverable mathematical error."""

    pass


class InsufficientDataError(AnalyticsError):
    """Raised when a dataset lacks minimum required rows or columns for analysis."""

    pass
