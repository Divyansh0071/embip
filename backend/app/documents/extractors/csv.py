"""
CSV Document Extractor.
Converts tabular CSV files into structured, key-value text representations for vector retrieval.
"""

import csv
import io
from app.documents.extractors.base import DocumentExtractor, ExtractedDocument, TextBlock


class CSVExtractor(DocumentExtractor):
    """Extractor for Comma-Separated Values (.csv) files."""

    def extract(self, file_bytes: bytes, filename: str) -> ExtractedDocument:
        # Decode text with fallback
        try:
            content_str = file_bytes.decode("utf-8-sig")
        except UnicodeDecodeError:
            content_str = file_bytes.decode("latin-1", errors="replace")

        reader = csv.reader(io.StringIO(content_str))
        rows = [row for row in reader if any(cell.strip() for cell in row)]

        if not rows:
            return ExtractedDocument(
                filename=filename,
                file_type="csv",
                text_blocks=[],
                extracted_metadata={"row_count": 0},
            )

        headers = [h.strip() for h in rows[0]]
        data_rows = rows[1:]

        formatted_lines = []
        formatted_lines.append(f"Header Columns: {', '.join(headers)}")

        for r_idx, row in enumerate(data_rows):
            row_items = []
            for h_idx, cell_value in enumerate(row):
                val = cell_value.strip()
                if val:
                    col_name = headers[h_idx] if h_idx < len(headers) else f"Column_{h_idx + 1}"
                    row_items.append(f"{col_name}: {val}")

            if row_items:
                formatted_lines.append(f"Row {r_idx + 1}: " + " | ".join(row_items))

        text_content = "\n".join(formatted_lines)
        blocks = [
            TextBlock(
                text=text_content,
                row_count=len(data_rows),
                metadata={"source_filename": filename, "headers": headers, "total_rows": len(data_rows)},
            )
        ]

        return ExtractedDocument(
            filename=filename,
            file_type="csv",
            text_blocks=blocks,
            extracted_metadata={"column_count": len(headers), "row_count": len(data_rows)},
        )
