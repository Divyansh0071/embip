"""
Abstract Document Extractor Interface and Text Block Data Models.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TextBlock(BaseModel):
    """Extracted block of text with metadata (page number, sheet name, section)."""

    text: str = Field(..., description="Extracted text content block")
    page_number: Optional[int] = Field(default=None, description="Source page number (1-indexed)")
    sheet_name: Optional[str] = Field(default=None, description="Spreadsheet sheet name")
    row_count: Optional[int] = Field(default=None, description="Number of structured data rows")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional extraction metadata")


class ExtractedDocument(BaseModel):
    """Complete extracted document text and metadata blocks."""

    filename: str
    file_type: str
    text_blocks: List[TextBlock] = Field(default_factory=list)
    total_pages: Optional[int] = None
    total_sheets: Optional[int] = None
    extracted_metadata: Dict[str, Any] = Field(default_factory=dict)

    def full_text(self) -> str:
        return "\n\n".join(b.text for b in self.text_blocks if b.text.strip())


class DocumentExtractor(ABC):
    """Abstract Base Class for format-specific document text extractors."""

    @abstractmethod
    def extract(self, file_bytes: bytes, filename: str) -> ExtractedDocument:
        """
        Synchronously parse raw file_bytes and return structured ExtractedDocument.
        """
        pass
