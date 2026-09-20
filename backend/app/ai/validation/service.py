"""
ValidationService for EMBIP (Phase 13).
Orchestrates deterministic checks, LLM claim grounding audits, confidence scoring, and retry action decision logic.
"""

import logging
from typing import Any, Dict, List, Optional

from app.ai.validation.agent import validation_agent
from app.ai.validation.checks import (
    check_ast_safety_audit,
    check_contradiction_detection,
    check_numerical_consistency,
    check_rag_citation_integrity,
)
from app.ai.validation.models import (
    ValidationCheckResult,
    ValidationReport,
    ValidationRequest,
)

logger = logging.getLogger(__name__)


class ValidationService:
    """
    Main entry point for factual, security, and quality audit of multi-agent state outputs.
    """

    async def validate(self, request: ValidationRequest) -> ValidationReport:
        """
        Executes all validation checks, computes weighted confidence score, and determines workflow action.
        """
        checks: List[ValidationCheckResult] = []
        hallucinations: List[str] = []
        contradictions: List[str] = []
        warnings: List[str] = []

        # Collect text candidate explanations to check
        texts_to_check: List[str] = []
        if request.analytics_result and isinstance(request.analytics_result, dict):
            if request.analytics_result.get("explanation"):
                texts_to_check.append(str(request.analytics_result["explanation"]))
        if request.visualization_result and isinstance(request.visualization_result, dict):
            spec = request.visualization_result.get("spec") or {}
            if spec.get("title"):
                texts_to_check.append(str(spec["title"]))
            if spec.get("subtitle"):
                texts_to_check.append(str(spec["subtitle"]))
            if spec.get("executive_highlights"):
                texts_to_check.extend([str(h) for h in spec["executive_highlights"]])

        # 1. AST Safety Audit
        ast_check = check_ast_safety_audit(request.sql_result)
        checks.append(ast_check)
        if not ast_check.passed:
            warnings.append(f"AST Safety: {ast_check.message}")

        # 2. Numerical Consistency Check
        num_check = check_numerical_consistency(
            sql_result=request.sql_result,
            analytics_result=request.analytics_result,
            texts_to_check=texts_to_check,
        )
        checks.append(num_check)
        if not num_check.passed:
            unsupported = num_check.details.get("unsupported_numbers", [])
            hallucinations.append(f"Unsupported numerical claims detected in text: {unsupported}")
            warnings.append(num_check.message)

        # 3. RAG Citation Integrity Check
        citation_check = check_rag_citation_integrity(
            rag_result=request.rag_result,
            texts_to_check=texts_to_check,
        )
        checks.append(citation_check)
        if not citation_check.passed:
            uncited = citation_check.details.get("uncited_quotes", [])
            hallucinations.append(f"Uncited quotes detected: {uncited}")
            warnings.append(citation_check.message)

        # 4. Contradiction Detection Check
        contradiction_check = check_contradiction_detection(
            sql_result=request.sql_result,
            rag_result=request.rag_result,
        )
        checks.append(contradiction_check)
        if not contradiction_check.passed:
            detected_cntr = contradiction_check.details.get("contradictions", [])
            contradictions.extend(detected_cntr)
            warnings.append(contradiction_check.message)

        # 5. Semantic Claim Audit via ValidationAgent (if texts exist)
        candidate_text_combined = " ".join(texts_to_check)
        if candidate_text_combined.strip():
            audit_res = await validation_agent.audit_claim_grounding(
                question=request.question,
                sql_result=request.sql_result,
                rag_result=request.rag_result,
                analytics_result=request.analytics_result,
                candidate_text=candidate_text_combined,
            )
            semantic_check = ValidationCheckResult(
                check_name="semantic_grounding_audit",
                passed=audit_res.get("is_grounded", True),
                score=audit_res.get("confidence_score", 0.9),
                message=audit_res.get("audit_summary", "Semantic grounding audit complete."),
                details=audit_res,
            )
            checks.append(semantic_check)
            if audit_res.get("hallucinated_claims"):
                hallucinations.extend(audit_res["hallucinated_claims"])

        # Compute Weighted Confidence Score
        scores = [c.score for c in checks]
        confidence_score = sum(scores) / len(scores) if scores else 1.0
        confidence_score = round(confidence_score, 2)

        # Determine Overall Validity & Action
        is_valid = ast_check.passed and num_check.passed and confidence_score >= 0.70

        if not ast_check.passed or len(hallucinations) > 2 or confidence_score < 0.70:
            action = "retry"
        elif confidence_score < 0.85 or warnings:
            action = "flag"
        else:
            action = "pass"

        report = ValidationReport(
            is_valid=is_valid,
            confidence_score=confidence_score,
            checks=checks,
            hallucinations_detected=hallucinations,
            contradictions_detected=contradictions,
            warnings=warnings,
            action=action,
        )

        logger.info(
            f"ValidationService completed audit | is_valid={report.is_valid} | score={report.confidence_score} | action={report.action}"
        )
        return report


validation_service = ValidationService()
