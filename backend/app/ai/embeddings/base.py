"""
Abstract Base Embedding Provider Interface.
Allows plugging in replacement embedding providers (OpenAI, Cohere, HuggingFace, Local vLLM/Ollama, etc.)
without modifying application logic.
"""

from abc import ABC, abstractmethod
from typing import List
from app.ai.embeddings.models import EmbeddingRequest, EmbeddingResponse


class EmbeddingProvider(ABC):
    """Abstract interface that all embedding providers must implement."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns provider identifier name (e.g. 'openai')."""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Returns default vector dimension size."""
        pass

    @abstractmethod
    async def generate_embeddings(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """
        Asynchronously execute batch text embedding request.
        Must handle provider-specific SDK calls and translate exceptions to EmbeddingError subclasses.
        """
        pass
