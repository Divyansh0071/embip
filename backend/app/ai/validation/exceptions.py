"""
Custom Exception Classes for EMBIP Validation & Guardrails Agent (Phase 13).
"""

class ValidationError(Exception):
    """Base exception for all validation and guardrail errors."""
    pass


class HallucinationError(ValidationError):
    """Raised when an LLM summary/explanation includes figures or factual claims unsupported by raw source data."""
    pass


class ContradictionError(ValidationError):
    """Raised when a contradiction is detected between structured SQL metrics and RAG text documents."""
    pass


class UncitedClaimError(ValidationError):
    """Raised when a quote or citation in the response cannot be found within retrieved document chunks."""
    pass


class ASTSecurityViolationError(ValidationError):
    """Raised when a generated or executed SQL query fails AST security audit."""
    pass
