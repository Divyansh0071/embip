"""
Unit & Integration Test Suite for Embedding Subsystem (Phase 8).
IMPORTANT: All external OpenAI Embedding API calls are 100% mocked. ZERO paid API calls made.
"""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest
import openai

from app.ai.embeddings.base import EmbeddingProvider
from app.ai.embeddings.config import EmbeddingSettings
from app.ai.embeddings.exceptions import (
    EmbeddingAuthenticationError,
    EmbeddingConfigurationError,
    EmbeddingError,
    EmbeddingInvalidRequestError,
    EmbeddingProviderError,
    EmbeddingTimeoutError,
    _sanitize_message,
)
from app.ai.embeddings.models import EmbeddingRequest, EmbeddingResponse
from app.ai.embeddings.providers.openai_provider import OpenAIEmbeddingProvider
from app.ai.embeddings.service import EmbeddingService


# ------------------------------------------------------------------------------
# 1. EMBEDDING MODEL & REQUEST VALIDATION TESTS
# ------------------------------------------------------------------------------

def test_embedding_request_validation():
    """Verify EmbeddingRequest enforces non-empty texts list."""
    req = EmbeddingRequest(texts=["NovaMart sales summary"])
    assert len(req.texts) == 1
    assert req.texts[0] == "NovaMart sales summary"

    with pytest.raises(ValueError, match="texts list cannot be empty"):
        EmbeddingRequest(texts=[])


def test_embedding_secret_sanitization():
    """Verify API keys and Bearer tokens are redacted from embedding error messages."""
    raw_error = "OpenAI Embedding failed using key sk-proj-1234567890abcdef and Bearer token eyJhbGciOiJIUzI1NiJ9"
    sanitized = _sanitize_message(raw_error)

    assert "sk-proj-1234567890abcdef" not in sanitized
    assert "[REDACTED_API_KEY]" in sanitized
    assert "Bearer [REDACTED_TOKEN]" in sanitized


# ------------------------------------------------------------------------------
# 2. MOCKED OPENAI EMBEDDING PROVIDER TESTS
# ------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_openai_embedding_provider_success():
    """Test successful embedding generation using mocked AsyncOpenAI client."""
    mock_async_client = MagicMock()
    mock_item1 = MagicMock()
    mock_item1.index = 0
    mock_item1.embedding = [0.1] * 1536

    mock_item2 = MagicMock()
    mock_item2.index = 1
    mock_item2.embedding = [0.2] * 1536

    mock_usage = MagicMock()
    mock_usage.prompt_tokens = 25
    mock_usage.total_tokens = 25

    mock_resp = MagicMock()
    mock_resp.data = [mock_item1, mock_item2]
    mock_resp.model = "text-embedding-3-small"
    mock_resp.usage = mock_usage

    mock_async_client.embeddings.create = AsyncMock(return_value=mock_resp)

    provider = OpenAIEmbeddingProvider(api_key="sk-test-key-1234567890", client=mock_async_client)
    req = EmbeddingRequest(texts=["Chunk 1", "Chunk 2"])

    response = await provider.generate_embeddings(req)

    assert response.provider == "openai"
    assert response.dimension == 1536
    assert len(response.embeddings) == 2
    assert response.embeddings[0][0] == 0.1
    assert response.usage.prompt_tokens == 25


@pytest.mark.asyncio
async def test_openai_embedding_error_mapping():
    """Test translation of OpenAI SDK exceptions to normalized EmbeddingError subclasses."""
    mock_async_client = MagicMock()

    # 1. Authentication Error
    mock_async_client.embeddings.create = AsyncMock(
        side_effect=openai.AuthenticationError(
            message="Invalid API Key sk-proj-1234567890abcdef",
            response=MagicMock(status_code=401),
            body=None,
        )
    )
    provider = OpenAIEmbeddingProvider(api_key="sk-test-key-1234567890", client=mock_async_client)
    req = EmbeddingRequest(texts=["Test"])

    with pytest.raises(EmbeddingAuthenticationError) as exc_info:
        await provider.generate_embeddings(req)
    assert "sk-proj-1234567890abcdef" not in str(exc_info.value)  # Sanitized

    # 2. Timeout Error
    mock_async_client.embeddings.create = AsyncMock(
        side_effect=openai.APITimeoutError(request=MagicMock())
    )
    with pytest.raises(EmbeddingTimeoutError):
        await provider.generate_embeddings(req)


# ------------------------------------------------------------------------------
# 3. EMBEDDING SERVICE ORCHESTRATION & RETRY TESTS
# ------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_embedding_service_retry_mechanism():
    """Verify EmbeddingService retries transient errors and succeeds on recovery."""
    mock_provider = MagicMock(spec=EmbeddingProvider)
    mock_provider.provider_name = "mock_provider"
    mock_provider.dimension = 1536

    mock_resp = EmbeddingResponse(
        embeddings=[[0.0] * 1536],
        model="mock-model",
        provider="mock_provider",
        dimension=1536,
    )

    # Fail once with EmbeddingProviderError, then succeed
    mock_provider.generate_embeddings = AsyncMock(
        side_effect=[EmbeddingProviderError("Transient 503"), mock_resp]
    )

    service = EmbeddingService(default_provider=mock_provider)

    with patch("asyncio.sleep", new_callable=AsyncMock):
        res = await service.embed_texts(["Sample text"])
        assert len(res) == 1
        assert len(res[0]) == 1536
        assert mock_provider.generate_embeddings.call_count == 2
