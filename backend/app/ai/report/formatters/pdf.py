"""
PDF Exporter for EMBIP Report Generator Agent (Phase 14).
Generates publication-quality PDF binary streams from ReportData.
Uses ReportLab if available, or falls back to structured PDF stream generator.
"""

import io
import logging

from app.ai.report.exceptions import ReportExportError
from app.ai.report.models import ReportData


logger = logging.getLogger(__name__)

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class PDFExporter:
    """
    Exports ReportData objects to PDF binary stream.
    """

    def export(self, report: ReportData) -> bytes:
        if REPORTLAB_AVAILABLE:
            return self._export_reportlab(report)
        else:
            return self._export_simple_pdf(report)

    def _export_reportlab(self, report: ReportData) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()
        
        # Custom Paragraph Styles
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=4,
        )
        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#64748b"),
            spaceAfter=12,
        )
        h2_style = ParagraphStyle(
            "DocHeading2",
            parent=styles["Heading2"],
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=12,
            spaceAfter=6,
        )
        body_style = ParagraphStyle(
            "DocBody",
            parent=styles["BodyText"],
            fontSize=9.5,
            leading=13.5,
            textColor=colors.HexColor("#334155"),
            spaceAfter=6,
        )
        quote_style = ParagraphStyle(
            "DocQuote",
            parent=styles["Normal"],
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#475569"),
            leftIndent=15,
            spaceAfter=6,
        )

        story = []

        # Title Header
        story.append(Paragraph(report.title, title_style))
        if report.subtitle:
            story.append(Paragraph(report.subtitle, subtitle_style))
        
        # Metadata bar
        meta_text = f"<b>Generated At:</b> {report.generated_at} | <b>Confidence Rating:</b> {int(report.confidence_score * 100)}% Verified"
        story.append(Paragraph(meta_text, subtitle_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceBefore=6, spaceAfter=12))

        # Executive Summary Section
        story.append(Paragraph("1. Executive Summary", h2_style))
        story.append(Paragraph(report.executive_summary, body_style))
        story.append(Spacer(1, 8))

        # Key Metrics Table
        if report.metrics:
            story.append(Paragraph("2. Key Business Metrics", h2_style))
            table_data = [["Metric Name", "Value"]]
            for k, v in report.metrics.items():
                if isinstance(v, (int, float)):
                    formatted_val = f"{v:,.2f}" if isinstance(v, float) else f"{v:,}"
                else:
                    formatted_val = str(v)
                table_data.append([k.replace("_", " ").title(), formatted_val])

            t = Table(table_data, colWidths=[250, 250])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ]))
            story.append(t)
            story.append(Spacer(1, 10))

        # Content Sections
        sec_num = 3
        for sec in report.sections:
            if sec.section_type in ["executive_summary", "key_metrics"]:
                continue
            story.append(Paragraph(f"{sec_num}. {sec.title}", h2_style))
            story.append(Paragraph(sec.content, body_style))
            sec_num += 1

        # Citations Section
        if report.citations:
            story.append(Paragraph("Evidence & Source Documents", h2_style))
            for idx, cite in enumerate(report.citations, start=1):
                page_info = f" (Page {cite.page_number})" if cite.page_number else ""
                sheet_info = f" (Sheet: {cite.sheet_name})" if cite.sheet_name else ""
                header = f"<b>{idx}. {cite.source_filename}</b>{page_info}{sheet_info} — Score: {int(cite.score * 100)}%"
                story.append(Paragraph(header, body_style))
                story.append(Paragraph(f'"{cite.excerpt}"', quote_style))

        # Methodology Section
        story.append(Paragraph("Methodology & Operational Boundaries", h2_style))
        story.append(Paragraph(report.methodology, body_style))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def _export_simple_pdf(self, report: ReportData) -> bytes:
        """Fallback lightweight PDF binary stream generator if reportlab is absent."""
        text_content = f"EMBIP REPORT: {report.title}\n{report.executive_summary}\n\nMetrics:\n{report.metrics}"
        encoded = text_content.encode("utf-8")
        
        pdf_bytes = io.BytesIO()
        pdf_bytes.write(b"%PDF-1.4\n")
        pdf_bytes.write(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
        pdf_bytes.write(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
        pdf_bytes.write(b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n")
        
        stream_data = f"BT /F1 12 Pt 50 700 Td ({report.title}) Tj ET".encode("latin1", errors="ignore")
        pdf_bytes.write(f"4 0 obj\n<< /Length {len(stream_data)} >>\nstream\n".encode("utf-8"))
        pdf_bytes.write(stream_data)
        pdf_bytes.write(b"\nendstream\nendobj\n")
        pdf_bytes.write(b"xref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n0000000117 00000 n \n0000000215 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n300\n%%EOF")
        
        pdf_bytes.seek(0)
        return pdf_bytes.getvalue()


pdf_exporter = PDFExporter()
