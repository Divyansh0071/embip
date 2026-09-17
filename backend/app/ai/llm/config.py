"""
Environment-based Configuration for LLM Service & Providers.
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    """Pydantic configuration model for LLM Service."""

    LLM_PROVIDER: str = Field(default="openai", description="Default LLM provider (openai)")
    LLM_MODEL: str = Field(default="gpt-4o", description="Default LLM model name")
    LLM_TEMPERATURE: float = Field(default=0.0, description="Default sampling temperature")
    LLM_MAX_TOKENS: int = Field(default=4096, description="Default max output tokens")
    LLM_TIMEOUT_SECONDS: float = Field(default=30.0, description="Default per-request timeout")
    LLM_MAX_RETRIES: int = Field(default=3, description="Max retries for transient errors")

    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API secret key")
    OPENAI_ORGANIZATION_ID: Optional[str] = Field(default=None, description="Optional OpenAI Org ID")

    model_config = SettingsConfigDict(
        env_file=(".env.local", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def is_configured(self) -> bool:
        """Check if provider credentials are set and not a placeholder."""
        if not self.OPENAI_API_KEY:
            return False
        key = self.OPENAI_API_KEY.strip()
        if not key or "your-openai-api-key" in key or key == "sk-proj-placeholder":
            return False
        return True


llm_config = LLMSettings()
