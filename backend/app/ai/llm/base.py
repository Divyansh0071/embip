"""
Abstract Base LLM Provider Interface.
Allows plugging in replacement providers (OpenAI, Azure, Anthropic, Ollama, etc.)
without changing agent or service code.
"""

from abc import ABC, abstractmethod
from app.ai.llm.models import LLMRequest, LLMResponse


class LLMProvider(ABC):
    """Abstract interface that all LLM providers must implement."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns provider identifier name (e.g. 'openai')."""
        pass

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Asynchronously execute structured LLM completion request.
        Must handle provider-specific SDK calls and translate exceptions to normalized LLMError subclasses.
        """
        pass
