"""
Server-Sent Events (SSE) Streaming Engine for LangGraph Orchestration (Phase 15).
Provides async generator yielding allowlisted JSON event chunks for real-time progress updates.
Executes LangGraph workflow exactly ONCE.
"""

import json
import logging
import time
from typing import AsyncGenerator, Any, Dict, Optional, Set
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import generate_uuid_str
from app.ai.orchestration.graph import orchestration_graph
from app.ai.orchestration.state import OrchestrationState

logger = logging.getLogger(__name__)

# Explicit allowlist of user-facing graph nodes for progress tracking
ALLOWLISTED_NODES: Set[str] = {
    "planner",
    "sql_node",
    "rag_node",
    "analytics_node",
    "visualization_node",
    "validation_node",
    "report_node",
    "merge_node",
}


class OrchestrationStreamer:
    """
    Executes LangGraph orchestration state machine and streams node progress events over SSE.
    Executes graph exactly ONCE and yields only allowlisted metadata.
    """

    async def stream_events(
        self,
        question: str,
        workspace_id: str,
        user_id: Optional[str] = None,
        db: Optional[AsyncSession] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Yields formatted SSE strings: "data: {JSON}\n\n".
        """
        start_time = time.time()
        req_id = generate_uuid_str()

        initial_state: OrchestrationState = {
            "request_id": req_id,
            "user_id": user_id or "anonymous",
            "workspace_id": workspace_id,
            "question": question,
            "plan": None,
            "sql_result": None,
            "rag_result": None,
            "analytics_result": None,
            "visualization_result": None,
            "validation_result": None,
            "report_result": None,
            "retry_count": 0,
            "merged_results": None,
            "errors": [],
            "status": "pending",
        }

        # Configurable dict for db session inside graph nodes
        config = {"configurable": {"db": db}} if db else {}

        # 1. Emit Initial Stream Start Event
        yield self._format_sse_event(
            event_type="stream_started",
            data={
                "request_id": req_id,
                "question": question,
                "status": "running",
                "timestamp": round(time.time(), 3),
            },
        )

        latest_state: Dict[str, Any] = dict(initial_state)
        node_start_times: Dict[str, float] = {}

        try:
            # Execute LangGraph node event stream ONCE
            async for event in orchestration_graph.astream_events(initial_state, config=config, version="v2"):
                kind = event.get("event")
                name = event.get("name")

                if kind == "on_chain_start" and name in ALLOWLISTED_NODES:
                    node_start_times[name] = time.time()
                    yield self._format_sse_event(
                        event_type="node_start",
                        data={
                            "request_id": req_id,
                            "node": name,
                            "status": "running",
                            "timestamp": round(time.time(), 3),
                        },
                    )

                elif kind == "on_chain_end":
                    output = event.get("data", {}).get("output")
                    if isinstance(output, dict):
                        latest_state.update(output)

                    if name in ALLOWLISTED_NODES:
                        n_start = node_start_times.get(name, time.time())
                        duration_ms = round((time.time() - n_start) * 1000, 2)
                        yield self._format_sse_event(
                            event_type="node_complete",
                            data={
                                "request_id": req_id,
                                "node": name,
                                "status": "completed",
                                "duration_ms": duration_ms,
                                "timestamp": round(time.time(), 3),
                            },
                        )

            # Execution finished (SINGLE GRAPH EXECUTION)
            elapsed_ms = round((time.time() - start_time) * 1000, 2)

            plan_dict = latest_state.get("plan") or {
                "intent": "general",
                "requires_sql": False,
                "requires_rag": False,
                "requires_analytics": False,
                "requires_visualization": False,
                "reason": "Default execution plan.",
            }

            merged_results = latest_state.get("merged_results") or {}
            status = latest_state.get("status") or "completed"
            errors = latest_state.get("errors") or []

            yield self._format_sse_event(
                event_type="stream_completed",
                data={
                    "request_id": req_id,
                    "question": question,
                    "status": status,
                    "plan": plan_dict,
                    "results": merged_results,
                    "errors": errors,
                    "execution_time_ms": elapsed_ms,
                    "timestamp": round(time.time(), 3),
                },
            )

        except Exception as e:
            logger.error(f"OrchestrationStreamer Error | request_id='{req_id}' error='{str(e)}'", exc_info=True)
            yield self._format_sse_event(
                event_type="stream_error",
                data={
                    "request_id": req_id,
                    "status": "failed",
                    "error": "An unexpected error occurred during processing.",
                    "timestamp": round(time.time(), 3),
                },
            )

    def _format_sse_event(self, event_type: str, data: Dict[str, Any]) -> str:
        """Helper to format payload into standard SSE format."""
        payload = {"event": event_type, **data}
        return f"data: {json.dumps(payload)}\n\n"


orchestration_streamer = OrchestrationStreamer()
