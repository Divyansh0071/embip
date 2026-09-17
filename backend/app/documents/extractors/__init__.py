"""
Document Extractors Registry & Factory.
"""

from typing import Dict, Type
from app.documents.extractors.base import DocumentExtractor, ExtractedDocument, TextBlock
from app.documents.extractors.pdf import PDFExtractor
from app.documents.extractors.docx import DOCXExtractor
from app.documents.extractors.txt import TXTExtractor
from app.documents.extractors.csv import CSVExtractor
from app.documents.extractors.xlsx import XLSXExtractor

EXTRACTOR_MAP: Dict[str, Type[DocumentExtractor]] = {
    "pdf": PDFExtractor,
    "docx": DOCXExtractor,
    "txt": TXTExtractor,
    "csv": CSVExtractor,
    "xlsx": XLSXExtractor,
}


def get_extractor_for_file_type(file_type: str) -> DocumentExtractor:
    """
    Factory function returning an instantiated DocumentExtractor for given file_type.

    Raises ValueError if file_type is unsupported.
    """
    normalized_type = file_type.lower().lstrip(".")
    extractor_cls = EXTRACTOR_MAP.get(normalized_type)
    if not extractor_cls:
        raise ValueError(f"No document extractor registered for file type '{file_type}'.")
    return extractor_cls()


__all__ = [
    "DocumentExtractor",
    "ExtractedDocument",
    "TextBlock",
    "PDFExtractor",
    "DOCXExtractor",
    "TXTExtractor",
    "CSVExtractor",
    "XLSXExtractor",
    "get_extractor_for_file_type",
]
