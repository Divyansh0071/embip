"""
Abstract Storage Provider Interface for Document Management.
Allows switching storage backends (Local Disk, Supabase Storage, S3)
without changing ingestion or processing logic.
"""

from abc import ABC, abstractmethod
from typing import BinaryIO, Optional


class DocumentStorage(ABC):
    """Abstract file storage interface for document artifacts."""

    @abstractmethod
    async def store(self, file_content: bytes, destination_path: str) -> str:
        """
        Store raw file bytes at destination_path.
        Returns resolved storage reference path.
        """
        pass

    @abstractmethod
    async def retrieve(self, storage_path: str) -> bytes:
        """
        Retrieve raw file content bytes from storage_path.
        Raises FileNotFoundError or storage exception if path does not exist.
        """
        pass

    @abstractmethod
    async def delete(self, storage_path: str) -> bool:
        """
        Delete document file at storage_path.
        Returns True if deleted, False if file did not exist.
        """
        pass

    @abstractmethod
    async def exists(self, storage_path: str) -> bool:
        """
        Check if storage_path exists in storage backend.
        """
        pass
