"""
Custom Exception Classes for EMBIP Report Generator Agent (Phase 14).
"""

class ReportError(Exception):
    """Base exception for all report generation and export errors."""
    pass


class ReportValidationError(ReportError):
    """Raised when a generated report fails factual consistency or citation validation."""
    pass


class ReportExportError(ReportError):
    """Raised when formatting or exporting a report to PDF/Markdown fails."""
    pass
