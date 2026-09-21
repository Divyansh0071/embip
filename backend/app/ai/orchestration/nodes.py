"""
LangGraph Async Node Implementations for Multi-Agent Orchestration (Phase 10).
Executes PlannerAgent, SQLService (Phase 9), RAGRetrievalService (Phase 8),
Future Phase Adapters (Analytics/Visualization), and Response Merge.
"""

import logging
from typing import Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.analytics import AnalyticsInput, analytics_service
from app.ai.visualization import visualization_service
from app.ai.validation import ValidationRequest, validation_service
from app.ai.report import report_service
from app.ai.rag import rag_service
from app.ai.sql import SQLQueryRequest, sql_service

from app.ai.orchestration.planner import planner_agent
from app.ai.orchestration.state import OrchestrationState

logger = logging.getLogger(__name__)




async def planner_node(state: OrchestrationState) -> Dict[str, Any]:
    """
    Graph Node: Executes PlannerAgent to classify business question intent.
    """
    question = state["question"]
    try:
        plan = await planner_agent.plan(question)
        return {"plan": plan.model_dump()}
    except Exception as e:
        logger.error(f"planner_node Error | error='{str(e)}'")
        errors = list(state.get("errors") or [])
        errors.append(f"Planner Agent error: {str(e)}")
        return {
            "plan": {
                "intent": "general",
                "requires_sql": False,
                "requires_rag": False,
                "requires_analytics": False,
                "requires_visualization": False,
                "reason": f"Planner failed: {str(e)}",
            },
            "errors": errors,
            "status": "failed",
        }


async def sql_node(state: OrchestrationState, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Graph Node: Executes Phase 9 SQLService for database metric retrieval.
    """
    question = state["question"]
    workspace_id = state["workspace_id"]
    user_id = state.get("user_id")

    # Extract db session from RunnableConfig configurable dict if passed
    configurable = (config or {}).get("configurable", {})
    db: AsyncSession = configurable.get("db")

    if not db:
        logger.error("sql_node Error | No database session provided in graph config.")
        errors = list(state.get("errors") or [])
        errors.append("SQL Agent execution skipped: No database session available.")
        return {
            "sql_result": {"status": "error", "error": "No database session available."},
            "errors": errors,
        }

    try:
        req = SQLQueryRequest(question=question)
        resp = await sql_service.execute_question(
            session=db,
            request=req,
            workspace_id=workspace_id,
            user_id=user_id,
        )
        return {"sql_result": resp.model_dump()}
    except Exception as e:
        logger.error(f"sql_node Error | error='{str(e)}'")
        errors = list(state.get("errors") or [])
        errors.append(f"SQL Agent error: {str(e)}")
        return {
            "sql_result": {"status": "error", "error": str(e)},
            "errors": errors,
        }


async def rag_node(state: OrchestrationState) -> Dict[str, Any]:
    """
    Graph Node: Executes Phase 8 RAGRetrievalService for document chunk retrieval.
    """
    question = state["question"]
    workspace_id = state["workspace_id"]

    try:
        rag_resp = await rag_service.retrieve(
            query=question,
            workspace_id=workspace_id,
            top_k=5,
        )
        return {"rag_result": rag_resp.model_dump()}
    except Exception as e:
        logger.error(f"rag_node Error | error='{str(e)}'")
        errors = list(state.get("errors") or [])
        errors.append(f"RAG Retrieval error: {str(e)}")
        return {
            "rag_result": {"status": "error", "error": str(e)},
            "errors": errors,
        }


async def analytics_node(state: OrchestrationState) -> Dict[str, Any]:
    """
    Graph Node: Executes Phase 11 Analytics Service to perform deterministic calculations.
    """
    question = state["question"]
    workspace_id = state.get("workspace_id")
    sql_res = state.get("sql_result") or {}

    rows = sql_res.get("rows")
    columns = sql_res.get("columns")

    if not rows or not columns:
        logger.warning("analytics_node called but no valid SQL tabular rows/columns in state.")
        return {
            "analytics_result": {
                "operation": "unknown",
                "status": "skipped",
                "summary": {"rows_input": 0, "rows_used": 0, "missing_values": 0, "warnings": ["SQL Agent returned no rows/columns for analytical processing."]},
                "explanation": "Analytics skipped because no structured SQL data was returned.",
                "error": "No SQL tabular data available for analysis.",
            }
        }

    try:
        input_data = AnalyticsInput(
            columns=columns,
            rows=rows,
            operation="",  # Service will auto-classify based on question
        )
        res = await analytics_service.analyze(
            input_data=input_data,
            question=question,
            sql_request_id=sql_res.get("request_id"),
            workspace_id=workspace_id,
        )
        return {"analytics_result": res.model_dump()}
    except Exception as e:
        logger.error(f"analytics_node Error | error='{str(e)}'")
        errors = list(state.get("errors") or [])
        errors.append(f"Analytics Agent error: {str(e)}")
        return {
            "analytics_result": {"status": "error", "error": str(e)},
            "errors": errors,
        }


async def visualization_node(state: OrchestrationState) -> Dict[str, Any]:
    """
    Graph Node: Executes Phase 12 Visualization Agent to generate Recharts JSON specs.
    """
    question = state["question"]
    sql_res = state.get("sql_result")
    analytics_res = state.get("analytics_result")

    try:
        res = await visualization_service.generate_spec(
            question=question,
            sql_result=sql_res,
            analytics_result=analytics_res,
        )
        return {"visualization_result": res.model_dump()}
    except Exception as e:
        logger.error(f"visualization_node Error | error='{str(e)}'")
        errors = list(state.get("errors") or [])
        errors.append(f"Visualization Agent error: {str(e)}")
        return {
            "visualization_result": {"status": "error", "error": str(e)},
            "errors": errors,
        }


async def validation_node(state: OrchestrationState) -> Dict[str, Any]:
    """
    Graph Node: Executes Phase 13 Validation & Guardrails Agent to audit candidate state.
    """
    question = state["question"]
    plan = state.get("plan")
    sql_res = state.get("sql_result")
    rag_res = state.get("rag_result")
    analytics_res = state.get("analytics_result")
    viz_res = state.get("visualization_result")
    retry_count = state.get("retry_count", 0)

    try:
        req = ValidationRequest(
            question=question,
            plan=plan,
            sql_result=sql_res,
            rag_result=rag_res,
            analytics_result=analytics_res,
            visualization_result=viz_res,
        )
        report = await validation_service.validate(req)
        report_dict = report.model_dump()

        if report.action == "retry" and retry_count < 2:
            errors = list(state.get("errors") or [])
            errors.append(f"Validation retry attempt {retry_count + 1}: {', '.join(report.warnings or ['Low confidence'])}")
            return {
                "validation_result": report_dict,
                "retry_count": retry_count + 1,
                "errors": errors,
            }

        return {
            "validation_result": report_dict,
            "retry_count": retry_count,
        }
    except Exception as e:
        logger.error(f"validation_node Error | error='{str(e)}'")
        errors = list(state.get("errors") or [])
        errors.append(f"Validation Agent error: {str(e)}")
        return {
            "validation_result": {
                "is_valid": False,
                "confidence_score": 0.5,
                "checks": [],
                "hallucinations_detected": [],
                "contradictions_detected": [],
                "warnings": [f"Validation exception: {str(e)}"],
                "action": "flag",
            },
            "retry_count": retry_count,
            "errors": errors,
        }


async def report_node(state: OrchestrationState) -> Dict[str, Any]:
    """
    Graph Node: Executes Phase 14 Report Generator Agent to synthesize executive business report.
    """
    question = state["question"]
    sql_res = state.get("sql_result")
    rag_res = state.get("rag_result")
    analytics_res = state.get("analytics_result")
    viz_res = state.get("visualization_result")
    val_res = state.get("validation_result")

    try:
        report_data = await report_service.generate_report(
            question=question,
            sql_result=sql_res,
            rag_result=rag_res,
            analytics_result=analytics_res,
            visualization_result=viz_res,
            validation_result=val_res,
        )
        return {"report_result": report_data.model_dump()}
    except Exception as e:
        logger.error(f"report_node Error | error='{str(e)}'")
        errors = list(state.get("errors") or [])
        errors.append(f"Report Generator Agent error: {str(e)}")
        return {
            "report_result": {"status": "error", "error": str(e)},
            "errors": errors,
        }


async def merge_node(state: OrchestrationState) -> Dict[str, Any]:
    """
    Graph Node: Aggregates structured outputs from all executed capability nodes.
    """
    merged = {
        "sql": state.get("sql_result"),
        "rag": state.get("rag_result"),
        "analytics": state.get("analytics_result"),
        "visualization": state.get("visualization_result"),
        "validation": state.get("validation_result"),
        "report": state.get("report_result"),
    }

    errors = state.get("errors") or []
    status = "completed"
    if errors:
        status = "partial" if any(v is not None for v in merged.values()) else "failed"

    return {
        "merged_results": merged,
        "status": status,
    }
