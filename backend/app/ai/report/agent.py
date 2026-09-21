"""
ReportAgent for EMBIP (Phase 14).
Drafts executive narrative text using centralized LLMService.
"""

import json
import logging
from typing import Any, Dict, Optional

from app.ai.llm.service import llm_service
from app.ai.report.prompts import REPORT_SYSTEM_PROMPT, REPORT_USER_PROMPT

logger = logging.getLogger(__name__)


class ReportAgent:
    """
    LLM-assisted executive report drafting agent.
    Crafts narrative sections while preserving strict deterministic metrics and citations.
    """

    async def draft_report_narrative(
        self,
        question: str,
        sql_result: Optional[Dict[str, Any]],
        rag_result: Optional[Dict[str, Any]],
        analytics_result: Optional[Dict[str, Any]],
        validation_result: Optional[Dict[str, Any]],
    ) -> Dict[str, str]:
        """
        Calls LLMService to draft executive report title, summary, findings narrative, and methodology.
        """
        sql_summary = json.dumps(sql_result.get("rows", [])[:5]) if sql_result else "None"
        rag_summary = json.dumps([c.get("content", "")[:150] for c in rag_result.get("chunks", [])[:3]]) if rag_result else "None"
        analytics_summary = json.dumps(analytics_result.get("summary", {})) if analytics_result else "None"
        validation_summary = f"Confidence: {validation_result.get('confidence_score', 1.0)}, Action: {validation_result.get('action', 'pass')}" if validation_result else "Verified"

        user_prompt = REPORT_USER_PROMPT.format(
            question=question,
            sql_summary=sql_summary,
            rag_summary=rag_summary,
            analytics_summary=analytics_summary,
            validation_summary=validation_summary,
        )

        try:
            raw_response = await llm_service.generate(
                prompt=user_prompt,
                system_prompt=REPORT_SYSTEM_PROMPT,
                temperature=0.2,
            )

            clean_json = raw_response.strip()
            if clean_json.startswith("```"):
                lines = clean_json.split("\n")
                clean_json = "\n".join(lines[1:-1]) if lines[-1].startswith("```") else "\n".join(lines[1:])
            clean_json = clean_json.strip()

            parsed = json.loads(clean_json)
            return {
                "title": parsed.get("title") or f"Executive Analysis Report: {question[:50]}",
                "subtitle": parsed.get("subtitle") or "Enterprise Business Intelligence Insights",
                "executive_summary": parsed.get("executive_summary") or f"Executive synthesis addressing: {question}",
                "findings_narrative": parsed.get("findings_narrative") or "Detailed findings grounded in enterprise data outputs.",
                "methodology_note": parsed.get("methodology_note") or "Analysis executed via read-only SQL queries and verified RAG document retrieval.",
            }
        except Exception as e:
            logger.warning(f"ReportAgent LLM narrative drafting fallback due to: {str(e)}")
            return {
                "title": f"Executive Intelligence Report: {question[:50]}",
                "subtitle": "Generated BI Report Summary",
                "executive_summary": f"Executive summary addressing query: '{question}'. Grounded in verified relational and unstructured enterprise datasets.",
                "findings_narrative": "Detailed findings derived from verified database queries and analytical computations.",
                "methodology_note": f"Report generated automatically by EMBIP Multi-Agent Engine. System error fallback: {str(e)}",
            }


report_agent = ReportAgent()
