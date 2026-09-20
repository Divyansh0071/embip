"""
Custom Exception Hierarchy for Multi-Agent Orchestration (Phase 10).
"""

from typing import Any, Dict, Optional


class OrchestrationError(Exception):
    """Base exception for all Orchestration errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class PlannerError(OrchestrationError):
    """Raised when Planner Agent fails to classify intent or output valid plan."""

    pass


class RoutingError(OrchestrationError):
    """Raised when invalid or unpermitted capability route is requested."""

    pass


class NodeExecutionError(OrchestrationError):
    """Raised when individual graph node execution fails."""

    def __init__(self, node_name: str, message: str):
        super().__init__(f"Graph Node '{node_name}' failed: {message}", {"node_name": node_name})
        self.node_name = node_name
