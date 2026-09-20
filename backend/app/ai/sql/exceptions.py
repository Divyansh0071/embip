"""
Custom Exception Hierarchy for SQL Agent & Execution Engine (Phase 9).
"""

from typing import Any, Dict, List, Optional


class SQLAgentError(Exception):
    """Base exception for all SQL Agent errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class SQLValidationError(SQLAgentError):
    """Raised when generated SQL fails AST validation or security rules."""

    def __init__(self, message: str, invalid_reasons: Optional[List[str]] = None):
        reasons = invalid_reasons or [message]
        super().__init__(message, {"invalid_reasons": reasons})
        self.invalid_reasons = reasons


class SQLSecurityError(SQLValidationError):
    """Raised when generated SQL attempts dangerous or prohibited operations."""

    pass


class SQLExecutionTimeoutError(SQLAgentError):
    """Raised when query execution exceeds statement_timeout limits."""

    pass


class SQLExecutionError(SQLAgentError):
    """Raised when PostgreSQL database query execution fails."""

    pass
