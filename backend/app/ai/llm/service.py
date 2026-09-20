"""
Centralized LLM Service Orchestrator for EMBIP AI Architecture.
All AI agents interact with this service rather than direct provider SDKs.
"""

import asyncio
import logging
import time
from typing import Any, Dict, Optional

from app.ai.llm.base import LLMProvider
from app.ai.llm.config import llm_config
from app.ai.llm.exceptions import (
    LLMAuthenticationError,
    LLMConfigurationError,
    LLMError,
    LLMInvalidRequestError,
    LLMProviderError,
    LLMRateLimitError,
    LLMTimeoutError,
)
from app.ai.llm.models import LLMRequest, LLMResponse
from app.ai.llm.providers.openai_provider import OpenAIProvider

logger = logging.getLogger("embip.ai.llm")


class LLMService:
    """Centralized LLM Service handling request validation, routing, retries, and logging."""

    def __init__(self, providers: Optional[Dict[str, LLMProvider]] = None):
        self._providers: Dict[str, LLMProvider] = providers or {}
        
        # Register default OpenAI provider if not provided
        if "openai" not in self._providers:
            self._providers["openai"] = OpenAIProvider()

    def register_provider(self, provider: LLMProvider) -> None:
        """Register a new LLM provider implementation."""
        self._providers[provider.provider_name] = provider
        logger.info(f"Registered LLM Provider: '{provider.provider_name}'")

    def get_provider(self, provider_name: Optional[str] = None) -> LLMProvider:
        """Retrieve target LLM provider by name or fallback to configured default."""
        target_name = (provider_name or llm_config.LLM_PROVIDER).lower()
        provider = self._providers.get(target_name)
        if not provider:
            raise LLMConfigurationError(
                f"LLM Provider '{target_name}' is not registered. Available providers: {list(self._providers.keys())}",
                provider=target_name,
            )
        return provider

    def get_diagnostics(self) -> Dict[str, Any]:
        """
        Return safe diagnostic status of configured LLM providers.
        Does NOT make external paid API calls or leak API credentials.
        """
        configured = llm_config.is_configured()
        return {
            "status": "configured" if configured else "unconfigured",
            "provider": llm_config.LLM_PROVIDER,
            "default_model": llm_config.LLM_MODEL,
            "api_key_configured": configured,
            "registered_providers": list(self._providers.keys()),
            "max_retries": llm_config.LLM_MAX_RETRIES,
            "timeout_seconds": llm_config.LLM_TIMEOUT_SECONDS,
        }

    async def generate(self, request: LLMRequest, provider_name: Optional[str] = None) -> LLMResponse:
        """
        Asynchronously generate LLM completion with validation, safe retries, and timing metrics.
        """
        provider = self.get_provider(provider_name)
        max_retries = llm_config.LLM_MAX_RETRIES
        start_time = time.perf_counter()

        attempt = 0
        last_exception: Optional[LLMError] = None

        while attempt <= max_retries:
            attempt += 1
            try:
                logger.debug(
                    f"Executing LLM request (Attempt {attempt}/{max_retries + 1}) "
                    f"using provider='{provider.provider_name}', model='{request.model or llm_config.LLM_MODEL}'"
                )

                response = await provider.generate(request)
                
                # Record duration
                duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
                response.request_duration_ms = duration_ms

                # Safe observational logging (never log prompts or credentials)
                tokens_info = f"tokens={response.usage.total_tokens}" if response.usage else "tokens=N/A"
                logger.info(
                    f"LLM Call Success | provider='{response.provider}' model='{response.model}' "
                    f"duration={duration_ms}ms {tokens_info} retries={attempt - 1}"
                )
                return response

            except (LLMAuthenticationError, LLMConfigurationError, LLMInvalidRequestError) as non_transient_err:
                # Do NOT retry non-transient configuration/auth/request errors
                duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
                logger.error(
                    f"LLM Call Failed (Non-Transient) | provider='{provider.provider_name}' "
                    f"error='{non_transient_err.clean_message}' duration={duration_ms}ms"
                )
                raise non_transient_err

            except (LLMTimeoutError, LLMRateLimitError, LLMProviderError) as transient_err:
                last_exception = transient_err
                duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
                logger.warning(
                    f"LLM Call Transient Failure (Attempt {attempt}/{max_retries + 1}) | "
                    f"provider='{provider.provider_name}' error='{transient_err.clean_message}' duration={duration_ms}ms"
                )

                if attempt > max_retries:
                    break

                # Exponential backoff: 0.5s, 1.0s, 2.0s
                backoff_delay = 0.5 * (2 ** (attempt - 1))
                await asyncio.sleep(backoff_delay)

        # If retries exhausted
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        error_msg = f"LLM request failed after {max_retries + 1} attempts. Last error: {last_exception.clean_message if last_exception else 'Unknown'}"
        logger.error(f"LLM Call Exhausted Retries | provider='{provider.provider_name}' duration={duration_ms}ms")
        raise last_exception or LLMProviderError(error_msg, provider=provider.provider_name)

    async def generate_structured(self, request: LLMRequest, schema_cls: Any, provider_name: Optional[str] = None) -> Any:
        """
        Generates LLM completion and parses output using schema_cls.model_validate_json.
        """
        response = await self.generate(request, provider_name=provider_name)
        text_content = response.content.strip()
        if text_content.startswith("```"):
            lines = text_content.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text_content = "\n".join(lines).strip()
        return schema_cls.model_validate_json(text_content)


# Global Singleton LLMService Instance
llm_service = LLMService()
