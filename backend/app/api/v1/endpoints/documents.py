"""
FastAPI Router for Document Ingestion & Management API Endpoints (Phase 7).
Enforces RBAC and multi-tenant workspace isolation.
Uses reconciled schema with lowercase statuses ('uploaded', 'processing', 'processed', 'failed').
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, Response, UploadFile, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.core.security import get_current_user, require_role
from app.documents.processing.validator import DocumentValidationError
from app.documents.services.processing_service import DocumentProcessingService

router = APIRouter(prefix="/documents", tags=["documents"])


# Response Pydantic Schemas
class DocumentChunkResponse(BaseModel):
    id: str
    chunk_index: int
    content: str
    char_count: int
    token_count: int
    metadata_json: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class DocumentResponse(BaseModel):
    id: str
    workspace_id: str
    uploaded_by: Optional[str] = None
    file_name: str
    original_filename: Optional[str] = None
    file_type: str
    mime_type: Optional[str] = None
    file_size: int
    status: str
    processing_error: Optional[str] = None
    created_at: Any
    chunk_count: Optional[int] = 0

    @property
    def filename(self) -> str:
        return self.file_name

    model_config = ConfigDict(from_attributes=True)


class DocumentDetailResponse(DocumentResponse):
    chunks: List[DocumentChunkResponse] = []


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(lambda: f"{settings.RATE_LIMIT_UPLOAD_PER_MINUTE}/minute")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(require_role(["ANALYST", "MANAGER", "ADMIN"])),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload and process a document file (PDF, DOCX, TXT, CSV, XLSX).
    Validates, extracts, cleans, chunks, and persists file metadata and chunks.
    Requires ANALYST, MANAGER, or ADMIN role.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a valid filename.",
        )

    try:
        file_bytes = await file.read()
        service = DocumentProcessingService(db)

        document = await service.process_document_upload(
            file_bytes=file_bytes,
            original_filename=file.filename,
            declared_mime=file.content_type or "",
            workspace_id=current_user["workspace_id"],
            uploaded_by=current_user["id"],
            org_id=current_user.get("organization_id"),
        )

        # Build response with chunk count
        resp = DocumentResponse.model_validate(document)
        resp.chunk_count = len(document.chunks) if document.chunks else 0
        return resp

    except DocumentValidationError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during document upload: {str(e)}",
        )


@router.get("", response_model=List[DocumentResponse])
async def list_workspace_documents(
    doc_status: Optional[str] = Query(None, alias="status", description="Filter by status (uploaded, processing, processed, failed)"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: Dict[str, Any] = Depends(require_role(["VIEWER", "ANALYST", "MANAGER", "ADMIN"])),
    db: AsyncSession = Depends(get_db),
):
    """
    List documents owned by the authenticated user's workspace.
    Supports filtering by processing status and pagination.
    """
    service = DocumentProcessingService(db)
    docs = await service.list_documents(
        workspace_id=current_user["workspace_id"],
        limit=limit,
        offset=offset,
        status=doc_status,
    )

    result = []
    for doc in docs:
        item = DocumentResponse.model_validate(doc)
        item.chunk_count = len(doc.chunks) if doc.chunks else 0
        result.append(item)
    return result


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document_details(
    document_id: str,
    current_user: Dict[str, Any] = Depends(require_role(["VIEWER", "ANALYST", "MANAGER", "ADMIN"])),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve document details and chunk summary for a specific document ID.
    Enforces tenant isolation by workspace ID.
    """
    service = DocumentProcessingService(db)
    doc = await service.get_document(document_id, workspace_id=current_user["workspace_id"])

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' not found in your workspace.",
        )

    resp = DocumentDetailResponse.model_validate(doc)
    resp.chunk_count = len(doc.chunks) if doc.chunks else 0
    return resp


@router.get("/{document_id}/download")
@limiter.limit(lambda: f"{settings.RATE_LIMIT_DOWNLOAD_PER_MINUTE}/minute")
async def download_document(
    document_id: str,
    request: Request,
    current_user: Dict[str, Any] = Depends(require_role(["VIEWER", "ANALYST", "MANAGER", "ADMIN"])),
    db: AsyncSession = Depends(get_db),
):
    """
    Download the original document file.
    Requires VIEWER, ANALYST, MANAGER, or ADMIN role.
    Enforces tenant isolation by workspace ID.
    """
    service = DocumentProcessingService(db)
    result = await service.retrieve_document_file(
        document_id=document_id,
        workspace_id=current_user["workspace_id"],
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' not found in your workspace.",
        )

    file_bytes, filename, mime_type = result

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Length": str(len(file_bytes)),
    }

    return Response(
        content=file_bytes,
        media_type=mime_type,
        headers=headers,
    )


@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
async def delete_document(
    document_id: str,
    current_user: Dict[str, Any] = Depends(require_role(["MANAGER", "ADMIN"])),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a document and its processed chunks from the workspace.
    Requires MANAGER or ADMIN role. Enforces tenant isolation.
    """
    service = DocumentProcessingService(db)
    deleted = await service.delete_document(document_id, workspace_id=current_user["workspace_id"])

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' not found in your workspace.",
        )

    return {"success": True, "message": f"Document '{document_id}' deleted successfully."}
