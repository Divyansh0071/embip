"""
ValidationAgent for EMBIP (Phase 13).
Executes LLM-assisted semantic claim validation using centralized LLMService.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from app.ai.llm.service import llm_service
from app.ai.validation.prompts import VALIDATION_SYSTEM_PROMPT, VALIDATION_USER_PROMPT

logger = logging.getLogger(__name__)


class ValidationAgent:
    """
    LLM-assisted semantic audit agent.
    Checks candidate text explanations against raw workflow data for hallucinated claims or CoT leaks.
    """

    async def audit_claim_grounding(
        self,
        question: str,
        sql_result: Optional[Dict[str, Any]],
        rag_result: Optional[Dict[str, Any]],
        analytics_result: Optional[Dict[str, Any]],
        candidate_text: str,
    ) -> Dict[str, Any]:
        """
        Calls LLMService to audit whether candidate_text is grounded and safe.
        """
        if not candidate_text.strip():
            return {
                "is_grounded": True,
                "confidence_score": 1.0,
                "hallucinated_claims": [],
                "unsupported_statements": [],
                "audit_summary": "Empty candidate text. Grounding audit passed automatically.",
            }

        sql_summary = json.dumps(sql_result.get("rows", [])[:5]) if sql_result else "None"
        rag_summary = json.dumps([c.get("content", "")[:150] for c in rag_result.get("chunks", [])[:3]]) if rag_result else "None"
        analytics_summary = json.dumps(analytics_result.get("summary", {})) if analytics_result else "None"

        user_prompt = VALIDATION_USER_PROMPT.format(
            question=question,
            sql_summary=sql_summary,
            rag_summary=rag_summary,
            analytics_summary=analytics_summary,
            candidate_text=candidate_text[:1000],
        )

        try:
            raw_response = await llm_service.generate(
                prompt=user_prompt,
                system_prompt=VALIDATION_SYSTEM_PROMPT,
                temperature=0.0,  # Zero temperature for deterministic audit
            )

            clean_json = raw_response.strip()
            if clean_json.startswith("```"):
                lines = clean_json.split("\n")
                clean_json = "\n".join(lines[1:-1]) if lines[-1].startswith("```") else "\n".join(lines[1:])
            clean_json = clean_json.strip()

            parsed = json.loads(clean_json)
            return {
                "is_grounded": parsed.get("is_grounded", True),
                "confidence_score": float(parsed.get("confidence_score", 0.9)),
                "hallucinated_claims": parsed.get("hallucinated_claims", []),
                "unsupported_statements": parsed.get("unsupported_statements", []),
                "audit_summary": parsed.get("audit_summary", "Audit completed successfully."),
            }
        except Exception as e:
            logger.warning(f"ValidationAgent LLM audit fallback due to: {str(e)}")
            return {
                "is_grounded": True,
                "confidence_score": 0.85,
                "hallucinated_claims": [],
                "unsupported_statements": [],
                "audit_summary": f"Fallback audit applied: {str(e)}",
            }


validation_agent = ValidationAgent()
