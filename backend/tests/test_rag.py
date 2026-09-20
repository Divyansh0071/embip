"""
Unit & Integration Test Suite for RAG Retrieval & Semantic Search API (Phase 8).
IMPORTANT: All external OpenAI and Qdrant calls are 100% mocked. ZERO paid API calls made.
"""

from unittest.mock import AsyncMock, MagicMock
import pytest
from fastapi.testclient import TestClient

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.ai.embeddings.service import EmbeddingService
from app.ai.rag.service import RAGChunkCitation, RAGRetrievalService
from app.ai.vectorstore.models import VectorSearchResult
from app.ai.vectorstore.service import VectorStoreService
from app.core.database import Base
from app.documents.services.processing_service import DocumentProcessingService
from app.main import app

client = TestClient(app)


@pytest.fixture
async def test_engine():
    """Fixture providing an async in-memory SQLite engine."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine):
    """Fixture providing a clean test AsyncSession."""
    async_session = async_sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


# ------------------------------------------------------------------------------
# 1. RAG RETRIEVAL SERVICE TESTS
# ------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_rag_retrieval_service_success():
    """Test successful RAG retrieval with query embedding and vector search."""
    mock_emb_service = MagicMock(spec=EmbeddingService)
    mock_emb_service.embed_query = AsyncMock(return_value=[0.1] * 1536)

    mock_search_result = VectorSearchResult(
        chunk_id="chunk-999",
        document_id="doc-999",
        workspace_id="ws-tenant-1",
        chunk_index=0,
        file_name="Q3_Financials.pdf",
        file_type="pdf",
        content="Q3 Profit reached $2.4M",
        score=0.92,
        metadata={"page_number": 4},
    )

    mock_vec_service = MagicMock(spec=VectorStoreService)
    mock_vec_service.search_chunks = AsyncMock(return_value=[mock_search_result])

    service = RAGRetrievalService(emb_service=mock_emb_service, vec_service=mock_vec_service)

    resp = await service.retrieve(query="What was Q3 profit?", workspace_id="ws-tenant-1", top_k=5)

    assert resp.query == "What was Q3 profit?"
    assert resp.workspace_id == "ws-tenant-1"
    assert resp.total_retrieved == 1
    assert len(resp.results) == 1

    citation = resp.results[0]
    assert isinstance(citation, RAGChunkCitation)
    assert citation.document_id == "doc-999"
    assert citation.filename == "Q3_Financials.pdf"
    assert citation.score == 0.92
    assert citation.page_number == 4


@pytest.mark.asyncio
async def test_rag_retrieval_empty_query_validation():
    """Verify empty or whitespace query raises ValueError."""
    service = RAGRetrievalService()
    with pytest.raises(ValueError, match="cannot be empty"):
        await service.retrieve(query="   ", workspace_id="ws-1")


# ------------------------------------------------------------------------------
# 2. DOCUMENT INGESTION VECTOR INDEXING FAILURE HANDLING
# ------------------------------------------------------------------------------

from sqlalchemy import select
from app.models.documents import DocumentChunk


@pytest.mark.asyncio
async def test_document_processing_vector_indexing_failure(test_session):
    """
    Verify that if vector indexing fails during upload processing:
    1. Document status is set to 'failed'.
    2. Safe processing_error is logged.
    3. Stored PostgreSQL chunks are NOT destroyed.
    """
    mock_emb = MagicMock(spec=EmbeddingService)
    mock_emb.embed_texts = AsyncMock(side_effect=RuntimeError("OpenAI Embedding API Timeout"))

    service = DocumentProcessingService(session=test_session, emb_service=mock_emb)

    doc = await service.process_document_upload(
        file_bytes=b"Sample document text for embedding failure test",
        original_filename="sample_test.txt",
        declared_mime="text/plain",
        workspace_id="ws-fail-test",
        uploaded_by="user-fail-test",
    )

    assert doc.status == "failed"
    assert "Vector indexing failed" in doc.processing_error

    stmt = select(DocumentChunk).where(DocumentChunk.document_id == doc.id)
    res = await test_session.execute(stmt)
    chunks = res.scalars().all()
    assert len(chunks) >= 1  # PostgreSQL chunks preserved


# ------------------------------------------------------------------------------
# 3. FASTAPI RAG API ENDPOINT TESTS
# ------------------------------------------------------------------------------

def test_rag_search_unauthenticated_rejected():
    """Verify POST /api/v1/rag/search without Bearer token is rejected with HTTP 401."""
    response = client.post("/api/v1/rag/search", json={"query": "sales forecast", "top_k": 5})
    assert response.status_code == 401
