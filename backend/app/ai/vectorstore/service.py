"""
Centralized Vector Store Service Orchestrator for EMBIP AI Architecture.
Manages collection initialization, document chunk vector indexing, and workspace-isolated retrieval.
"""

import logging
from typing import List, Optional
from app.ai.embeddings.service import embedding_service
from app.ai.vectorstore.base import VectorStore
from app.ai.vectorstore.config import vectorstore_config
from app.ai.vectorstore.models import VectorPoint, VectorSearchResult
from app.ai.vectorstore.qdrant import QdrantVectorStore
from app.models.documents import Document, DocumentChunk

logger = logging.getLogger(__name__)


class VectorStoreService:
    """
    Service managing Qdrant vector collection setup, vector point creation, upserts, and search operations.
    """

    def __init__(self, provider: Optional[VectorStore] = None):
        self.provider = provider or QdrantVectorStore()
        self.collection_name = vectorstore_config.QDRANT_COLLECTION

    async def ensure_collection(self, vector_size: Optional[int] = None) -> bool:
        """Ensure default target collection exists in vector database."""
        size = vector_size or embedding_service.dimension
        return await self.provider.ensure_collection(self.collection_name, size)

    async def index_document_chunks(
        self,
        document: Document,
        chunks: List[DocumentChunk],
        embeddings: List[List[float]],
    ) -> bool:
        """
        Builds VectorPoint list from document chunks and generated embedding vectors,
        and upserts points into Qdrant.
        """
        if not chunks or not embeddings or len(chunks) != len(embeddings):
            raise ValueError("Chunks list and embeddings list must be non-empty and equal in length.")

        # Ensure vector collection exists before upserting
        dim = len(embeddings[0])
        await self.ensure_collection(vector_size=dim)

        points: List[VectorPoint] = []
        for chunk, vector in zip(chunks, embeddings):
            payload = {
                "chunk_id": chunk.id,
                "document_id": document.id,
                "workspace_id": document.workspace_id,
                "uploaded_by": document.uploaded_by,
                "chunk_index": chunk.chunk_index,
                "file_name": document.file_name,
                "file_type": document.file_type,
                "content": chunk.content,
                "created_at": document.created_at.isoformat() if document.created_at else None,
                "metadata": chunk.metadata_json or {},
            }

            points.append(
                VectorPoint(
                    id=chunk.id,
                    vector=vector,
                    payload=payload,
                )
            )

        return await self.provider.upsert_vectors(self.collection_name, points)

    async def search_chunks(
        self,
        query_vector: List[float],
        workspace_id: str,
        limit: int = 5,
        document_id_filter: Optional[str] = None,
    ) -> List[VectorSearchResult]:
        """
        Executes workspace-isolated vector search for query vector.
        """
        return await self.provider.search_vectors(
            collection_name=self.collection_name,
            query_vector=query_vector,
            filter_workspace_id=workspace_id,
            limit=limit,
            document_id_filter=document_id_filter,
        )

    async def delete_document_vectors(self, document_id: str) -> bool:
        """Deletes document vectors from Qdrant."""
        return await self.provider.delete_document_vectors(self.collection_name, document_id)


# Global Singleton Instance
vectorstore_service = VectorStoreService()
