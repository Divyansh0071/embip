"""
Document Processing Orchestrator Service for EMBIP.
Handles the complete document lifecycle:
Validation -> Storage -> Extraction -> Cleaning -> Chunking -> DB Persistence -> Embedding -> Qdrant Upsert.
Uses lowercase status values ('uploaded', 'processing', 'processed', 'failed').
"""

import hashlib
import logging
import uuid
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.embeddings.service import EmbeddingService, embedding_service
from app.ai.vectorstore.service import VectorStoreService, vectorstore_service
from app.documents.extractors import get_extractor_for_file_type
from app.documents.processing.cleaner import TextCleaner
from app.documents.processing.chunker import TextChunker
from app.documents.processing.validator import DocumentValidationError, DocumentValidator
from app.documents.storage.base import DocumentStorage
from app.documents.storage.local import LocalDocumentStorage
from app.models.documents import Document, DocumentChunk
from app.repositories.documents import DocumentChunkRepository, DocumentRepository

logger = logging.getLogger(__name__)


class DocumentProcessingService:
    """
    Service managing document ingestion, extraction, text cleaning, chunking, embedding, vector indexing, and DB persistence.
    """

    def __init__(
        self,
        session: AsyncSession,
        storage_provider: Optional[DocumentStorage] = None,
        emb_service: Optional[EmbeddingService] = None,
        vec_service: Optional[VectorStoreService] = None,
    ):
        self.session = session
        self.doc_repo = DocumentRepository(session)
        self.chunk_repo = DocumentChunkRepository(session)
        self.storage = storage_provider or LocalDocumentStorage()
        self.chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
        self.embedding_service = emb_service or embedding_service
        self.vectorstore_service = vec_service or vectorstore_service

    async def process_document_upload(
        self,
        file_bytes: bytes,
        original_filename: str,
        declared_mime: str,
        workspace_id: str,
        uploaded_by: str,
        org_id: Optional[str] = None,
    ) -> Document:
        """
        Executes end-to-end document ingestion flow including text extraction, chunking, embedding, and vector indexing.

        Returns Document model instance.
        """
        # 1. Validate file
        sanitized_name, file_type, validated_mime = DocumentValidator.validate_file(
            filename=original_filename,
            file_bytes=file_bytes,
            declared_mime=declared_mime,
        )

        # 2. Compute SHA-256 checksum
        checksum = hashlib.sha256(file_bytes).hexdigest()

        # 3. Store raw file bytes
        doc_uuid = str(uuid.uuid4())
        relative_storage_path = f"{workspace_id}/{doc_uuid}_{sanitized_name}"
        stored_path = await self.storage.store(file_bytes, relative_storage_path)

        # 4. Create initial Document DB record with status 'processing'
        document = Document(
            id=doc_uuid,
            workspace_id=workspace_id,
            uploaded_by=uploaded_by,
            file_name=sanitized_name,
            original_filename=original_filename,
            file_type=file_type,
            mime_type=validated_mime,
            file_size=len(file_bytes),
            storage_path=stored_path,
            status="processing",
            checksum=checksum,
        )

        document = await self.doc_repo.create(document)

        try:
            # 5. Extract text
            extractor = get_extractor_for_file_type(file_type)
            extracted_doc = extractor.extract(file_bytes=file_bytes, filename=sanitized_name)

            # 6. Clean text
            cleaned_doc = TextCleaner.clean_document(extracted_doc)

            # 7. Chunk text
            chunks_data = self.chunker.chunk_document(cleaned_doc, document_id=document.id)

            # 8. Persist chunks in DB
            orm_chunks = [
                DocumentChunk(
                    id=str(uuid.uuid4()),
                    document_id=document.id,
                    chunk_index=cd.chunk_index,
                    content=cd.content,
                    char_count=cd.char_count,
                    token_count=cd.token_count,
                    metadata_json=cd.metadata,
                )
                for cd in chunks_data
            ]

            if orm_chunks:
                await self.chunk_repo.bulk_create_chunks(orm_chunks)

                # 8b. Embed chunks and upsert vectors into Qdrant
                try:
                    chunk_texts = [c.content for c in orm_chunks]
                    embeddings = await self.embedding_service.embed_texts(chunk_texts)
                    await self.vectorstore_service.index_document_chunks(document, orm_chunks, embeddings)
                except Exception as vec_err:
                    error_msg = f"Vector indexing failed: {str(vec_err)}"
                    logger.error(f"Vector Indexing Failed | id='{document.id}' error='{str(vec_err)}'")
                    document.status = "failed"
                    document.processing_error = error_msg[:1000]
                    await self.session.flush()
                    return document

            # 9. Update document status to 'processed'
            document.status = "processed"
            document.processing_error = None
            await self.session.flush()

            logger.info(
                f"Document Ingestion & Vector Indexing Succeeded | id='{document.id}' workspace='{workspace_id}' "
                f"type='{file_type}' chunks={len(orm_chunks)}"
            )
            return document

        except Exception as e:
            # Mark document as 'failed'
            error_msg = f"Document processing failed during extraction/chunking: {str(e)}"
            logger.error(f"Document Ingestion Failed | id='{document.id}' error='{str(e)}'")
            document.status = "failed"
            document.processing_error = error_msg[:1000]
            await self.session.flush()
            return document

    async def list_documents(
        self, workspace_id: str, limit: int = 100, offset: int = 0, status: Optional[str] = None
    ) -> List[Document]:
        return await self.doc_repo.get_by_workspace(workspace_id, limit=limit, offset=offset, status=status)

    async def get_document(self, document_id: str, workspace_id: str) -> Optional[Document]:
        return await self.doc_repo.get_by_id_and_workspace(document_id, workspace_id)

    async def delete_document(self, document_id: str, workspace_id: str) -> bool:
        doc = await self.get_document(document_id, workspace_id)
        if not doc:
            return False

        # Delete physical file from storage
        await self.storage.delete(doc.storage_path)

        # Delete vectors from Qdrant
        try:
            await self.vectorstore_service.delete_document_vectors(document_id)
        except Exception as e:
            logger.warning(f"Failed to delete Qdrant vectors for doc '{document_id}': {str(e)}")

        # Cascade delete DB record and chunks
        return await self.doc_repo.delete_by_id_and_workspace(document_id, workspace_id)
