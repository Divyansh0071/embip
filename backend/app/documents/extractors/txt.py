"""
TXT Text File Extractor.
Parses plaintext (.txt) files with encoding fallback handling.
"""

from app.documents.extractors.base import DocumentExtractor, ExtractedDocument, TextBlock


class TXTExtractor(DocumentExtractor):
    """Extractor for Plain Text (.txt) files."""

    def extract(self, file_bytes: bytes, filename: str) -> ExtractedDocument:
        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
        decoded_text = ""
        used_encoding = "utf-8"

        for enc in encodings:
            try:
                decoded_text = file_bytes.decode(enc)
                used_encoding = enc
                break
            except UnicodeDecodeError:
                continue
        else:
            decoded_text = file_bytes.decode("utf-8", errors="replace")
            used_encoding = "utf-8-replaced"

        cleaned_text = decoded_text.strip()
        blocks = []

        if cleaned_text:
            blocks.append(
                TextBlock(
                    text=cleaned_text,
                    metadata={"source_filename": filename, "encoding": used_encoding},
                )
            )

        return ExtractedDocument(
            filename=filename,
            file_type="txt",
            text_blocks=blocks,
            extracted_metadata={"encoding": used_encoding, "character_length": len(cleaned_text)},
        )
