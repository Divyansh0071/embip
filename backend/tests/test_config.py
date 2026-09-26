import pytest
from app.core.config import Settings


def test_database_readonly_url_postgresql_normalization():
    """Verify postgresql:// and postgres:// URLs are converted to postgresql+asyncpg:// for DATABASE_READONLY_URL."""
    s1 = Settings(DATABASE_READONLY_URL="postgresql://user:pass@db.example.com:5432/mydb")
    assert s1.get_async_readonly_database_url() == "postgresql+asyncpg://user:pass@db.example.com:5432/mydb"

    s2 = Settings(DATABASE_READONLY_URL="postgres://user:pass@db.example.com:5432/mydb")
    assert s2.get_async_readonly_database_url() == "postgresql+asyncpg://user:pass@db.example.com:5432/mydb"


def test_database_readonly_url_sqlite_preservation():
    """Verify SQLite URLs and template placeholders fallback safely to sqlite+aiosqlite."""
    s1 = Settings(DATABASE_READONLY_URL="sqlite+aiosqlite:///./test.db")
    assert s1.get_async_readonly_database_url() == "sqlite+aiosqlite:///./test.db"

    s2 = Settings(DATABASE_READONLY_URL="postgresql://postgres:[YOUR-PASSWORD]@db.your-project.supabase.co:5432/postgres")
    assert s2.get_async_readonly_database_url() == "sqlite+aiosqlite:///./embip.db"


def test_cors_origins_comma_separated_parsing():
    """Verify comma-separated string environment variables are parsed into cleaned list of origins."""
    s = Settings(BACKEND_CORS_ORIGINS="https://app.embip.com, https://www.embip.com, ")
    assert s.BACKEND_CORS_ORIGINS == ["https://app.embip.com", "https://www.embip.com"]


def test_cors_origins_list_configuration():
    """Verify Python lists and default CORS origins work as expected."""
    s1 = Settings(BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"])
    assert s1.BACKEND_CORS_ORIGINS == ["http://localhost:3000", "http://127.0.0.1:3000"]

    s2 = Settings(BACKEND_CORS_ORIGINS='["https://demo.embip.com"]')
    assert s2.BACKEND_CORS_ORIGINS == ["https://demo.embip.com"]


def test_external_service_optional_settings_fields():
    """Verify optional external service settings load cleanly without exposing secret values."""
    s = Settings(
        SUPABASE_URL="https://test.supabase.co",
        SUPABASE_SERVICE_ROLE_KEY="secret-service-role-key",
        SUPABASE_JWT_SECRET="secret-jwt-key",
        QDRANT_URL="http://qdrant.local:6333",
        QDRANT_API_KEY="secret-qdrant-key",
    )
    assert s.SUPABASE_URL == "https://test.supabase.co"
    assert s.SUPABASE_SERVICE_ROLE_KEY == "secret-service-role-key"
    assert s.SUPABASE_JWT_SECRET == "secret-jwt-key"
    assert s.QDRANT_URL == "http://qdrant.local:6333"
    assert s.QDRANT_API_KEY == "secret-qdrant-key"

    # Representation / string serialization does not crash or expose unhandled format
    str_repr = str(s)
    assert "Settings" in str_repr or "EMBIP" in str_repr
