"""
Pydantic Schemas for EMBIP Validation & Guardrails Agent (Phase 13).
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class ValidationCheckResult(BaseModel):
    """Result of an individual validation check (e.g. AST Safety, Numerical Consistency, Citations, Contradiction)."""
    check_name: str = Field(..., description="Name of the validation check")
    passed: bool = Field(..., description="Whether the check passed without critical issues")
    score: float = Field(..., ge=0.0, le=1.0, description="Confidence/quality score for this check from 0.0 to 1.0")
    message: str = Field(..., description="Human-readable summary of the check result")
    details: Dict[str, Any] = Field(default_factory=dict, description="Structured diagnostics and details")


class ValidationReport(BaseModel):
    """Overall validation report for the executed workflow."""
    is_valid: bool = Field(..., description="True if overall validation meets safety & factual thresholds")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Overall weighted confidence score (0.0 to 1.0)")
    checks: List[ValidationCheckResult] = Field(default_factory=list, description="Individual check results")
    hallucinations_detected: List[str] = Field(default_factory=list, description="List of detected hallucinated claims/numbers")
    contradictions_detected: List[str] = Field(default_factory=list, description="List of detected dataset contradictions")
    warnings: List[str] = Field(default_factory=list, description="Non-fatal warnings or low-confidence indicators")
    action: Literal["pass", "retry", "flag"] = Field(
        ...,
        description="Action decision: 'pass' (proceed), 'retry' (loop back to planner), or 'flag' (output with warnings)"
    )


class ValidationRequest(BaseModel):
    """Input parameters passed into ValidationService."""
    question: str = Field(..., description="Original user question")
    plan: Optional[Dict[str, Any]] = Field(default=None, description="Planner Agent execution plan")
    sql_result: Optional[Dict[str, Any]] = Field(default=None, description="Phase 9 SQL Agent execution result")
    rag_result: Optional[Dict[str, Any]] = Field(default=None, description="Phase 8 RAG retrieval result")
    analytics_result: Optional[Dict[str, Any]] = Field(default=None, description="Phase 11 Analytics result")
    visualization_result: Optional[Dict[str, Any]] = Field(default=None, description="Phase 12 Visualization result")
