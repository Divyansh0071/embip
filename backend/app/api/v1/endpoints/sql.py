"""
SQL Query Execution API Endpoint (Phase 9).
Provides secure natural language SQL query processing with JWT auth & workspace isolation.
"""

import logging
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.core.security import get_current_user
from app.models.tenancy import User
from app.ai.sql.exceptions import (
    SQLExecutionError,
    SQLExecutionTimeoutError,
    SQLSecurityError,
    SQLValidationError,
)
from app.ai.sql.models import SQLQueryRequest, SQLQueryResponse
from app.ai.sql.service import sql_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/query",
    response_model=SQLQueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute Natural Language SQL Query",
    description="Translates a natural language business question into validated read-only SQL and returns PostgreSQL results.",
)
@limiter.limit(lambda: f"{settings.RATE_LIMIT_SQL_PER_MINUTE}/minute")
async def execute_sql_query(
    query_request: SQLQueryRequest,
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SQLQueryResponse:
    """
    POST /api/v1/sql/query
    Guarded endpoint translating natural language questions into executed SQL database results.
    """
    user_id = current_user.get("id") if isinstance(current_user, dict) else getattr(current_user, "id", "")
    workspace_id = current_user.get("workspace_id") if isinstance(current_user, dict) else getattr(current_user, "active_workspace_id", None)
    if not workspace_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Active workspace context is required to execute database queries.",
        )

    try:
        response = await sql_service.execute_question(
            session=db,
            request=query_request,
            workspace_id=workspace_id,
            user_id=user_id,
        )
        return response

    except (SQLValidationError, SQLSecurityError) as e:
        logger.warning(f"SQL API Validation Error | user='{user_id}' error='{e.message}'")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SQL Query Validation Failed: {e.message}",
        )

    except SQLExecutionTimeoutError as e:
        logger.error(f"SQL API Timeout | user='{user_id}' error='{e.message}'")
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail="Database query execution timed out. Try refining your question to a smaller date range or scope.",
        )

    except SQLExecutionError as e:
        logger.error(f"SQL API Execution Error | user='{user_id}' error='{e.message}'")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database execution error occurred while running generated query.",
        )

    except Exception as e:
        logger.error(f"SQL API Unexpected Failure | user='{user_id}' error='{str(e)}'")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your request.",
        )
