"""
TypedDict Graph State for LangGraph Orchestration Engine (Phase 10).
"""

from typing import Any, Dict, List, Optional, TypedDict


class OrchestrationState(TypedDict, total=False):
    """
    Shared graph state object passed through LangGraph nodes.
    Maintains strongly typed context across planner, tool execution, and merge steps.
    """

    request_id: str
    user_id: str
    workspace_id: str
    question: str
    plan: Optional[Dict[str, Any]]
    sql_result: Optional[Dict[str, Any]]
    rag_result: Optional[Dict[str, Any]]
    analytics_result: Optional[Dict[str, Any]]
    visualization_result: Optional[Dict[str, Any]]
    validation_result: Optional[Dict[str, Any]]
    retry_count: int
    merged_results: Optional[Dict[str, Any]]
    errors: List[str]
    status: str
