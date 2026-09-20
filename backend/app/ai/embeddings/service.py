"""
Centralized Embedding Service Orchestrator for EMBIP AI Architecture.
All AI components interact with this service for text vectorization.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional

from app.ai.embeddings.base import EmbeddingProvider
from app.ai.embeddings.config import embedding_config
from app.ai.embeddings.exceptions import (
    EmbeddingAuthenticationError,
    EmbeddingConfigurationError,
    EmbeddingError,
    EmbeddingInvalidRequestError,
    EmbeddingProviderError,
    EmbeddingTimeoutError,
)
from app.ai.embeddings.models import EmbeddingRequest, EmbeddingResponse
from app.ai.embeddings.providers.openai_provider import OpenAIEmbeddingProvider

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Centralized Embedding Service managing provider selection, validation, retries, and observability.
    """

    def __init__(self, default_provider: Optional[EmbeddingProvider] = None):
        self._providers: Dict[str, EmbeddingProvider] = {}
        if default_provider:
            self.default_provider_name = default_provider.provider_name.lower()
            self.register_provider(default_provider)
        else:
            self.default_provider_name = embedding_config.EMBEDDING_PROVIDER.lower()
            self.register_provider(OpenAIEmbeddingProvider())

    def register_provider(self, provider: EmbeddingProvider) -> None:
        """Register custom or built-in embedding provider."""
        self._providers[provider.provider_name.lower()] = provider

    def get_provider(self, provider_name: Optional[str] = None) -> EmbeddingProvider:
        """Resolve requested or default registered provider."""
        target_name = (provider_name or self.default_provider_name).lower()
        provider = self._providers.get(target_name)
        if not provider:
            raise EmbeddingConfigurationError(
                f"Embedding provider '{target_name}' is not registered. Available: {list(self._providers.keys())}"
            )
        return provider

    @property
    def dimension(self) -> int:
        """Returns vector dimension of default configured provider."""
        return self.get_provider().dimension

    async def generate_embeddings(
        self,
        request: EmbeddingRequest,
        provider_name: Optional[str] = None,
    ) -> EmbeddingResponse:
        """
        Executes embedding generation request with retries and exponential backoff.
        """
        provider = self.get_provider(provider_name)
        max_retries = embedding_config.EMBEDDING_MAX_RETRIES
        start_time = time.time()

        if not request.texts:
            raise EmbeddingInvalidRequestError("Embedding request must contain at least one text string.")

        last_exception: Optional[Exception] = None

        for attempt in range(1, max_retries + 1):
            try:
                response = await provider.generate_embeddings(request)
                duration_ms = (time.time() - start_time) * 1000

                logger.info(
                    f"Embedding Success | provider='{provider.provider_name}' "
                    f"count={len(response.embeddings)} dim={response.dimension} duration={duration_ms:.1f}ms"
                )
                return response

            except (EmbeddingAuthenticationError, EmbeddingConfigurationError, EmbeddingInvalidRequestError) as e:
                # Non-transient errors fail immediately without retry
                logger.error(f"Embedding Hard Failure | provider='{provider.provider_name}' error='{str(e)}'")
                raise e

            except (EmbeddingTimeoutError, EmbeddingProviderError) as e:
                last_exception = e
                duration_ms = (time.time() - start_time) * 1000
                logger.warning(
                    f"Embedding Transient Failure (Attempt {attempt}/{max_retries}) | "
                    f"provider='{provider.provider_name}' error='{str(e)}'"
                )

                if attempt > max_retries:
                    break

                backoff_delay = 0.5 * (2 ** (attempt - 1))
                await asyncio.sleep(backoff_delay)

        duration_ms = (time.time() - start_time) * 1000
        error_msg = f"Embedding service exhausted all {max_retries} retries. Last error: {str(last_exception)}"
        logger.error(f"Embedding Retries Exhausted | provider='{provider.provider_name}' duration={duration_ms:.1f}ms")
        raise last_exception or EmbeddingProviderError(error_msg, provider=provider.provider_name)

    async def embed_texts(self, texts: List[str], provider_name: Optional[str] = None) -> List[List[float]]:
        """
        Helper method to vectorise a batch of strings.
        Returns list of float vectors.
        """
        request = EmbeddingRequest(texts=texts)
        response = await self.generate_embeddings(request, provider_name=provider_name)
        return response.embeddings

    async def embed_query(self, text: str, provider_name: Optional[str] = None) -> List[float]:
        """
        Helper method to vectorise a single search query string.
        Returns single float vector.
        """
        vectors = await self.embed_texts([text], provider_name=provider_name)
        return vectors[0]


# Global Singleton Instance
embedding_service = EmbeddingService()
