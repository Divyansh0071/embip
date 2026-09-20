from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "EMBIP Backend Engine"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./embip.db"
    DATABASE_READONLY_URL: str = "sqlite+aiosqlite:///./embip.db"

    # SQL Execution Safety
    SQL_STATEMENT_TIMEOUT_SECONDS: float = 10.0
    SQL_MAX_ROWS: int = 500
    SQL_MAX_RESULT_BYTES: int = 5_000_000
    SQL_MAX_QUERY_LENGTH: int = 2000
    SQL_MAX_RETRIES: int = 1


    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    model_config = SettingsConfigDict(
        env_file=(".env.local", ".env"),
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


settings = Settings()
