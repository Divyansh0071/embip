"""
Text Cleaning & Normalization Stage for Document Ingestion Pipeline.
"""

import re
import unicodedata
from typing import List
from app.documents.extractors.base import ExtractedDocument, TextBlock


class TextCleaner:
    """
    Clean and normalize extracted document text while preserving semantic meaning,
    financial values, column headers, and page/sheet structure.
    """

    @staticmethod
    def clean_string(text: str) -> str:
        if not text:
            return ""

        # 1. Unicode Normalization (NFC)
        normalized = unicodedata.normalize("NFC", text)

        # 2. Strip non-printable control characters (preserve \n and \t)
        cleaned_chars = [
            ch for ch in normalized
            if ch in ("\n", "\t") or (unicodedata.category(ch) != "Cc")
        ]
        cleaned = "".join(cleaned_chars)

        # 3. Collapse multiple spaces into single space per line
        lines = []
        for line in cleaned.split("\n"):
            line_cleaned = re.sub(r"[ \t]+", " ", line).strip()
            lines.append(line_cleaned)

        rejoined = "\n".join(lines)

        # 4. Collapse 3 or more consecutive newlines into 2 (paragraph break)
        rejoined = re.sub(r"\n{3,}", "\n\n", rejoined)

        return rejoined.strip()

    @classmethod
    def clean_document(cls, extracted_doc: ExtractedDocument) -> ExtractedDocument:
        """
        Cleans all text blocks within an ExtractedDocument.
        """
        cleaned_blocks: List[TextBlock] = []
        for block in extracted_doc.text_blocks:
            cleaned_text = cls.clean_string(block.text)
            if cleaned_text:
                cleaned_blocks.append(
                    TextBlock(
                        text=cleaned_text,
                        page_number=block.page_number,
                        sheet_name=block.sheet_name,
                        row_count=block.row_count,
                        metadata=block.metadata,
                    )
                )

        return ExtractedDocument(
            filename=extracted_doc.filename,
            file_type=extracted_doc.file_type,
            text_blocks=cleaned_blocks,
            total_pages=extracted_doc.total_pages,
            total_sheets=extracted_doc.total_sheets,
            extracted_metadata=extracted_doc.extracted_metadata,
        )
