"""
Markdown Formatter for EMBIP Report Generator Agent (Phase 14).
Converts ReportData Pydantic schema into clean, structured GitHub-Flavored Markdown.
"""

from app.ai.report.models import ReportData


class MarkdownFormatter:
    """
    Renders ReportData objects into publication-ready Markdown text.
    """

    def format(self, report: ReportData) -> str:
        lines = []

        # Title & Subtitle Header
        lines.append(f"# {report.title}")
        if report.subtitle:
            lines.append(f"*{report.subtitle}*")
        lines.append("")
        lines.append(f"**Generated At:** `{report.generated_at}` | **Confidence Rating:** `{int(report.confidence_score * 100)}% Verified`")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Executive Summary Section
        lines.append("## 1. Executive Summary")
        lines.append(report.executive_summary)
        lines.append("")

        # Key Metrics Section
        if report.metrics:
            lines.append("## 2. Key Business Metrics")
            lines.append("| Metric Name | Value |")
            lines.append("| :--- | :--- |")
            for k, v in report.metrics.items():
                if isinstance(v, (int, float)):
                    formatted_val = f"{v:,.2f}" if isinstance(v, float) else f"{v:,}"
                else:
                    formatted_val = str(v)
                lines.append(f"| **{k.replace('_', ' ').title()}** | `{formatted_val}` |")
            lines.append("")

        # Content Sections
        for idx, sec in enumerate(report.sections, start=3):
            if sec.section_type in ["executive_summary", "key_metrics"]:
                continue
            lines.append(f"## {idx}. {sec.title}")
            lines.append(sec.content)
            lines.append("")

        # Citations & Evidence Section
        if report.citations:
            lines.append("## Evidence & Source Documents")
            for c_idx, cite in enumerate(report.citations, start=1):
                page_info = f" (Page {cite.page_number})" if cite.page_number else ""
                sheet_info = f" (Sheet: {cite.sheet_name})" if cite.sheet_name else ""
                lines.append(f"{c_idx}. **{cite.source_filename}**{page_info}{sheet_info} — *Score: {int(cite.score * 100)}%*")
                lines.append(f"> \"{cite.excerpt}\"")
                lines.append("")

        # Methodology & Limitations Section
        lines.append("## Methodology & Operational Boundaries")
        lines.append(report.methodology)
        lines.append("")

        return "\n".join(lines)


markdown_formatter = MarkdownFormatter()
