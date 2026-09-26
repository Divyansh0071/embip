"""
Ask Natural Language Intelligence API Endpoint (Phase 10).
Provides multi-agent orchestration endpoint executing LangGraph workflow.
"""

import logging
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.core.security import get_current_user
from app.models.tenancy import User
from app.ai.orchestration.models import AskRequest, AskResponse
from app.ai.orchestration.service import orchestration_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "",
    response_model=AskResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask Natural Language Intelligence Query",
    description="Orchestrates multi-agent execution (Planner, SQL, RAG, Analytics, Visualization) via LangGraph.",
)
@limiter.limit(lambda: f"{settings.RATE_LIMIT_ASK_PER_MINUTE}/minute")
async def ask_intelligence(
    request_data: AskRequest,
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AskResponse:
    """
    POST /api/v1/ask
    Guarded endpoint executing multi-agent query orchestration.
    """
    user_id = current_user.get("id") if isinstance(current_user, dict) else getattr(current_user, "id", "")
    workspace_id = current_user.get("workspace_id") if isinstance(current_user, dict) else getattr(current_user, "active_workspace_id", None)
    if not workspace_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Active workspace context is required to process intelligence requests.",
        )

    try:
        response = await orchestration_service.ask(
            question=request_data.question,
            workspace_id=workspace_id,
            user_id=user_id,
            db=db,
        )
        return response

    except Exception as e:
        logger.error(f"Ask API Unexpected Error | user='{user_id}' error='{str(e)}'")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during multi-agent orchestration.",
        )


@router.get(
    "/stream",
    summary="Stream Natural Language Intelligence Query Events",
    description="Streams real-time Server-Sent Events (SSE) progress updates as LangGraph agent nodes execute.",
)
@limiter.limit(lambda: f"{settings.RATE_LIMIT_ASK_PER_MINUTE}/minute")
async def ask_intelligence_stream(
    question: str,
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    GET /api/v1/ask/stream?question=...
    Real-time Server-Sent Events (SSE) stream endpoint.
    """
    user_id = current_user.get("id") if isinstance(current_user, dict) else getattr(current_user, "id", "")
    workspace_id = current_user.get("workspace_id") if isinstance(current_user, dict) else getattr(current_user, "active_workspace_id", None)
    if not workspace_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Active workspace context is required to process intelligence requests.",
        )

    try:
        generator = await orchestration_service.ask_stream(
            question=question,
            workspace_id=workspace_id,
            user_id=user_id,
            db=db,
        )
        return StreamingResponse(
            generator,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    except Exception as e:
        logger.error(f"Ask Stream API Unexpected Error | user='{user_id}' error='{str(e)}'")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during streaming orchestration.",
        )
