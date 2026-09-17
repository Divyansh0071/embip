"""
Pydantic Data Models for Structured LLM Communication.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class LLMMessage(BaseModel):
    """Single prompt message in a multi-turn LLM conversation."""

    role: str = Field(..., description="Role of message author: system, user, or assistant")
    content: str = Field(..., description="Text content of the message")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        valid_roles = {"system", "user", "assistant"}
        if v.lower() not in valid_roles:
            raise ValueError(f"Invalid message role '{v}'. Must be one of: {valid_roles}")
        return v.lower()

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("LLMMessage content cannot be empty or whitespace-only.")
        return v


class ResponseFormat(BaseModel):
    """Configuration for structured output generation."""

    type: str = Field(default="text", description="Output format type: text, json_object, or json_schema")
    json_schema: Optional[Dict[str, Any]] = Field(default=None, description="Optional JSON Schema specification")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        valid_types = {"text", "json_object", "json_schema"}
        if v.lower() not in valid_types:
            raise ValueError(f"Invalid response_format type '{v}'. Must be one of: {valid_types}")
        return v.lower()

    @model_validator(mode="after")
    def validate_json_schema(self) -> "ResponseFormat":
        if self.type == "json_schema" and not self.json_schema:
            raise ValueError("json_schema must be provided when response_format type is 'json_schema'.")
        return self


class LLMRequest(BaseModel):
    """Structured completion request passed to LLMService/LLMProvider."""

    messages: List[LLMMessage] = Field(..., description="Chronological prompt messages list")
    model: Optional[str] = Field(default=None, description="Override target model name")
    temperature: Optional[float] = Field(default=None, description="Sampling temperature (0.0 - 2.0)")
    max_tokens: Optional[int] = Field(default=None, description="Max token generation limit")
    timeout: Optional[float] = Field(default=None, description="Per-request timeout in seconds")
    response_format: Optional[ResponseFormat] = Field(default=None, description="Structured output configuration")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Custom request metadata/correlation tags")

    @field_validator("messages")
    @classmethod
    def validate_messages_not_empty(cls, v: List[LLMMessage]) -> List[LLMMessage]:
        if not v:
            raise ValueError("LLMRequest must contain at least one LLMMessage.")
        return v

    @field_validator("temperature")
    @classmethod
    def validate_temperature_range(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and (v < 0.0 or v > 2.0):
            raise ValueError("Temperature must be between 0.0 and 2.0.")
        return v

    @field_validator("max_tokens")
    @classmethod
    def validate_max_tokens_positive(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError("max_tokens must be greater than 0.")
        return v

    @field_validator("timeout")
    @classmethod
    def validate_timeout_positive(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("timeout must be greater than 0.")
        return v


class UsageMetadata(BaseModel):
    """Token consumption metrics for observability."""

    prompt_tokens: Optional[int] = Field(default=None, description="Input prompt tokens consumed")
    completion_tokens: Optional[int] = Field(default=None, description="Generated response tokens consumed")
    total_tokens: Optional[int] = Field(default=None, description="Total tokens consumed")


class LLMResponse(BaseModel):
    """Normalized structured response returned from LLMService/LLMProvider."""

    content: str = Field(..., description="Generated text content from LLM model")
    model: str = Field(..., description="Model identifier used for generation")
    provider: str = Field(..., description="Provider name (e.g. openai)")
    usage: Optional[UsageMetadata] = Field(default=None, description="Token usage metrics")
    finish_reason: Optional[str] = Field(default=None, description="Completion finish reason (e.g. stop, length)")
    request_duration_ms: Optional[float] = Field(default=None, description="Total execution time in milliseconds")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Echoed request or execution metadata")
