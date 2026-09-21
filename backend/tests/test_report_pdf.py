"""
Unit Tests for PDFExporter (Phase 14).
"""

import pytest
from app.ai.report.formatters import pdf_exporter
from app.ai.report.models import ReportCitation, ReportData, ReportSection


def test_pdf_exporter():
    report = ReportData(
        report_id="rep_pdf_123",
        title="Annual Financial Summary",
        subtitle="Executive Board Report",
        generated_at="2026-09-21T00:00:00Z",
        executive_summary="Annual financial growth exceeded expectations.",
        sections=[
            ReportSection(
                section_id="sec_1",
                title="Performance",
                content="Revenue grew by 20% year over year.",
                section_type="key_metrics",
            )
        ],
        metrics={"annual_revenue": 10000000},
        citations=[
            ReportCitation(
                source_filename="Annual_Report.pdf",
                chunk_id="chk_2",
                excerpt="Annual revenue reached $10M.",
                score=0.95,
            )
        ],
        methodology="SQL calculations and verified vector retrieval.",
        confidence_score=0.96,
        is_validated=True,
    )

    pdf_bytes = pdf_exporter.export(report)

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    assert pdf_bytes.startswith(b"%PDF")
