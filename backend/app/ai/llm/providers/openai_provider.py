"""
Concrete OpenAI Provider Implementation using Official OpenAI Python SDK.
IMPORTANT: All OpenAI SDK imports are isolated strictly within this module.
"""

from typing import Any, Dict, Optional
import openai
from openai import AsyncOpenAI

from app.ai.llm.base import LLMProvider
from app.ai.llm.config import llm_config
from app.ai.llm.exceptions import (
    LLMAuthenticationError,
    LLMConfigurationError,
    LLMInvalidRequestError,
    LLMProviderError,
    LLMRateLimitError,
    LLMTimeoutError,
)
from app.ai.llm.models import LLMRequest, LLMResponse, UsageMetadata


class OpenAIProvider(LLMProvider):
    """Concrete OpenAI LLM Provider."""

    def __init__(self, api_key: Optional[str] = None, client: Optional[AsyncOpenAI] = None):
        self._api_key = api_key or llm_config.OPENAI_API_KEY
        if client:
            self.client = client
        else:
            if not self._api_key or "your-openai-api-key" in self._api_key:
                # Client initialization can proceed, but generate() will check if configured
                self.client = None
            else:
                self.client = AsyncOpenAI(api_key=self._api_key, organization=llm_config.OPENAI_ORGANIZATION_ID)

    @property
    def provider_name(self) -> str:
        return "openai"

    def _ensure_client(self):
        """Lazy-initialize or validate AsyncOpenAI client."""
        if not self._api_key or "your-openai-api-key" in self._api_key or self._api_key == "sk-proj-placeholder":
            raise LLMConfigurationError(
                "OpenAI API key is missing or configured with a placeholder value.",
                provider=self.provider_name,
            )
        if not self.client:
            self.client = AsyncOpenAI(api_key=self._api_key, organization=llm_config.OPENAI_ORGANIZATION_ID)

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Asynchronously call OpenAI Chat Completions API with normalized exception handling."""
        self._ensure_client()

        model_name = request.model or llm_config.LLM_MODEL
        temperature = request.temperature if request.temperature is not None else llm_config.LLM_TEMPERATURE
        max_tokens = request.max_tokens or llm_config.LLM_MAX_TOKENS
        timeout = request.timeout or llm_config.LLM_TIMEOUT_SECONDS

        # Format messages for OpenAI API
        formatted_messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        # Format structured output option
        rf_kwarg: Optional[Dict[str, Any]] = None
        if request.response_format:
            fmt_type = request.response_format.type
            if fmt_type == "json_object":
                rf_kwarg = {"type": "json_object"}
            elif fmt_type == "json_schema" and request.response_format.json_schema:
                rf_kwarg = {
                    "type": "json_schema",
                    "json_schema": request.response_format.json_schema,
                }

        kwargs: Dict[str, Any] = {
            "model": model_name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "timeout": timeout,
        }
        if rf_kwarg:
            kwargs["response_format"] = rf_kwarg

        try:
            raw_response = await self.client.chat.completions.create(**kwargs)
        except openai.AuthenticationError as e:
            raise LLMAuthenticationError(str(e), provider=self.provider_name) from e
        except openai.APITimeoutError as e:
            raise LLMTimeoutError(f"OpenAI request timed out after {timeout} seconds.", provider=self.provider_name) from e
        except openai.RateLimitError as e:
            raise LLMRateLimitError(str(e), provider=self.provider_name) from e
        except openai.BadRequestError as e:
            raise LLMInvalidRequestError(str(e), provider=self.provider_name) from e
        except openai.InternalServerError as e:
            raise LLMProviderError(f"OpenAI server error: {str(e)}", provider=self.provider_name) from e
        except openai.OpenAIError as e:
            raise LLMProviderError(f"OpenAI API error: {str(e)}", provider=self.provider_name) from e
        except Exception as e:
            raise LLMProviderError(f"Unexpected provider execution error: {str(e)}", provider=self.provider_name) from e

        # Parse normalized response content
        choice = raw_response.choices[0]
        content = choice.message.content or ""
        finish_reason = choice.finish_reason

        # Extract usage metadata
        usage_meta = None
        if raw_response.usage:
            usage_meta = UsageMetadata(
                prompt_tokens=raw_response.usage.prompt_tokens,
                completion_tokens=raw_response.usage.completion_tokens,
                total_tokens=raw_response.usage.total_tokens,
            )

        return LLMResponse(
            content=content,
            model=raw_response.model or model_name,
            provider=self.provider_name,
            usage=usage_meta,
            finish_reason=finish_reason,
            metadata=request.metadata,
        )
