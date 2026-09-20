"""
Pydantic Data Models for Embedding Requests and Responses.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class EmbeddingRequest(BaseModel):
    """Batch or single embedding request."""

    texts: List[str] = Field(..., description="List of strings to embed")
    model: Optional[str] = Field(default=None, description="Override target embedding model name")

    @field_validator("texts")
    @classmethod
    def validate_texts_not_empty(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("EmbeddingRequest texts list cannot be empty.")
        return v


class EmbeddingUsage(BaseModel):
    """Token consumption metrics for embeddings."""

    prompt_tokens: int = Field(default=0)
    total_tokens: int = Field(default=0)


class EmbeddingResponse(BaseModel):
    """Structured response containing generated float embedding vectors."""

    embeddings: List[List[float]] = Field(..., description="Generated vector list matching input texts")
    model: str = Field(..., description="Model identifier used for generation")
    provider: str = Field(..., description="Provider identifier (e.g. openai)")
    dimension: int = Field(..., description="Dimension of generated vectors")
    usage: Optional[EmbeddingUsage] = Field(default=None)
    metadata: Optional[Dict[str, Any]] = Field(default=None)
