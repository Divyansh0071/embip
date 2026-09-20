"""
Data Models for Vector Points and Vector Search Results.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class VectorPoint(BaseModel):
    """Vector record to be upserted into vector database."""

    id: str = Field(..., description="Unique vector point ID (UUID str)")
    vector: List[float] = Field(..., description="Dense float embedding vector")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Metadata payload")


class VectorSearchResult(BaseModel):
    """Retrieved vector result with score and metadata payload."""

    chunk_id: str = Field(..., description="UUID of document chunk")
    document_id: str = Field(..., description="UUID of source document")
    workspace_id: str = Field(..., description="Workspace ID for tenant isolation")
    chunk_index: int = Field(..., description="0-indexed chunk order")
    file_name: str = Field(..., description="Source document file name")
    file_type: str = Field(..., description="Source document file extension/type")
    content: str = Field(..., description="Chunk text content")
    score: float = Field(..., description="Cosine similarity score (0.0 to 1.0)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata (page, sheet, etc.)")
