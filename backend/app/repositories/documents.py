from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.documents import Document, DocumentChunk
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    """Async repository for tenant-isolated Document operations."""

    def __init__(self, session):
        super().__init__(Document, session)

    async def get_by_workspace(
        self, workspace_id: str, limit: int = 100, offset: int = 0, status: Optional[str] = None
    ) -> List[Document]:
        query = select(Document).where(Document.workspace_id == workspace_id)
        if status:
            query = query.where(Document.status == status.lower())
        query = query.order_by(Document.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id_and_workspace(
        self, document_id: str, workspace_id: str
    ) -> Optional[Document]:
        query = (
            select(Document)
            .options(selectinload(Document.chunks))
            .where(Document.id == document_id, Document.workspace_id == workspace_id)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def delete_by_id_and_workspace(
        self, document_id: str, workspace_id: str
    ) -> bool:
        doc = await self.get_by_id_and_workspace(document_id, workspace_id)
        if doc:
            await self.session.delete(doc)
            await self.session.flush()
            return True
        return False


class DocumentChunkRepository(BaseRepository[DocumentChunk]):
    """Async repository for DocumentChunk operations."""

    def __init__(self, session):
        super().__init__(DocumentChunk, session)

    async def get_chunks_by_document(self, document_id: str) -> List[DocumentChunk]:
        query = (
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index.asc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def bulk_create_chunks(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        self.session.add_all(chunks)
        await self.session.flush()
        return chunks
