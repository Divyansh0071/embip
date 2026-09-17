"""
Supabase Storage Adapter Hook for Production Document Storage.
Communicates with Supabase Storage REST API using authenticated user tokens or service-role keys.
"""

import os
from typing import Optional
import httpx
from app.documents.storage.base import DocumentStorage


class SupabaseDocumentStorage(DocumentStorage):
    """
    Supabase Storage Provider for production bucket deployment.
    """

    def __init__(
        self,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
        bucket_name: str = "documents",
    ):
        self.supabase_url = supabase_url or os.getenv("NEXT_PUBLIC_SUPABASE_URL", "")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        self.bucket_name = bucket_name

    def is_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_key and "your-" not in self.supabase_key)

    async def store(self, file_content: bytes, destination_path: str) -> str:
        if not self.is_configured():
            raise RuntimeError("Supabase Storage credentials are not configured in environment.")

        endpoint = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{destination_path}"
        headers = {
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/octet-stream",
            "x-upsert": "true",
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(endpoint, content=file_content, headers=headers)
            if resp.status_code not in (200, 201):
                raise RuntimeError(f"Supabase storage upload failed with HTTP {resp.status_code}: {resp.text}")

        return destination_path

    async def retrieve(self, storage_path: str) -> bytes:
        if not self.is_configured():
            raise RuntimeError("Supabase Storage credentials are not configured in environment.")

        endpoint = f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{storage_path}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(endpoint)
            if resp.status_code != 200:
                raise FileNotFoundError(f"File not found in Supabase Storage: {storage_path}")
            return resp.content

    async def delete(self, storage_path: str) -> bool:
        if not self.is_configured():
            return False

        endpoint = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{storage_path}"
        headers = {"Authorization": f"Bearer {self.supabase_key}"}

        async with httpx.AsyncClient() as client:
            resp = await client.delete(endpoint, headers=headers)
            return resp.status_code in (200, 204)

    async def exists(self, storage_path: str) -> bool:
        try:
            await self.retrieve(storage_path)
            return True
        except Exception:
            return False
