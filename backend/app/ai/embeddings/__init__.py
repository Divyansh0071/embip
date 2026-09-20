"""
Embedding Subsystem Root Package Exports.
"""

from app.ai.embeddings.base import EmbeddingProvider
from app.ai.embeddings.config import EmbeddingSettings, embedding_config
from app.ai.embeddings.exceptions import (
    EmbeddingAuthenticationError,
    EmbeddingConfigurationError,
    EmbeddingError,
    EmbeddingInvalidRequestError,
    EmbeddingProviderError,
    EmbeddingTimeoutError,
)
from app.ai.embeddings.models import EmbeddingRequest, EmbeddingResponse, EmbeddingUsage
from app.ai.embeddings.service import EmbeddingService, embedding_service

__all__ = [
    "EmbeddingProvider",
    "EmbeddingSettings",
    "embedding_config",
    "EmbeddingError",
    "EmbeddingConfigurationError",
    "EmbeddingAuthenticationError",
    "EmbeddingTimeoutError",
    "EmbeddingProviderError",
    "EmbeddingInvalidRequestError",
    "EmbeddingRequest",
    "EmbeddingResponse",
    "EmbeddingUsage",
    "EmbeddingService",
    "embedding_service",
]
