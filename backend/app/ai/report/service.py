"""
ReportService for EMBIP (Phase 14).
Synthesizes multi-agent workflow results into structured ReportData, applies post-generation validation, and handles format exports.
"""

import datetime
import uuid
import logging
from typing import Any, Dict, List, Optional

from app.ai.report.agent import report_agent
from app.ai.report.formatters import markdown_formatter, pdf_exporter
from app.ai.report.models import (
    ReportCitation,
    ReportData,
    ReportExportRequest,
    ReportSection,
)

logger = logging.getLogger(__name__)


class ReportService:
    """
    Main orchestrator for generating and exporting executive BI reports.
    """

    async def generate_report(
        self,
        question: str,
        sql_result: Optional[Dict[str, Any]] = None,
        rag_result: Optional[Dict[str, Any]] = None,
        analytics_result: Optional[Dict[str, Any]] = None,
        visualization_result: Optional[Dict[str, Any]] = None,
        validation_result: Optional[Dict[str, Any]] = None,
    ) -> ReportData:
        """
        Synthesizes structured outputs from all agents into a publication-ready ReportData.
        """
        report_id = f"rep_{uuid.uuid4().hex[:12]}"
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Draft Narrative Sections via ReportAgent
        narrative = await report_agent.draft_report_narrative(
            question=question,
            sql_result=sql_result,
            rag_result=rag_result,
            analytics_result=analytics_result,
            validation_result=validation_result,
        )

        # Extract Ground-Truth Metrics
        metrics: Dict[str, Any] = {}
        if sql_result and isinstance(sql_result, dict):
            if sql_result.get("row_count") is not None:
                metrics["total_records_analyzed"] = sql_result["row_count"]
        if analytics_result and isinstance(analytics_result, dict):
            if analytics_result.get("metric") and analytics_result.get("value") is not None:
                metrics[str(analytics_result["metric"])] = analytics_result["value"]
            if analytics_result.get("operation"):
                metrics["primary_analytics_op"] = analytics_result["operation"]

        # Extract Citations
        citations: List[ReportCitation] = []
        if rag_result and isinstance(rag_result, dict) and rag_result.get("chunks"):
            for chunk in rag_result["chunks"]:
                if isinstance(chunk, dict):
                    citations.append(
                        ReportCitation(
                            source_filename=chunk.get("filename", "Document.pdf"),
                            chunk_id=str(chunk.get("chunk_id", uuid.uuid4().hex[:8])),
                            excerpt=chunk.get("content", "")[:300],
                            score=float(chunk.get("score", 0.8)),
                            page_number=chunk.get("page_number"),
                            sheet_name=chunk.get("sheet_name"),
                        )
                    )

        # Build Sections
        sections: List[ReportSection] = [
            ReportSection(
                section_id="sec_summary",
                title="Executive Summary",
                content=narrative["executive_summary"],
                section_type="executive_summary",
            ),
            ReportSection(
                section_id="sec_metrics",
                title="Key Findings & Analytics",
                content=narrative["findings_narrative"],
                section_type="key_metrics",
            ),
        ]

        if citations:
            sources_summary = "\n".join([f"- **{c.source_filename}**: \"{c.excerpt[:100]}...\"" for c in citations])
            sections.append(
                ReportSection(
                    section_id="sec_sources",
                    title="Source Documents & Evidence",
                    content=sources_summary,
                    section_type="sources",
                )
            )

        sections.append(
            ReportSection(
                section_id="sec_methodology",
                title="Methodology & Data Scope",
                content=narrative["methodology_note"],
                section_type="methodology",
            )
        )

        # Confidence Score from Validation Result
        confidence_score = 1.0
        is_validated = True
        if validation_result and isinstance(validation_result, dict):
            confidence_score = float(validation_result.get("confidence_score", 1.0))
            is_validated = bool(validation_result.get("is_valid", True))

        # Visualization Spec
        viz_spec = None
        if visualization_result and isinstance(visualization_result, dict):
            viz_spec = visualization_result.get("spec")

        report = ReportData(
            report_id=report_id,
            title=narrative["title"],
            subtitle=narrative["subtitle"],
            generated_at=timestamp,
            executive_summary=narrative["executive_summary"],
            sections=sections,
            metrics=metrics,
            visualization_spec=viz_spec,
            citations=citations,
            methodology=narrative["methodology_note"],
            confidence_score=confidence_score,
            is_validated=is_validated,
        )

        logger.info(f"ReportService generated report | id='{report_id}' | score={confidence_score}")
        return report

    def export_report(self, request: ReportExportRequest) -> Any:
        """
        Exports ReportData to Markdown, PDF, or JSON format.
        """
        if request.format == "markdown":
            return markdown_formatter.format(request.report_data)
        elif request.format == "pdf":
            return pdf_exporter.export(request.report_data)
        elif request.format == "json":
            return request.report_data.model_dump()
        else:
            raise ValueError(f"Unsupported report export format: {request.format}")


report_service = ReportService()
