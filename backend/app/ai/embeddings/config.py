"""
Environment-based Configuration for Embedding Service & Providers.
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EmbeddingSettings(BaseSettings):
    """Pydantic configuration model for Embedding Service."""

    EMBEDDING_PROVIDER: str = Field(default="openai", description="Default embedding provider (openai)")
    EMBEDDING_MODEL: str = Field(default="text-embedding-3-small", description="Target embedding model name")
    EMBEDDING_DIMENSION: int = Field(default=1536, description="Embedding vector dimension size")
    EMBEDDING_TIMEOUT_SECONDS: float = Field(default=30.0, description="Per-request embedding timeout in seconds")
    EMBEDDING_MAX_RETRIES: int = Field(default=3, description="Max retries for transient embedding errors")

    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API secret key")

    model_config = SettingsConfigDict(
        env_file=(".env.local", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def is_configured(self) -> bool:
        """Check if provider API key is set and valid."""
        if not self.OPENAI_API_KEY:
            return False
        key = self.OPENAI_API_KEY.strip()
        if not key or "your-openai-api-key" in key or key == "sk-proj-placeholder":
            return False
        return True


embedding_config = EmbeddingSettings()
