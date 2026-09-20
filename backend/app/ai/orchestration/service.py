"""
Application-Level Orchestration Service (Phase 10).
Provides clean entry point for multi-agent execution, managing request correlation IDs,
authenticated workspace propagation, and LangGraph workflow invocation.
"""

import logging
import time
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import generate_uuid_str
from app.ai.orchestration.graph import orchestration_graph
from app.ai.orchestration.models import AskResponse, PlannerPlan

logger = logging.getLogger(__name__)


class OrchestrationService:
    """
    High-level orchestrator service invoking compiled LangGraph workflow.
    """

    async def ask(
        self,
        question: str,
        workspace_id: str,
        user_id: str,
        db: AsyncSession,
        request_id: Optional[str] = None,
    ) -> AskResponse:
        """
        Processes natural language question through LangGraph multi-agent workflow.
        """
        req_id = request_id or generate_uuid_str()
        start_time = time.time()

        initial_state = {
            "request_id": req_id,
            "user_id": user_id,
            "workspace_id": workspace_id,
            "question": question,
            "plan": None,
            "sql_result": None,
            "rag_result": None,
            "analytics_result": None,
            "visualization_result": None,
            "merged_results": None,
            "errors": [],
            "status": "pending",
        }

        # Pass db session to graph nodes via RunnableConfig
        config = {"configurable": {"db": db}}

        try:
            logger.info(f"Orchestration Start | req_id='{req_id}' user='{user_id}' ws='{workspace_id}'")
            final_state = await orchestration_graph.ainvoke(initial_state, config=config)
            execution_time_ms = round((time.time() - start_time) * 1000, 2)

            plan_dict = final_state.get("plan") or {
                "intent": "general",
                "requires_sql": False,
                "requires_rag": False,
                "requires_analytics": False,
                "requires_visualization": False,
                "reason": "Default execution plan.",
            }

            plan = PlannerPlan(**plan_dict)
            results = final_state.get("merged_results") or {}
            errors = final_state.get("errors") or []
            status = final_state.get("status") or "completed"

            logger.info(f"Orchestration Complete | req_id='{req_id}' status='{status}' duration={execution_time_ms}ms")

            return AskResponse(
                request_id=req_id,
                question=question,
                status=status,
                plan=plan,
                results=results,
                errors=errors,
                execution_time_ms=execution_time_ms,
            )

        except Exception as e:
            execution_time_ms = round((time.time() - start_time) * 1000, 2)
            logger.error(f"Orchestration Failed | req_id='{req_id}' error='{str(e)}'")
            return AskResponse(
                request_id=req_id,
                question=question,
                status="failed",
                plan=PlannerPlan(
                    intent="general",
                    requires_sql=False,
                    requires_rag=False,
                    requires_analytics=False,
                    requires_visualization=False,
                    reason=f"Orchestration failed: {str(e)}",
                ),
                results={},
                errors=[str(e)],
                execution_time_ms=execution_time_ms,
            )


# Singleton Instance
orchestration_service = OrchestrationService()
