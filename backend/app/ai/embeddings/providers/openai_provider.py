"""
Concrete OpenAI Embedding Provider Implementation.
All OpenAI SDK embedding imports are strictly isolated within this module.
"""

from typing import Optional
import openai
from openai import AsyncOpenAI

from app.ai.embeddings.base import EmbeddingProvider
from app.ai.embeddings.config import embedding_config
from app.ai.embeddings.exceptions import (
    EmbeddingAuthenticationError,
    EmbeddingConfigurationError,
    EmbeddingInvalidRequestError,
    EmbeddingProviderError,
    EmbeddingTimeoutError,
)
from app.ai.embeddings.models import EmbeddingRequest, EmbeddingResponse, EmbeddingUsage


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """
    OpenAI Embedding Provider using official AsyncOpenAI SDK.
    Supports text-embedding-3-small (1536 dim) and text-embedding-3-large (3072 dim).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        dimension: Optional[int] = None,
        client: Optional[AsyncOpenAI] = None,
    ):
        self._api_key = api_key or embedding_config.OPENAI_API_KEY
        self.default_model = model or embedding_config.EMBEDDING_MODEL
        self._dimension = dimension or embedding_config.EMBEDDING_DIMENSION
        self.client = client

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def dimension(self) -> int:
        return self._dimension

    def _ensure_client(self) -> AsyncOpenAI:
        if self.client:
            return self.client

        if not self._api_key or "your-openai-api-key" in self._api_key or self._api_key == "sk-proj-placeholder":
            raise EmbeddingConfigurationError(
                "OpenAI API key is missing or unconfigured. Set OPENAI_API_KEY in environment.",
                provider=self.provider_name,
            )

        self.client = AsyncOpenAI(api_key=self._api_key, timeout=embedding_config.EMBEDDING_TIMEOUT_SECONDS)
        return self.client

    async def generate_embeddings(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """
        Executes text embedding generation against OpenAI API.
        """
        async_client = self._ensure_client()
        model_name = request.model or self.default_model

        # Filter and sanitize empty strings to prevent OpenAI API errors
        inputs = [t if t and t.strip() else " " for t in request.texts]

        try:
            raw_response = await async_client.embeddings.create(
                input=inputs,
                model=model_name,
            )

            # Sort vectors by index to preserve input list ordering
            sorted_data = sorted(raw_response.data, key=lambda x: x.index)
            embeddings = [item.embedding for item in sorted_data]

            detected_dim = len(embeddings[0]) if embeddings else self._dimension

            usage_meta = None
            if raw_response.usage:
                usage_meta = EmbeddingUsage(
                    prompt_tokens=raw_response.usage.prompt_tokens,
                    total_tokens=raw_response.usage.total_tokens,
                )

            return EmbeddingResponse(
                embeddings=embeddings,
                model=raw_response.model or model_name,
                provider=self.provider_name,
                dimension=detected_dim,
                usage=usage_meta,
            )

        except openai.AuthenticationError as e:
            raise EmbeddingAuthenticationError(f"OpenAI API Key invalid or unauthorized: {str(e)}", provider=self.provider_name) from e
        except openai.APITimeoutError as e:
            raise EmbeddingTimeoutError(f"OpenAI embedding call timed out: {str(e)}", provider=self.provider_name) from e
        except openai.BadRequestError as e:
            raise EmbeddingInvalidRequestError(f"OpenAI bad request: {str(e)}", provider=self.provider_name) from e
        except openai.InternalServerError as e:
            raise EmbeddingProviderError(f"OpenAI internal server error: {str(e)}", provider=self.provider_name) from e
        except Exception as e:
            raise EmbeddingProviderError(f"Unexpected OpenAI embedding error: {str(e)}", provider=self.provider_name) from e
