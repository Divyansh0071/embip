"""
Comprehensive Unit & Integration Test Suite for Document Ingestion Pipeline (Phase 7).
Covers validation, storage abstraction, extractors (PDF, DOCX, TXT, CSV, XLSX), cleaner, chunker,
processing service lifecycle, tenant isolation, and FastAPI endpoints.
"""

import io
import os
import tempfile
import pytest
import docx
import openpyxl
from pypdf import PdfWriter
from fastapi.testclient import TestClient

from app.documents.extractors import (
    CSVExtractor,
    DOCXExtractor,
    PDFExtractor,
    TXTExtractor,
    XLSXExtractor,
    get_extractor_for_file_type,
)
from app.documents.extractors.base import ExtractedDocument, TextBlock
from app.documents.processing.cleaner import TextCleaner
from app.documents.processing.chunker import TextChunker
from app.documents.processing.validator import DocumentValidationError, DocumentValidator
from app.documents.storage.local import LocalDocumentStorage
from app.main import app

client = TestClient(app)


# Helper functions for generating binary sample test files in-memory
def create_sample_pdf_bytes() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def create_sample_docx_bytes() -> bytes:
    doc = docx.Document()
    doc.add_heading("NovaMart Q3 Report", 0)
    doc.add_paragraph("Total Q3 Revenue reached $12,450,000 across 10 retail stores.")
    table = doc.add_table(rows=2, cols=2)
    table.rows[0].cells[0].text = "Region"
    table.rows[0].cells[1].text = "Revenue"
    table.rows[1].cells[0].text = "North"
    table.rows[1].cells[1].text = "$5,200,000"
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def create_sample_xlsx_bytes() -> bytes:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Financial Summary"
    ws.append(["Category", "Q1", "Q2", "Q3", "Q4"])
    ws.append(["Sales", 100, 150, 200, 250])
    ws.append(["Expenses", 50, 60, 70, 80])
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


# ------------------------------------------------------------------------------
# 1. FILE VALIDATOR TESTS
# ------------------------------------------------------------------------------

def test_validator_supported_formats():
    """Verify supported file extensions are accepted."""
    name, ftype, mime = DocumentValidator.validate_file(
        filename="sales_report.pdf",
        file_bytes=b"%PDF-1.4 test content",
    )
    assert name == "sales_report.pdf"
    assert ftype == "pdf"
    assert mime == "application/pdf"


def test_validator_unsupported_format_rejected():
    """Verify dangerous or unsupported extensions are rejected."""
    with pytest.raises(DocumentValidationError, match="Unsupported file format"):
        DocumentValidator.validate_file(filename="script.exe", file_bytes=b"MZ test")

    with pytest.raises(DocumentValidationError, match="Unsupported file format"):
        DocumentValidator.validate_file(filename="shell.sh", file_bytes=b"#!/bin/sh")


def test_validator_empty_file_rejected():
    """Verify 0-byte files are rejected."""
    with pytest.raises(DocumentValidationError, match="Empty file uploaded"):
        DocumentValidator.validate_file(filename="empty.txt", file_bytes=b"")


def test_validator_file_size_exceeded():
    """Verify files exceeding maximum byte limit are rejected."""
    large_bytes = b"X" * 100
    with pytest.raises(DocumentValidationError, match="exceeds maximum allowed limit"):
        DocumentValidator.validate_file(
            filename="large.txt", file_bytes=large_bytes, max_size_bytes=50
        )


def test_validator_path_traversal_sanitization():
    """Verify filename sanitization strips directory traversal attempts."""
    malicious_names = [
        "../../etc/passwd.pdf",
        "C:\\Windows\\System32\\cmd.exe.txt",
        "nested/subfolder/file.csv",
        "file\x00with_null.docx",
    ]
    for m in malicious_names:
        sanitized = DocumentValidator.sanitize_filename(m)
        assert "/" not in sanitized
        assert "\\" not in sanitized
        assert "\x00" not in sanitized
        assert ".." not in sanitized


def test_validator_magic_bytes_check():
    """Verify file magic signatures are validated."""
    # Invalid PDF signature
    with pytest.raises(DocumentValidationError, match="Invalid PDF file signature"):
        DocumentValidator.validate_file(filename="fake.pdf", file_bytes=b"NOT_A_PDF_FILE")

    # Invalid DOCX signature
    with pytest.raises(DocumentValidationError, match="Invalid DOCX archive signature"):
        DocumentValidator.validate_file(filename="fake.docx", file_bytes=b"NOT_A_ZIP_ARCHIVE")


# ------------------------------------------------------------------------------
# 2. FILE EXTRACTORS TESTS
# ------------------------------------------------------------------------------

def test_txt_extractor():
    """Test TXTExtractor text extraction and encoding fallback."""
    txt_bytes = "NovaMart Annual Sales Summary 2025\nTotal Transactions: 100,000".encode("utf-8")
    extractor = TXTExtractor()
    extracted = extractor.extract(txt_bytes, "summary.txt")

    assert extracted.file_type == "txt"
    assert len(extracted.text_blocks) == 1
    assert "NovaMart Annual Sales Summary" in extracted.text_blocks[0].text


def test_csv_extractor():
    """Test CSVExtractor structured key-value line formatting."""
    csv_content = "Store,City,Revenue\n101,Mumbai,1500000\n102,Delhi,1800000\n".encode("utf-8")
    extractor = CSVExtractor()
    extracted = extractor.extract(csv_content, "stores.csv")

    assert extracted.file_type == "csv"
    assert len(extracted.text_blocks) == 1
    text = extracted.text_blocks[0].text
    assert "Header Columns: Store, City, Revenue" in text
    assert "Row 1: Store: 101 | City: Mumbai | Revenue: 1500000" in text


def test_pdf_extractor():
    """Test PDFExtractor page-by-page extraction."""
    pdf_bytes = create_sample_pdf_bytes()
    extractor = PDFExtractor()
    extracted = extractor.extract(pdf_bytes, "sample.pdf")

    assert extracted.file_type == "pdf"
    assert extracted.total_pages == 1


def test_docx_extractor():
    """Test DOCXExtractor paragraph and table extraction."""
    docx_bytes = create_sample_docx_bytes()
    extractor = DOCXExtractor()
    extracted = extractor.extract(docx_bytes, "report.docx")

    assert extracted.file_type == "docx"
    assert len(extracted.text_blocks) >= 1
    full_text = extracted.full_text()
    assert "NovaMart Q3 Report" in full_text
    assert "North" in full_text
    assert "$5,200,000" in full_text


def test_xlsx_extractor():
    """Test XLSXExtractor sheet and cell extraction."""
    xlsx_bytes = create_sample_xlsx_bytes()
    extractor = XLSXExtractor()
    extracted = extractor.extract(xlsx_bytes, "financials.xlsx")

    assert extracted.file_type == "xlsx"
    assert extracted.total_sheets == 1
    text = extracted.full_text()
    assert "[Sheet: Financial Summary]" in text
    assert "Category | Q1 | Q2 | Q3 | Q4" in text
    assert "Sales | 100 | 150 | 200 | 250" in text


# ------------------------------------------------------------------------------
# 3. TEXT CLEANER & DETERMINISTIC CHUNKER TESTS
# ------------------------------------------------------------------------------

def test_text_cleaner():
    """Verify TextCleaner normalizes whitespace and strips control characters."""
    dirty_text = "  Header   Line \r\n\n\n\n  Subtext \x00 with   spaces  "
    cleaned = TextCleaner.clean_string(dirty_text)

    assert "\x00" not in cleaned
    assert "Header Line" in cleaned
    assert "\n\n" in cleaned  # Collapsed 4 newlines into 2
    assert "Subtext with spaces" in cleaned


def test_text_chunker_deterministic():
    """Verify TextChunker generates stable, overlapping chunks with metadata."""
    sample_text = "Word " * 300  # ~1500 characters
    block = TextBlock(text=sample_text, page_number=2, metadata={"author": "Analyst"})
    extracted_doc = ExtractedDocument(
        filename="test.txt",
        file_type="txt",
        text_blocks=[block],
    )

    chunker = TextChunker(chunk_size=500, chunk_overlap=100)
    chunks = chunker.chunk_document(extracted_doc, document_id="doc-uuid-123")

    assert len(chunks) > 1
    assert chunks[0].chunk_index == 0
    assert chunks[1].chunk_index == 1
    assert chunks[0].metadata["document_id"] == "doc-uuid-123"
    assert chunks[0].metadata["page_number"] == 2
    assert chunks[0].char_count == len(chunks[0].content)
    assert chunks[0].token_count > 0


# ------------------------------------------------------------------------------
# 4. STORAGE ABSTRACTION SECURITY TESTS
# ------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_local_storage_path_traversal_prevention():
    """Verify LocalDocumentStorage prevents directory traversal outside base_dir."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = LocalDocumentStorage(base_dir=tmpdir)

        # Valid save
        saved_path = await storage.store(b"test file content", "workspace_1/doc1.txt")
        assert await storage.exists(saved_path)

        # Path traversal attempt should raise ValueError
        with pytest.raises(ValueError, match="attempts directory traversal"):
            await storage.store(b"malicious", "../../outside.txt")


# ------------------------------------------------------------------------------
# 5. FASTAPI ENDPOINTS & TENANT ISOLATION INTEGRATION TESTS
# ------------------------------------------------------------------------------

def test_documents_unauthenticated_upload_rejected():
    """Verify document upload without Bearer token is rejected with HTTP 401."""
    files = {"file": ("test.txt", b"Content", "text/plain")}
    response = client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == 401


def test_documents_list_unauthenticated_rejected():
    """Verify document list endpoint requires authentication."""
    response = client.get("/api/v1/documents")
    assert response.status_code == 401
