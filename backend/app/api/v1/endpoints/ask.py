"""
Ask Natural Language Intelligence API Endpoint (Phase 10).
Provides multi-agent orchestration endpoint executing LangGraph workflow.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
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
async def ask_intelligence(
    request: AskRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AskResponse:
    """
    POST /api/v1/ask
    Guarded endpoint executing multi-agent query orchestration.
    """
    workspace_id = current_user.active_workspace_id
    if not workspace_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Active workspace context is required to process intelligence requests.",
        )

    try:
        response = await orchestration_service.ask(
            question=request.question,
            workspace_id=workspace_id,
            user_id=current_user.id,
            db=db,
        )
        return response

    except Exception as e:
        logger.error(f"Ask API Unexpected Error | user='{current_user.id}' error='{str(e)}'")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during multi-agent orchestration.",
        )
