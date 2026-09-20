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
        Determines target initial nodes to execute from planner based on state['plan'].
        If SQL is required, sql_node is executed first before analytics_node.
        """
        plan = state.get("plan")
        if not plan:
            logger.warning("Router called without plan in state. Defaulting to merge_node.")
            return ["merge_node"]

        target_nodes: List[str] = []

        if plan.get("requires_sql"):
            target_nodes.append("sql_node")
        elif plan.get("requires_analytics"):
            target_nodes.append("analytics_node")

        if plan.get("requires_rag"):
            target_nodes.append("rag_node")

        if plan.get("requires_visualization") and not (plan.get("requires_sql") or plan.get("requires_analytics")):
            target_nodes.append("visualization_node")

        # Validate all computed target nodes against ALLOWED_NODES
        for node in target_nodes:
            if node not in ALLOWED_NODES:
                raise RoutingError(f"Router attempt to execute unauthorized node '{node}'.")

        if not target_nodes:
            logger.info("Plan requires no tool execution. Routing directly to merge_node.")
            return ["merge_node"]

        logger.info(f"Router calculated target initial graph nodes: {target_nodes}")
        return target_nodes

    def route_after_sql(self, state: OrchestrationState) -> str:
        """
        Determines next node after sql_node completes.
        Routes to analytics_node if plan requires analytics, else merge_node.
        """
        plan = state.get("plan") or {}
        if plan.get("requires_analytics"):
            logger.info("Routing from sql_node to analytics_node.")
            return "analytics_node"
        elif plan.get("requires_visualization"):
            logger.info("Routing from sql_node to visualization_node.")
            return "visualization_node"
        return "merge_node"


# Singleton Instance
orchestration_router = OrchestrationRouter()
