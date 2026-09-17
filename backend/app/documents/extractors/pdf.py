"""
PDF Document Extractor using pypdf.
Extracts page-by-page text while preserving page number metadata for citation tracing.
"""

import io
from pypdf import PdfReader
from app.documents.extractors.base import DocumentExtractor, ExtractedDocument, TextBlock


class PDFExtractor(DocumentExtractor):
    """Extractor for Portable Document Format (.pdf) files."""

    def extract(self, file_bytes: bytes, filename: str) -> ExtractedDocument:
        reader = PdfReader(io.BytesIO(file_bytes))
        total_pages = len(reader.pages)
        blocks = []

        for i, page in enumerate(reader.pages):
            page_num = i + 1
            text = page.extract_text() or ""
            text = text.strip()
            if text:
                blocks.append(
                    TextBlock(
                        text=text,
                        page_number=page_num,
                        metadata={"source_filename": filename, "page_number": page_num},
                    )
                )

        return ExtractedDocument(
            filename=filename,
            file_type="pdf",
            text_blocks=blocks,
            total_pages=total_pages,
            extracted_metadata={"total_pages": total_pages},
        )
