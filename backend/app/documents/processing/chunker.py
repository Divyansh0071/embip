"""
Deterministic Text Chunking Engine for Document Retrieval & RAG.
Performs chunking with configurable character limits, overlap window, and metadata retention.
"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field
from app.documents.extractors.base import ExtractedDocument


class ChunkData(BaseModel):
    """Processed document chunk ready for persistence."""

    chunk_index: int
    content: str
    char_count: int
    token_count: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TextChunker:
    """
    Deterministic chunker splitting ExtractedDocument text blocks into overlapping chunks.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0.")
        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be non-negative and strictly less than chunk_size.")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, extracted_doc: ExtractedDocument, document_id: str) -> List[ChunkData]:
        """
        Splits an ExtractedDocument into deterministic, overlapping chunks.
        """
        chunks: List[ChunkData] = []
        global_chunk_idx = 0

        for block in extracted_doc.text_blocks:
            text = block.text.strip()
            if not text:
                continue

            # Base metadata inherited from TextBlock
            base_meta = {
                "document_id": document_id,
                "filename": extracted_doc.filename,
                "file_type": extracted_doc.file_type,
            }
            if block.page_number is not None:
                base_meta["page_number"] = block.page_number
            if block.sheet_name is not None:
                base_meta["sheet_name"] = block.sheet_name
            if block.row_count is not None:
                base_meta["row_count"] = block.row_count
            base_meta.update(block.metadata)

            # If text fits within single chunk
            if len(text) <= self.chunk_size:
                char_count = len(text)
                token_estimate = max(1, char_count // 4)
                meta = dict(base_meta)
                meta.update({"start_char": 0, "end_char": char_count})

                chunks.append(
                    ChunkData(
                        chunk_index=global_chunk_idx,
                        content=text,
                        char_count=char_count,
                        token_count=token_estimate,
                        metadata=meta,
                    )
                )
                global_chunk_idx += 1
            else:
                # Sliding window chunking
                step = self.chunk_size - self.chunk_overlap
                start = 0
                text_len = len(text)

                while start < text_len:
                    end = min(start + self.chunk_size, text_len)
                    chunk_str = text[start:end].strip()

                    if chunk_str:
                        char_count = len(chunk_str)
                        token_estimate = max(1, char_count // 4)
                        meta = dict(base_meta)
                        meta.update({"start_char": start, "end_char": end})

                        chunks.append(
                            ChunkData(
                                chunk_index=global_chunk_idx,
                                content=chunk_str,
                                char_count=char_count,
                                token_count=token_estimate,
                                metadata=meta,
                            )
                        )
                        global_chunk_idx += 1

                    if end == text_len:
                        break
                    start += step

        return chunks
