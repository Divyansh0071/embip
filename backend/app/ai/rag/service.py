"""
RAG Retrieval Service for EMBIP AI Architecture.
Executes query vectorization, workspace-isolated Qdrant search, and citation metadata formatting.
"""

import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.ai.embeddings.service import EmbeddingService, embedding_service
from app.ai.vectorstore.models import VectorSearchResult
from app.ai.vectorstore.service import VectorStoreService, vectorstore_service

logger = logging.getLogger(__name__)


class RAGChunkCitation(BaseModel):
    """Traceable document chunk citation for RAG answers."""

    chunk_id: str = Field(..., description="UUID of document chunk")
    document_id: str = Field(..., description="UUID of source document")
    filename: str = Field(..., description="Source document file name")
    file_type: str = Field(..., description="Source file format")
    chunk_index: int = Field(..., description="0-indexed chunk order")
    content: str = Field(..., description="Relevant chunk text content")
    score: float = Field(..., description="Cosine similarity score (0.0 to 1.0)")
    page_number: Optional[int] = Field(default=None, description="Source page number if available")
    sheet_name: Optional[str] = Field(default=None, description="Spreadsheet sheet name if available")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional document metadata")


class RAGRetrievalResponse(BaseModel):
    """Structured RAG semantic search response."""

    query: str
    workspace_id: str
    results: List[RAGChunkCitation]
    total_retrieved: int


class RAGRetrievalService:
    """
    RAG Retrieval Service generating query embeddings and retrieving workspace-isolated vector results.
    """

    def __init__(
        self,
        emb_service: Optional[EmbeddingService] = None,
        vec_service: Optional[VectorStoreService] = None,
    ):
        self.embedding_service = emb_service or embedding_service
        self.vectorstore_service = vec_service or vectorstore_service

    async def retrieve(
        self,
        query: str,
        workspace_id: str,
        top_k: int = 5,
        document_id_filter: Optional[str] = None,
    ) -> RAGRetrievalResponse:
        """
        Executes end-to-end RAG retrieval pipeline:
        Query Validation -> Vector Embedding -> Qdrant Tenant Search -> Citation Formatting.
        """
        if not query or not query.strip():
            raise ValueError("Retrieval query cannot be empty or whitespace-only.")

        cleaned_query = query.strip()
        bounded_top_k = min(max(1, top_k), 50)

        # 1. Generate query vector
        query_vector = await self.embedding_service.embed_query(cleaned_query)

        # 2. Search Qdrant with workspace_id tenant isolation filter
        search_results: List[VectorSearchResult] = await self.vectorstore_service.search_chunks(
            query_vector=query_vector,
            workspace_id=workspace_id,
            limit=bounded_top_k,
            document_id_filter=document_id_filter,
        )

        # 3. Format citations
        citations: List[RAGChunkCitation] = []
        for res in search_results:
            page_num = res.metadata.get("page_number")
            sheet_nm = res.metadata.get("sheet_name")

            citations.append(
                RAGChunkCitation(
                    chunk_id=res.chunk_id,
                    document_id=res.document_id,
                    filename=res.file_name,
                    file_type=res.file_type,
                    chunk_index=res.chunk_index,
                    content=res.content,
                    score=res.score,
                    page_number=int(page_num) if page_num is not None else None,
                    sheet_name=str(sheet_nm) if sheet_nm else None,
                    metadata=res.metadata,
                )
            )

        logger.info(
            f"RAG Retrieval Succeeded | query='{cleaned_query[:30]}...' "
            f"workspace='{workspace_id}' retrieved={len(citations)}"
        )

        return RAGRetrievalResponse(
            query=cleaned_query,
            workspace_id=workspace_id,
            results=citations,
            total_retrieved=len(citations),
        )


# Global Singleton Instance
rag_service = RAGRetrievalService()
