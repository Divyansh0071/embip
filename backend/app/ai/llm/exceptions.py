"""
Normalized Application Exceptions for LLM Provider & Service Operations.
Ensures zero credential leakage in error messages returned to clients or logs.
"""


def _sanitize_message(message: str) -> str:
    """Strip any potential API keys or authorization tokens from error text."""
    if not message:
        return "An unspecified LLM error occurred."
    
    # Redact common key patterns (e.g. sk-..., bearer tokens)
    import re
    cleaned = re.sub(r"sk-[a-zA-Z0-9\-_]+", "[REDACTED_API_KEY]", str(message))
    cleaned = re.sub(r"Bearer\s+[a-zA-Z0-9\-_.]+", "Bearer [REDACTED_TOKEN]", cleaned)
    return cleaned


class LLMError(Exception):
    """Base exception class for all LLM service & provider errors."""

    def __init__(self, message: str, provider: str = "unknown"):
        self.raw_message = message
        self.clean_message = _sanitize_message(message)
        self.provider = provider
        super().__init__(self.clean_message)


class LLMConfigurationError(LLMError):
    """Raised when LLM configuration or environment settings are invalid/missing."""

    pass


class LLMAuthenticationError(LLMError):
    """Raised when provider API key is invalid, missing, or unauthorized."""

    pass


class LLMTimeoutError(LLMError):
    """Raised when LLM provider call exceeds execution timeout limits."""

    pass


class LLMRateLimitError(LLMError):
    """Raised when provider rate limit is exceeded or quota is exhausted."""

    pass


class LLMInvalidRequestError(LLMError):
    """Raised when LLM request parameters or prompt context are invalid/malformed."""

    pass


class LLMProviderError(LLMError):
    """Raised when an internal server error (5xx) occurs on the provider side."""

    pass
