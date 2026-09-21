"""
Unit Tests for EMBIP Report Generator Agent (Phase 14).
"""

import pytest
from app.ai.report.formatters import markdown_formatter
from app.ai.report.models import ReportCitation, ReportData, ReportSection
from app.ai.report.service import report_service


def test_markdown_formatter():
    report = ReportData(
        report_id="rep_test123",
        title="Q3 Sales Performance Report",
        subtitle="Quarterly Revenue Summary",
        generated_at="2026-09-21T00:00:00Z",
        executive_summary="Executive summary: Sales increased 15% in Q3.",
        sections=[
            ReportSection(
                section_id="sec_1",
                title="Regional Breakdown",
                content="North region led overall revenue.",
                section_type="key_metrics",
            )
        ],
        metrics={"total_revenue": 1250000.5, "total_orders": 4500},
        citations=[
            ReportCitation(
                source_filename="Q3_Report.pdf",
                chunk_id="chk_1",
                excerpt="North region achieved $1.25M sales.",
                score=0.92,
                page_number=3,
            )
        ],
        methodology="Executed via read-only SQL queries on NovaMart DB.",
        confidence_score=0.98,
        is_validated=True,
    )

    md_output = markdown_formatter.format(report)

    assert "# Q3 Sales Performance Report" in md_output
    assert "98% Verified" in md_output
    assert "Executive summary: Sales increased 15% in Q3." in md_output
    assert "1,250,000.50" in md_output
    assert "Q3_Report.pdf" in md_output
    assert "North region achieved $1.25M sales." in md_output


@pytest.mark.asyncio
async def test_report_service_generate_report():
    question = "What was our quarterly revenue and top product?"
    sql_res = {"status": "success", "rows": [{"product": "Widget A", "revenue": 500000}], "row_count": 1}
    rag_res = {"chunks": [{"filename": "sales_doc.pdf", "content": "Widget A was top product in Q3.", "score": 0.88}]}
    analytics_res = {"metric": "total_revenue", "value": 500000, "operation": "sum"}
    validation_res = {"confidence_score": 0.95, "is_valid": True}

    report = await report_service.generate_report(
        question=question,
        sql_result=sql_res,
        rag_result=rag_res,
        analytics_result=analytics_res,
        validation_result=validation_res,
    )

    assert report.report_id.startswith("rep_")
    assert report.confidence_score == 0.95
    assert report.metrics.get("total_records_analyzed") == 1
    assert len(report.citations) == 1
    assert report.citations[0].source_filename == "sales_doc.pdf"
