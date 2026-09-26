from typing import List, Optional, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "EMBIP Backend Engine"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./embip.db"
    DATABASE_READONLY_URL: str = "sqlite+aiosqlite:///./embip.db"

    # External Services Configuration
    SUPABASE_URL: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    SUPABASE_JWT_SECRET: Optional[str] = None
    QDRANT_URL: Optional[str] = None
    QDRANT_API_KEY: Optional[str] = None

    # Rate Limiting Configuration
    RATE_LIMIT_ENABLED: bool = True
    REDIS_URL: Optional[str] = None
    RATE_LIMIT_ASK_PER_MINUTE: int = 10
    RATE_LIMIT_SQL_PER_MINUTE: int = 20
    RATE_LIMIT_UPLOAD_PER_MINUTE: int = 10
    RATE_LIMIT_SEARCH_PER_MINUTE: int = 30
    RATE_LIMIT_DOWNLOAD_PER_MINUTE: int = 30
    RATE_LIMIT_HEALTH_PER_MINUTE: int = 60

    # SQL Execution Safety
    SQL_STATEMENT_TIMEOUT_SECONDS: float = 10.0
    SQL_MAX_ROWS: int = 500
    SQL_MAX_RESULT_BYTES: int = 5_000_000
    SQL_MAX_QUERY_LENGTH: int = 2000
    SQL_MAX_RETRIES: int = 1

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    v = json.loads(v)
                except Exception:
                    v = v.strip("[]").split(",")
            else:
                v = v.split(",")
        if isinstance(v, list):
            return [str(origin).strip() for origin in v if str(origin).strip()]
        return []

    model_config = SettingsConfigDict(
        env_file=(".env.local", ".env", "../.env.local", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def get_async_database_url(self) -> str:
        """Returns normalized async database URL."""
        url = self.DATABASE_URL
        if "[YOUR-PASSWORD]" in url or "your-project" in url:
            # Fallback to local SQLite for testing/development if credentials are template placeholders
            return "sqlite+aiosqlite:///./embip.db"

        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)

        return url

    def get_async_readonly_database_url(self) -> str:
        """Returns normalized async read-only database URL."""
        url = self.DATABASE_READONLY_URL
        if "[YOUR-PASSWORD]" in url or "your-project" in url:
            # Fallback to local SQLite for testing/development if credentials are template placeholders
            return "sqlite+aiosqlite:///./embip.db"

        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)

        return url


settings = Settings()
