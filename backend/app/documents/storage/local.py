"""
Local Disk Document Storage Implementation with Path Traversal Protection.
"""

import os
from pathlib import Path
from typing import Optional
from app.documents.storage.base import DocumentStorage


class LocalDocumentStorage(DocumentStorage):
    """
    Local filesystem storage provider for local development & automated testing.
    Protects against directory traversal and root escaping.
    """

    def __init__(self, base_dir: Optional[str] = None):
        if base_dir:
            self.base_path = Path(base_dir).resolve()
        else:
            # Default to backend/storage/uploads
            self.base_path = Path(__file__).parent.parent.parent.parent / "storage" / "uploads"
            self.base_path = self.base_path.resolve()

        os.makedirs(self.base_path, exist_ok=True)

    def _resolve_safe_path(self, destination_path: str) -> Path:
        """
        Ensures destination_path resolves within self.base_path to prevent path traversal attacks.
        """
        # Strip leading slashes / backslashes
        cleaned = destination_path.lstrip("/\\")
        target = (self.base_path / cleaned).resolve()

        # Enforce boundary check
        try:
            target.relative_to(self.base_path)
        except ValueError:
            raise ValueError(f"Security error: Invalid path '{destination_path}' attempts directory traversal.")

        return target

    async def store(self, file_content: bytes, destination_path: str) -> str:
        target = self._resolve_safe_path(destination_path)
        os.makedirs(target.parent, exist_ok=True)

        with open(target, "wb") as f:
            f.write(file_content)

        return str(target.relative_to(self.base_path)).replace("\\", "/")

    async def retrieve(self, storage_path: str) -> bytes:
        target = self._resolve_safe_path(storage_path)
        if not target.exists():
            raise FileNotFoundError(f"Document file not found at storage path: {storage_path}")

        with open(target, "rb") as f:
            return f.read()

    async def delete(self, storage_path: str) -> bool:
        target = self._resolve_safe_path(storage_path)
        if target.exists() and target.is_file():
            os.remove(target)
            return True
        return False

    async def exists(self, storage_path: str) -> bool:
        target = self._resolve_safe_path(storage_path)
        return target.exists() and target.is_file()
