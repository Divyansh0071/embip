"""
Secure File Validation Engine for Document Uploads.
Validates file extensions, MIME types, file sizes, magic bytes signatures, and sanitizes filenames.
"""

import os
import re
from typing import Dict, Tuple

MAX_UPLOAD_SIZE_BYTES = 25 * 1024 * 1024  # 25MB default

SUPPORTED_FORMATS: Dict[str, Dict[str, str]] = {
    ".pdf": {"file_type": "pdf", "default_mime": "application/pdf"},
    ".docx": {"file_type": "docx", "default_mime": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
    ".txt": {"file_type": "txt", "default_mime": "text/plain"},
    ".csv": {"file_type": "csv", "default_mime": "text/csv"},
    ".xlsx": {"file_type": "xlsx", "default_mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
}


class DocumentValidationError(ValueError):
    """Raised when file validation fails security or format constraints."""
    pass


class DocumentValidator:
    """Validator enforcing upload size, extension, MIME type, and magic bytes checks."""

    @staticmethod
    def sanitize_filename(original_filename: str) -> str:
        """
        Sanitize user-provided filename to prevent path traversal and shell injection.
        Strips path components, null bytes, and non-safe characters.
        """
        if not original_filename:
            return "unnamed_document"

        # Remove path separators and null bytes
        basename = os.path.basename(original_filename.replace("\\", "/"))
        basename = basename.replace("\x00", "").strip()

        # Replace unsafe characters while preserving extension dot
        cleaned = re.sub(r"[^\w\-. ]", "_", basename)
        cleaned = re.sub(r"\s+", "_", cleaned)
        return cleaned or "document"

    @staticmethod
    def validate_file(
        filename: str,
        file_bytes: bytes,
        declared_mime: str = "",
        max_size_bytes: int = MAX_UPLOAD_SIZE_BYTES,
    ) -> Tuple[str, str, str]:
        """
        Validates file attributes and returns (sanitized_filename, file_type, validated_mime).

        Raises DocumentValidationError on constraint failure.
        """
        # 1. File size check
        if not file_bytes or len(file_bytes) == 0:
            raise DocumentValidationError("Empty file uploaded. File content cannot be 0 bytes.")

        if len(file_bytes) > max_size_bytes:
            limit_mb = max_size_bytes / (1024 * 1024)
            actual_mb = len(file_bytes) / (1024 * 1024)
            raise DocumentValidationError(
                f"File size ({actual_mb:.2f}MB) exceeds maximum allowed limit ({limit_mb:.0f}MB)."
            )

        # 2. Extension check
        ext = os.path.splitext(filename)[1].lower()
        if ext not in SUPPORTED_FORMATS:
            allowed = ", ".join(SUPPORTED_FORMATS.keys())
            raise DocumentValidationError(
                f"Unsupported file format '{ext}'. Allowed formats: {allowed}."
            )

        fmt_info = SUPPORTED_FORMATS[ext]
        file_type = fmt_info["file_type"]
        validated_mime = declared_mime if declared_mime else fmt_info["default_mime"]

        # 3. Magic Bytes / Signature Verification
        if ext == ".pdf" and not file_bytes.startswith(b"%PDF"):
            raise DocumentValidationError("Invalid PDF file signature. File header does not match PDF specification.")

        if ext in (".docx", ".xlsx") and not file_bytes.startswith(b"PK\x03\x04"):
            raise DocumentValidationError(f"Invalid {ext.lstrip('.').upper()} archive signature. File is corrupted or invalid.")

        sanitized_name = DocumentValidator.sanitize_filename(filename)
        return sanitized_name, file_type, validated_mime
