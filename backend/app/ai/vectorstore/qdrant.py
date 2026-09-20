"""
Concrete Qdrant Vector Store Implementation using qdrant-client.
Supports local Qdrant server and Qdrant Cloud.
Enforces Cosine distance and workspace payload filtering for tenant isolation.
"""

import logging
from typing import Any, Dict, List, Optional
from qdrant_client import AsyncQdrantClient, models
from qdrant_client.http.exceptions import UnexpectedResponse

from app.ai.vectorstore.base import VectorStore
from app.ai.vectorstore.config import vectorstore_config
from app.ai.vectorstore.exceptions import (
    VectorStoreCollectionError,
    VectorStoreConnectionError,
    VectorStoreOperationError,
)
from app.ai.vectorstore.models import VectorPoint, VectorSearchResult

logger = logging.getLogger(__name__)


class QdrantVectorStore(VectorStore):
    """
    Qdrant implementation of VectorStore interface.
    """

    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        client: Optional[AsyncQdrantClient] = None,
    ):
        self.url = url or vectorstore_config.QDRANT_URL
        self.api_key = api_key or vectorstore_config.QDRANT_API_KEY
        self._client = client

    def _get_client(self) -> AsyncQdrantClient:
        if self._client:
            return self._client

        try:
            if self.api_key and "your-" not in self.api_key:
                self._client = AsyncQdrantClient(
                    url=self.url,
                    api_key=self.api_key,
                    timeout=vectorstore_config.QDRANT_TIMEOUT_SECONDS,
                )
            else:
                self._client = AsyncQdrantClient(
                    url=self.url,
                    timeout=vectorstore_config.QDRANT_TIMEOUT_SECONDS,
                )
            return self._client
        except Exception as e:
            raise VectorStoreConnectionError(f"Failed to initialize Qdrant client: {str(e)}") from e

    async def ensure_collection(self, collection_name: str, vector_size: int) -> bool:
        client = self._get_client()
        try:
            exists = await client.collection_exists(collection_name)
            if not exists:
                logger.info(f"Creating Qdrant collection '{collection_name}' (dim={vector_size}, distance=COSINE)...")
                await client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(
                        size=vector_size,
                        distance=models.Distance.COSINE,
                    ),
                )
            return True
        except Exception as e:
            raise VectorStoreCollectionError(f"Failed to ensure Qdrant collection '{collection_name}': {str(e)}") from e

    async def upsert_vectors(self, collection_name: str, points: List[VectorPoint]) -> bool:
        if not points:
            return True

        client = self._get_client()
        qdrant_points = [
            models.PointStruct(
                id=p.id,
                vector=p.vector,
                payload=p.payload,
            )
            for p in points
        ]

        try:
            await client.upsert(
                collection_name=collection_name,
                points=qdrant_points,
            )
            logger.info(f"Successfully upserted {len(points)} vector points to Qdrant collection '{collection_name}'.")
            return True
        except Exception as e:
            raise VectorStoreOperationError(f"Qdrant vector upsert failed: {str(e)}") from e

    async def search_vectors(
        self,
        collection_name: str,
        query_vector: List[float],
        filter_workspace_id: str,
        limit: int = 5,
        document_id_filter: Optional[str] = None,
    ) -> List[VectorSearchResult]:
        client = self._get_client()

        # Enforce workspace tenant isolation filter
        must_conditions = [
            models.FieldCondition(
                key="workspace_id",
                match=models.MatchValue(value=filter_workspace_id),
            )
        ]

        if document_id_filter:
            must_conditions.append(
                models.FieldCondition(
                    key="document_id",
                    match=models.MatchValue(value=document_id_filter),
                )
            )

        payload_filter = models.Filter(must=must_conditions)

        try:
            # Use query_points or search
            hits = await client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                query_filter=payload_filter,
                limit=limit,
                with_payload=True,
            )

            results: List[VectorSearchResult] = []
            for hit in hits:
                payload = hit.payload or {}
                results.append(
                    VectorSearchResult(
                        chunk_id=str(payload.get("chunk_id", hit.id)),
                        document_id=str(payload.get("document_id", "")),
                        workspace_id=str(payload.get("workspace_id", filter_workspace_id)),
                        chunk_index=int(payload.get("chunk_index", 0)),
                        file_name=str(payload.get("file_name", "document")),
                        file_type=str(payload.get("file_type", "txt")),
                        content=str(payload.get("content", "")),
                        score=float(hit.score),
                        metadata=payload.get("metadata", {}),
                    )
                )

            return results
        except Exception as e:
            raise VectorStoreOperationError(f"Qdrant vector search failed: {str(e)}") from e

    async def delete_document_vectors(self, collection_name: str, document_id: str) -> bool:
        client = self._get_client()
        payload_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="document_id",
                    match=models.MatchValue(value=document_id),
                )
            ]
        )

        try:
            await client.delete(
                collection_name=collection_name,
                points_selector=models.FilterSelector(filter=payload_filter),
            )
            logger.info(f"Deleted vectors for document_id='{document_id}' from Qdrant.")
            return True
        except Exception as e:
            logger.warning(f"Failed to delete Qdrant vectors for document_id='{document_id}': {str(e)}")
            return False
