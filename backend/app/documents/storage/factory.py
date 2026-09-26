"""
Storage Provider Factory for selecting document storage implementation based on environment configuration.
"""

import os
from typing import Optional
from app.documents.storage.base import DocumentStorage
from app.documents.storage.local import LocalDocumentStorage
from app.documents.storage.supabase import SupabaseDocumentStorage


def get_storage_provider(
    environment: Optional[str] = None,
    supabase_url: Optional[str] = None,
    supabase_key: Optional[str] = None,
) -> DocumentStorage:
    """
    Factory function selecting the appropriate document storage provider.
    - Development / Testing: Uses LocalDocumentStorage by default.
    - Production: Uses SupabaseDocumentStorage if configured.
      Fails clearly with RuntimeError if production storage credentials are missing.
    """
    from app.core.config import settings

    env = (environment or settings.ENVIRONMENT or "development").lower()
    url = (
        supabase_url
        or settings.SUPABASE_URL
        or os.getenv("SUPABASE_URL")
        or os.getenv("NEXT_PUBLIC_SUPABASE_URL", "")
    )
    key = (
        supabase_key
        or settings.SUPABASE_SERVICE_ROLE_KEY
        or os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    )

    if env == "production":
        provider = SupabaseDocumentStorage(supabase_url=url, supabase_key=key)
        if not provider.is_configured():
            raise RuntimeError(
                "Production document storage configuration error: "
                "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be configured when ENVIRONMENT=production."
            )
        return provider

    return LocalDocumentStorage()
