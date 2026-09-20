"""
Vector Store Subsystem Root Package Exports.
"""

from app.ai.vectorstore.base import VectorStore
from app.ai.vectorstore.config import VectorStoreSettings, vectorstore_config
from app.ai.vectorstore.exceptions import (
    VectorStoreCollectionError,
    VectorStoreConnectionError,
    VectorStoreError,
    VectorStoreOperationError,
)
from app.ai.vectorstore.models import VectorPoint, VectorSearchResult
from app.ai.vectorstore.qdrant import QdrantVectorStore
from app.ai.vectorstore.service import VectorStoreService, vectorstore_service

__all__ = [
    "VectorStore",
    "VectorStoreSettings",
    "vectorstore_config",
    "VectorStoreError",
    "VectorStoreConnectionError",
    "VectorStoreCollectionError",
    "VectorStoreOperationError",
    "VectorPoint",
    "VectorSearchResult",
    "QdrantVectorStore",
    "VectorStoreService",
    "vectorstore_service",
]
