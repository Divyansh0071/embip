"""
LangGraph Multi-Agent Workflow Execution Graph (Phase 10).
Defines StateGraph structure, dynamic capability routing, and node execution paths.
"""

import logging
from langgraph.graph import END, START, StateGraph

from app.ai.orchestration.nodes import (
    analytics_node,
    merge_node,
    planner_node,
    rag_node,
    sql_node,
    validation_node,
    visualization_node,
)
from app.ai.orchestration.router import orchestration_router
from app.ai.orchestration.state import OrchestrationState

logger = logging.getLogger(__name__)


def build_orchestration_graph():
    """
    Constructs and compiles the multi-agent LangGraph workflow.
    """
    workflow = StateGraph(OrchestrationState)

    # 1. Register Graph Nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("sql_node", sql_node)
    workflow.add_node("rag_node", rag_node)
    workflow.add_node("analytics_node", analytics_node)
    workflow.add_node("visualization_node", visualization_node)
    workflow.add_node("validation_node", validation_node)
    workflow.add_node("merge_node", merge_node)

    # 2. Define Entry Edge
    workflow.add_edge(START, "planner")

    # 3. Define Conditional Branching Edges from Planner
    workflow.add_conditional_edges(
        "planner",
        orchestration_router.route,
        {
            "sql_node": "sql_node",
            "rag_node": "rag_node",
            "analytics_node": "analytics_node",
            "visualization_node": "visualization_node",
            "validation_node": "validation_node",
            "merge_node": "merge_node",
        },
    )

    # 4. Define Conditional Edges from SQL Node
    workflow.add_conditional_edges(
        "sql_node",
        orchestration_router.route_after_sql,
        {
            "analytics_node": "analytics_node",
            "visualization_node": "visualization_node",
            "validation_node": "validation_node",
        },
    )

    # 5. Define Conditional Edges from Analytics Node
    workflow.add_conditional_edges(
        "analytics_node",
        orchestration_router.route_after_analytics,
        {
            "visualization_node": "visualization_node",
            "validation_node": "validation_node",
        },
    )

    # 6. Connect Tool Execution Nodes to Validation Node
    workflow.add_edge("rag_node", "validation_node")
    workflow.add_edge("visualization_node", "validation_node")

    # 7. Define Conditional Edge from Validation Node (Retry loop or Merge)
    workflow.add_conditional_edges(
        "validation_node",
        orchestration_router.route_after_validation,
        {
            "planner": "planner",
            "merge_node": "merge_node",
        },
    )

    # 8. Define Terminal Edge
    workflow.add_edge("merge_node", END)

    compiled_graph = workflow.compile()
    logger.info("LangGraph Orchestration StateGraph successfully compiled.")
    return compiled_graph



# Compiled Graph Singleton
orchestration_graph = build_orchestration_graph()
