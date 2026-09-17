# Documents Processing (`documents/`)

This directory houses corporate documents (PDFs, DOCXs, CSVs, XLSXs) used for document ingestion and RAG vector storage processing.

## Directory Structure

```
documents/
├── sample/    # Sample corporate reports, PDFs, and spreadsheets for testing
├── uploads/   # Temporary storage location for uploaded user files
├── processed/ # Extracted and chunked text outputs
└── README.md  # Documentation
```

## Implementation Plan
* **Phase 7 (Document Ingestion):** Parsing PDF, DOCX, TXT, CSV, and XLSX formats with semantic chunking.
* **Phase 8 (RAG Engine):** Embedding chunk vectors and loading into Qdrant Cloud.
