"""
Unit & Integration Test Suite for Vector Store Subsystem (Phase 8).
IMPORTANT: All Qdrant vector database calls are 100% mocked. ZERO live cluster connections required.
"""

from unittest.mock import AsyncMock, MagicMock
import pytest
from qdrant_client import models

from app.ai.vectorstore.models import VectorPoint, VectorSearchResult
from app.ai.vectorstore.qdrant import QdrantVectorStore
from app.ai.vectorstore.service import VectorStoreService
from app.models.documents import Document, DocumentChunk


@pytest.mark.asyncio
async def test_qdrant_ensure_collection():
    """Verify QdrantVectorStore checks collection existence and creates if missing."""
    mock_client = MagicMock()
    mock_client.collection_exists = AsyncMock(return_value=False)
    mock_client.create_collection = AsyncMock(return_value=True)

    store = QdrantVectorStore(client=mock_client)
    success = await store.ensure_collection("test_collection", vector_size=1536)

    assert success is True
    mock_client.collection_exists.assert_called_once_with("test_collection")
    mock_client.create_collection.assert_called_once()


@pytest.mark.asyncio
async def test_qdrant_upsert_vectors():
    """Verify points are upserted into Qdrant collection."""
    mock_client = MagicMock()
    mock_client.upsert = AsyncMock(return_value=True)

    store = QdrantVectorStore(client=mock_client)
    point = VectorPoint(
        id="chunk-uuid-1",
        vector=[0.1] * 1536,
        payload={"workspace_id": "ws-100", "content": "Sample content"},
    )

    success = await store.upsert_vectors("test_collection", [point])
    assert success is True
    mock_client.upsert.assert_called_once()


@pytest.mark.asyncio
async def test_qdrant_search_vectors_tenant_isolation():
    """Verify search_vectors enforces workspace_id payload filter for tenant isolation."""
    mock_client = MagicMock()

    mock_hit = MagicMock()
    mock_hit.id = "chunk-uuid-1"
    mock_hit.score = 0.89
    mock_hit.payload = {
        "chunk_id": "chunk-uuid-1",
        "document_id": "doc-uuid-1",
        "workspace_id": "ws-target-123",
        "chunk_index": 0,
        "file_name": "annual_report.pdf",
        "file_type": "pdf",
        "content": "Q3 Revenue reached $12M",
        "metadata": {"page_number": 3},
    }

    mock_client.search = AsyncMock(return_value=[mock_hit])
    store = QdrantVectorStore(client=mock_client)

    results = await store.search_vectors(
        collection_name="test_collection",
        query_vector=[0.1] * 1536,
        filter_workspace_id="ws-target-123",
        limit=5,
    )

    assert len(results) == 1
    assert results[0].workspace_id == "ws-target-123"
    assert results[0].file_name == "annual_report.pdf"
    assert results[0].score == 0.89

    # Verify search call passed workspace_id filter
    call_kwargs = mock_client.search.call_args[1]
    query_filter = call_kwargs["query_filter"]
    assert query_filter.must[0].key == "workspace_id"
    assert query_filter.must[0].match.value == "ws-target-123"


@pytest.mark.asyncio
async def test_vectorstore_service_indexing():
    """Verify VectorStoreService builds payload points and indexes document chunks."""
    mock_provider = MagicMock()
    mock_provider.ensure_collection = AsyncMock(return_value=True)
    mock_provider.upsert_vectors = AsyncMock(return_value=True)

    service = VectorStoreService(provider=mock_provider)

    document = Document(
        id="doc-100",
        workspace_id="ws-100",
        file_name="invoice.pdf",
        file_type="pdf",
    )
    chunk = DocumentChunk(
        id="chunk-100",
        document_id="doc-100",
        chunk_index=0,
        content="Invoice Total: $500",
    )

    embeddings = [[0.5] * 1536]
    success = await service.index_document_chunks(document, [chunk], embeddings)

    assert success is True
    mock_provider.upsert_vectors.assert_called_once()
    upsert_args = mock_provider.upsert_vectors.call_args[0]
    points = upsert_args[1]
    assert len(points) == 1
    assert points[0].payload["workspace_id"] == "ws-100"
    assert points[0].payload["content"] == "Invoice Total: $500"
