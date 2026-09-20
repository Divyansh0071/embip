"""
FastAPI Router for RAG Semantic Search & Retrieval Endpoint (Phase 8).
Enforces authentication and multi-tenant workspace vector isolation.
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.ai.rag.service import RAGRetrievalResponse, rag_service
from app.core.security import get_current_user

router = APIRouter(prefix="/rag", tags=["rag"])


class RAGSearchRequest(BaseModel):
    """Payload for RAG semantic chunk search."""

    query: str = Field(..., description="Natural language search query")
    top_k: int = Field(default=5, ge=1, le=50, description="Max matching document chunks to retrieve (1-50)")
    document_id: Optional[str] = Field(default=None, description="Optional document ID scope filter")


@router.post("/search", response_model=RAGRetrievalResponse, status_code=status.HTTP_200_OK)
async def search_rag_chunks(
    request: RAGSearchRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Executes semantic similarity search over workspace document chunks.
    Derives workspace_id from authenticated session token to enforce tenant isolation.
    """
    if not request.query or not request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query cannot be empty or whitespace-only.",
        )

    try:
        response = await rag_service.retrieve(
            query=request.query,
            workspace_id=current_user["workspace_id"],
            top_k=request.top_k,
            document_id_filter=request.document_id,
        )
        return response
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during RAG retrieval: {str(e)}",
        )
