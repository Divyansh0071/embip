"""
Unit & Integration Test Suite for Centralized LLM Service & Provider Abstraction.
IMPORTANT: All external LLM provider calls are 100% mocked. ZERO paid API calls made.
"""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest
import openai
from fastapi.testclient import TestClient

from app.ai.llm.base import LLMProvider
from app.ai.llm.config import LLMSettings, llm_config
from app.ai.llm.exceptions import (
    LLMAuthenticationError,
    LLMConfigurationError,
    LLMError,
    LLMInvalidRequestError,
    LLMProviderError,
    LLMRateLimitError,
    LLMTimeoutError,
    _sanitize_message,
)
from app.ai.llm.models import (
    LLMMessage,
    LLMRequest,
    LLMResponse,
    ResponseFormat,
    UsageMetadata,
)
from app.ai.llm.providers.openai_provider import OpenAIProvider
from app.ai.llm.service import LLMService
import jwt
from app.main import app

client = TestClient(app)


# ------------------------------------------------------------------------------
# 1. MESSAGE & REQUEST MODEL VALIDATION TESTS
# ------------------------------------------------------------------------------

def test_llm_message_validation():
    """Test message role and content validation rules."""
    # Valid messages
    msg_sys = LLMMessage(role="system", content="You are a helpful assistant.")
    msg_user = LLMMessage(role="user", content="Hello!")
    msg_assistant = LLMMessage(role="assistant", content="Hi there!")
    assert msg_sys.role == "system"
    assert msg_user.content == "Hello!"

    # Invalid role
    with pytest.raises(ValueError, match="Invalid message role"):
        LLMMessage(role="invalid_role", content="Test")

    # Empty content
    with pytest.raises(ValueError, match="cannot be empty"):
        LLMMessage(role="user", content="   ")


def test_llm_request_validation():
    """Test LLMRequest boundary constraints and field defaults."""
    messages = [LLMMessage(role="user", content="Analyze sales trends.")]
    
    # Valid request
    req = LLMRequest(messages=messages, temperature=0.7, max_tokens=1000)
    assert len(req.messages) == 1
    assert req.temperature == 0.7

    # Empty messages list
    with pytest.raises(ValueError, match="at least one LLMMessage"):
        LLMRequest(messages=[])

    # Out of bounds temperature
    with pytest.raises(ValueError, match="Temperature must be between"):
        LLMRequest(messages=messages, temperature=2.5)

    # Invalid max_tokens
    with pytest.raises(ValueError, match="max_tokens must be greater than 0"):
        LLMRequest(messages=messages, max_tokens=-10)

    # Invalid timeout
    with pytest.raises(ValueError, match="timeout must be greater than 0"):
        LLMRequest(messages=messages, timeout=0)


def test_response_format_json_schema_validation():
    """Verify ResponseFormat validation for json_schema requirement."""
    # 1. json_schema type without a schema is rejected
    with pytest.raises(ValueError, match="json_schema must be provided"):
        ResponseFormat(type="json_schema")

    # 2. json_schema type with a schema is accepted
    schema = {"type": "object", "properties": {"summary": {"type": "string"}}}
    rf_schema = ResponseFormat(type="json_schema", json_schema=schema)
    assert rf_schema.type == "json_schema"
    assert rf_schema.json_schema == schema

    # 3. text and json_object formats allow None json_schema
    rf_text = ResponseFormat(type="text")
    rf_json_obj = ResponseFormat(type="json_object")
    assert rf_text.json_schema is None
    assert rf_json_obj.json_schema is None


# ------------------------------------------------------------------------------
# 2. SANITIZATION & SECURITY TESTS
# ------------------------------------------------------------------------------

def test_error_sanitization():
    """Verify secrets and API keys are redacted from error messages."""
    raw_error = "OpenAI API error using key sk-proj-1234567890abcdef1234567890abcdef and Bearer eyJhbGciOiJIUzI1NiJ9.test"
    sanitized = _sanitize_message(raw_error)
    assert "sk-proj-1234567890abcdef1234567890abcdef" not in sanitized
    assert "[REDACTED_API_KEY]" in sanitized
    assert "Bearer [REDACTED_TOKEN]" in sanitized


# ------------------------------------------------------------------------------
# 3. MOCKED OPENAI PROVIDER TESTS
# ------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_openai_provider_success():
    """Test successful generation using mocked AsyncOpenAI client."""
    mock_async_client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Total 2025 revenue was $758.11M."
    mock_choice.finish_reason = "stop"

    mock_usage = MagicMock()
    mock_usage.prompt_tokens = 45
    mock_usage.completion_tokens = 15
    mock_usage.total_tokens = 60

    mock_raw_resp = MagicMock()
    mock_raw_resp.choices = [mock_choice]
    mock_raw_resp.model = "gpt-4o"
    mock_raw_resp.usage = mock_usage

    mock_async_client.chat.completions.create = AsyncMock(return_value=mock_raw_resp)

    provider = OpenAIProvider(api_key="sk-proj-testkey", client=mock_async_client)
    req = LLMRequest(messages=[LLMMessage(role="user", content="Query total revenue.")])

    response = await provider.generate(req)
    assert response.content == "Total 2025 revenue was $758.11M."
    assert response.model == "gpt-4o"
    assert response.provider == "openai"
    assert response.usage.total_tokens == 60
    assert response.finish_reason == "stop"


@pytest.mark.asyncio
async def test_openai_provider_structured_output():
    """Test JSON structured output request format translation."""
    mock_async_client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = '{"revenue": 1000}'
    mock_choice.finish_reason = "stop"
    mock_raw_resp = MagicMock()
    mock_raw_resp.choices = [mock_choice]
    mock_raw_resp.model = "gpt-4o"
    mock_raw_resp.usage = None

    mock_create = AsyncMock(return_value=mock_raw_resp)
    mock_async_client.chat.completions.create = mock_create

    provider = OpenAIProvider(api_key="sk-proj-testkey", client=mock_async_client)
    req = LLMRequest(
        messages=[LLMMessage(role="user", content="Get JSON")],
        response_format=ResponseFormat(type="json_object"),
    )

    response = await provider.generate(req)
    assert response.content == '{"revenue": 1000}'
    
    # Assert response_format kwarg was passed to OpenAI SDK call
    _, kwargs = mock_create.call_args
    assert kwargs["response_format"] == {"type": "json_object"}


@pytest.mark.asyncio
async def test_openai_provider_error_mapping():
    """Test translation of OpenAI SDK exceptions to normalized application exceptions."""
    mock_async_client = MagicMock()
    
    # 1. Authentication Error
    mock_async_client.chat.completions.create = AsyncMock(
        side_effect=openai.AuthenticationError(
            message="Invalid API Key sk-proj-12345",
            response=MagicMock(status_code=401),
            body=None,
        )
    )
    provider = OpenAIProvider(api_key="sk-proj-testkey", client=mock_async_client)
    req = LLMRequest(messages=[LLMMessage(role="user", content="Hi")])

    with pytest.raises(LLMAuthenticationError) as exc_info:
        await provider.generate(req)
    assert "sk-proj-12345" not in str(exc_info.value)  # Sanitized

    # 2. Timeout Error
    mock_async_client.chat.completions.create = AsyncMock(
        side_effect=openai.APITimeoutError(request=MagicMock())
    )
    with pytest.raises(LLMTimeoutError):
        await provider.generate(req)

    # 3. Rate Limit Error
    mock_async_client.chat.completions.create = AsyncMock(
        side_effect=openai.RateLimitError(
            message="Rate limit exceeded",
            response=MagicMock(status_code=429),
            body=None,
        )
    )
    with pytest.raises(LLMRateLimitError):
        await provider.generate(req)


# ------------------------------------------------------------------------------
# 4. LLM SERVICE ORCHESTRATION & RETRY TESTS
# ------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_llm_service_provider_selection():
    """Test LLMService registering custom provider and selecting default."""
    class CustomProvider(LLMProvider):
        @property
        def provider_name(self) -> str:
            return "custom_mock"
        
        async def generate(self, request: LLMRequest) -> LLMResponse:
            return LLMResponse(content="Custom reply", model="custom-1", provider="custom_mock")

    service = LLMService()
    service.register_provider(CustomProvider())

    prov = service.get_provider("custom_mock")
    assert prov.provider_name == "custom_mock"

    # Test unknown provider raises LLMConfigurationError
    with pytest.raises(LLMConfigurationError, match="not registered"):
        service.get_provider("non_existent_provider")


@pytest.mark.asyncio
async def test_llm_service_retry_transient_failures():
    """Test retry behavior: retries transient errors up to max_retries."""
    mock_provider = MagicMock()
    mock_provider.provider_name = "openai"

    # First 2 attempts raise LLMTimeoutError, 3rd attempt succeeds
    mock_provider.generate = AsyncMock(
        side_effect=[
            LLMTimeoutError("Timed out", provider="openai"),
            LLMTimeoutError("Timed out again", provider="openai"),
            LLMResponse(content="Success after retries", model="gpt-4o", provider="openai"),
        ]
    )

    service = LLMService(providers={"openai": mock_provider})
    req = LLMRequest(messages=[LLMMessage(role="user", content="Retry test")])

    with patch("asyncio.sleep", new_callable=AsyncMock):  # Fast forward retry delays
        res = await service.generate(req, provider_name="openai")

    assert res.content == "Success after retries"
    assert mock_provider.generate.call_count == 3


@pytest.mark.asyncio
async def test_llm_service_no_retry_on_auth_failure():
    """Test that non-transient auth errors do NOT trigger retries."""
    mock_provider = MagicMock()
    mock_provider.provider_name = "openai"
    mock_provider.generate = AsyncMock(
        side_effect=LLMAuthenticationError("Invalid credentials", provider="openai")
    )

    service = LLMService(providers={"openai": mock_provider})
    req = LLMRequest(messages=[LLMMessage(role="user", content="Auth test")])

    with pytest.raises(LLMAuthenticationError):
        await service.generate(req, provider_name="openai")

    # Verify attempt count is exactly 1 (no retries)
    assert mock_provider.generate.call_count == 1


# ------------------------------------------------------------------------------
# 5. DIAGNOSTICS & HEALTH API ENDPOINT TESTS
# ------------------------------------------------------------------------------

def test_llm_status_endpoint_unauthenticated():
    """Verify GET /api/v1/llm/status requires authentication (401)."""
    response = client.get("/api/v1/llm/status")
    assert response.status_code == 401


def test_llm_status_endpoint_authenticated():
    """Verify GET /api/v1/llm/status returns safe diagnostics for authenticated user."""
    payload = {
        "sub": "00000000-0000-4000-a000-000000000003",
        "email": "test@novamart.com",
        "user_metadata": {"role": "Analyst", "workspace_id": "00000000-0000-4000-a000-000000000002"},
    }
    token = jwt.encode(payload, "secret-key", algorithm="HS256")

    response = client.get(
        "/api/v1/llm/status",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "provider" in data
    assert "api_key_configured" in data
    assert "registered_providers" in data
    # Ensure no secret key is exposed in API response
    assert "OPENAI_API_KEY" not in data
    assert "sk-proj" not in str(data)

