"""
Normalized Application Exceptions for Embedding Service & Providers.
Ensures zero credential leakage in error messages returned to clients or logs.
"""

import re


def _sanitize_message(message: str) -> str:
    """Strip any potential API keys or authorization tokens from error text."""
    if not message:
        return "An unspecified embedding error occurred."

    cleaned = re.sub(r"sk-[a-zA-Z0-9\-_]+", "[REDACTED_API_KEY]", str(message))
    cleaned = re.sub(r"Bearer\s+[a-zA-Z0-9\-_.]+", "Bearer [REDACTED_TOKEN]", cleaned)
    return cleaned


class EmbeddingError(Exception):
    """Base exception class for all embedding provider and service errors."""

    def __init__(self, message: str, provider: str = "unknown"):
        self.raw_message = message
        self.clean_message = _sanitize_message(message)
        self.provider = provider
        super().__init__(self.clean_message)


class EmbeddingConfigurationError(EmbeddingError):
    """Raised when embedding configuration or environment settings are invalid/missing."""
    pass


class EmbeddingAuthenticationError(EmbeddingError):
    """Raised when provider API key is invalid, missing, or unauthorized."""
    pass


class EmbeddingTimeoutError(EmbeddingError):
    """Raised when embedding provider call exceeds execution timeout limits."""
    pass


class EmbeddingProviderError(EmbeddingError):
    """Raised when an internal server error or API failure occurs on the provider side."""
    pass


class EmbeddingInvalidRequestError(EmbeddingError):
    """Raised when embedding request parameters or input texts are malformed/invalid."""
    pass
