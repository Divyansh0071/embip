import pytest
from app.documents.storage.factory import get_storage_provider
from app.documents.storage.local import LocalDocumentStorage
from app.documents.storage.supabase import SupabaseDocumentStorage


def test_development_selects_local_document_storage():
    """Verify development/testing defaults to LocalDocumentStorage."""
    provider = get_storage_provider(environment="development")
    assert isinstance(provider, LocalDocumentStorage)

    provider_test = get_storage_provider(environment="testing")
    assert isinstance(provider_test, LocalDocumentStorage)


def test_production_valid_supabase_configuration():
    """Verify production with valid Supabase URL and key selects SupabaseDocumentStorage."""
    provider = get_storage_provider(
        environment="production",
        supabase_url="https://xyz123.supabase.co",
        supabase_key="sb-service-role-secret-key-value",
    )
    assert isinstance(provider, SupabaseDocumentStorage)
    assert provider.is_configured() is True
    assert provider.supabase_url == "https://xyz123.supabase.co"
    assert provider.supabase_key == "sb-service-role-secret-key-value"


def test_production_missing_credentials_fails_safely():
    """Verify production without valid storage credentials raises a descriptive configuration error without exposing secrets."""
    with pytest.raises(RuntimeError, match="Production document storage configuration error"):
        get_storage_provider(
            environment="production",
            supabase_url=None,
            supabase_key=None,
        )

    with pytest.raises(RuntimeError, match="Production document storage configuration error"):
        get_storage_provider(
            environment="production",
            supabase_url="https://xyz123.supabase.co",
            supabase_key="your-service-role-key-placeholder",
        )


@pytest.mark.asyncio
async def test_workspace_path_isolation_intact(tmp_path):
    """Verify storage path resolution enforces boundary checks and workspace prefix isolation."""
    storage = LocalDocumentStorage(base_dir=str(tmp_path))
    workspace_id = "00000000-0000-4000-a000-000000000002"
    doc_path = f"{workspace_id}/test_doc.pdf"

    # Store file content
    stored_path = await storage.store(b"%PDF-1.4 test", doc_path)
    assert stored_path.startswith(workspace_id)
    assert await storage.exists(doc_path) is True

    # Path traversal outside boundary is blocked
    with pytest.raises(ValueError, match="directory traversal"):
        storage._resolve_safe_path("../../../etc/passwd")
