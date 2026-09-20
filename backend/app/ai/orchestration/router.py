"""
Routing Logic & Capability Validation for LangGraph Orchestration (Phase 10).
Converts Planner Agent output into safe graph routing decisions.
"""

import logging
from typing import List

from app.ai.orchestration.exceptions import RoutingError
from app.ai.orchestration.state import OrchestrationState

logger = logging.getLogger(__name__)

# Strictly permitted node names in the LangGraph graph execution workflow
ALLOWED_NODES = {
    "sql_node",
    "rag_node",
    "analytics_node",
    "visualization_node",
    "merge_node",
}


class OrchestrationRouter:
    """
    Validates planner intent and calculates safe graph branch routes.
    """

    def route(self, state: OrchestrationState) -> List[str]:
        """
        Determines target nodes to execute based on state['plan'].
        Returns list of target node strings for LangGraph conditional branching.
        """
        plan = state.get("plan")
        if not plan:
            logger.warning("Router called without plan in state. Defaulting to merge_node.")
            return ["merge_node"]

        target_nodes: List[str] = []

        if plan.get("requires_sql"):
            target_nodes.append("sql_node")
        if plan.get("requires_rag"):
            target_nodes.append("rag_node")
        if plan.get("requires_analytics"):
            target_nodes.append("analytics_node")
        if plan.get("requires_visualization"):
            target_nodes.append("visualization_node")

        # Validate all computed target nodes against ALLOWED_NODES
        for node in target_nodes:
            if node not in ALLOWED_NODES:
                raise RoutingError(f"Router attempt to execute unauthorized node '{node}'.")

        if not target_nodes:
            logger.info("Plan requires no tool execution. Routing directly to merge_node.")
            return ["merge_node"]

        logger.info(f"Router calculated target graph nodes: {target_nodes}")
        return target_nodes


# Singleton Instance
orchestration_router = OrchestrationRouter()
