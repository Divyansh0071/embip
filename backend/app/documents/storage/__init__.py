"""
Document Storage Package for EMBIP.
"""

from app.documents.storage.base import DocumentStorage
from app.documents.storage.factory import get_storage_provider
from app.documents.storage.local import LocalDocumentStorage
from app.documents.storage.supabase import SupabaseDocumentStorage

__all__ = [
    "DocumentStorage",
    "LocalDocumentStorage",
    "SupabaseDocumentStorage",
    "get_storage_provider",
]
