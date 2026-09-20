"""
Environment-based Configuration for Vector Database / Qdrant Integration.
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class VectorStoreSettings(BaseSettings):
    """Pydantic configuration settings for Qdrant Vector DB."""

    QDRANT_URL: str = Field(default="http://localhost:6333", description="Qdrant server/cluster URL")
    QDRANT_API_KEY: Optional[str] = Field(default=None, description="Qdrant Cloud API Key")
    QDRANT_COLLECTION: str = Field(default="embip_document_chunks", description="Default vector collection name")
    QDRANT_TIMEOUT_SECONDS: float = Field(default=30.0, description="Per-request Qdrant connection timeout")

    model_config = SettingsConfigDict(
        env_file=(".env.local", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def is_cloud(self) -> bool:
        """Check if configured for remote Qdrant Cloud."""
        return bool(self.QDRANT_API_KEY and "your-" not in self.QDRANT_API_KEY)


vectorstore_config = VectorStoreSettings()
