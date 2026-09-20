"""
Abstract Base Vector Store Interface.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from app.ai.vectorstore.models import VectorPoint, VectorSearchResult


class VectorStore(ABC):
    """Abstract interface for Vector DB operations (Qdrant, Pinecone, Milvus, PgVector, etc.)."""

    @abstractmethod
    async def ensure_collection(self, collection_name: str, vector_size: int) -> bool:
        """
        Verify that collection exists or create it with cosine distance & specified vector_size.
        """
        pass

    @abstractmethod
    async def upsert_vectors(self, collection_name: str, points: List[VectorPoint]) -> bool:
        """
        Upsert a batch of vector points into specified collection.
        """
        pass

    @abstractmethod
    async def search_vectors(
        self,
        collection_name: str,
        query_vector: List[float],
        filter_workspace_id: str,
        limit: int = 5,
        document_id_filter: Optional[str] = None,
    ) -> List[VectorSearchResult]:
        """
        Executes semantic similarity search with mandatory workspace_id payload filter.
        """
        pass

    @abstractmethod
    async def delete_document_vectors(self, collection_name: str, document_id: str) -> bool:
        """
        Deletes all vector points matching document_id payload filter.
        """
        pass
