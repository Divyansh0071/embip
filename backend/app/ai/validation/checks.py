"""
Pure Deterministic Check Routines for EMBIP Validation & Guardrails Agent (Phase 13).
Performs AST safety auditing, numerical consistency verification, citation integrity checks, and contradiction detection.
"""

import re
from typing import Any, Dict, List, Optional, Set
from app.ai.validation.models import ValidationCheckResult


def extract_numbers_from_text(text: str) -> List[float]:
    """
    Extracts numerical values from text, stripping common formatting ($ , % etc.).
    Ignores dates/years (e.g. 2024, 2025, 2026) when evaluating standard numbers.
    """
    if not text:
        return []

    # Pattern matches integers, floats, currency ($1,234.56), percentages (45.2%)
    pattern = r"[\$€£]?\b\d+(?:,\d{3})*(?:\.\d+)?%?\b"
    matches = re.findall(pattern, text)

    extracted: List[float] = []
    for raw in matches:
        clean = raw.replace("$", "").replace("€", "").replace("£", "").replace("%", "").replace(",", "")
        try:
            val = float(clean)
            extracted.append(val)
        except ValueError:
            continue
    return extracted



def extract_numbers_from_structured_data(data: Any) -> Set[float]:
    """
    Recursively extracts all numerical values from SQL rows, columns, analytics outputs, etc.
    """
    numbers: Set[float] = set()

    if isinstance(data, (int, float)):
        numbers.add(float(data))
    elif isinstance(data, str):
        for num in extract_numbers_from_text(data):
            numbers.add(num)
    elif isinstance(data, dict):
        for v in data.values():
            numbers.update(extract_numbers_from_structured_data(v))
    elif isinstance(data, (list, tuple, set)):
        for item in data:
            numbers.update(extract_numbers_from_structured_data(item))

    return numbers


def check_ast_safety_audit(sql_result: Optional[Dict[str, Any]]) -> ValidationCheckResult:
    """
    Validates that executed SQL query passed AST security parsing and read-only checks.
    """
    if not sql_result or sql_result.get("status") == "skipped":
        return ValidationCheckResult(
            check_name="ast_safety_audit",
            passed=True,
            score=1.0,
            message="SQL execution skipped or not required. AST safety check passed.",
            details={"status": "skipped"}
        )

    if sql_result.get("status") == "error":
        error_msg = sql_result.get("error", "Unknown SQL error")
        is_security = "security" in error_msg.lower() or "ast" in error_msg.lower() or "read-only" in error_msg.lower()
        return ValidationCheckResult(
            check_name="ast_safety_audit",
            passed=not is_security,
            score=0.0 if is_security else 0.5,
            message=f"SQL error detected: {error_msg}",
            details={"error": error_msg, "is_security_violation": is_security}
        )

    query = sql_result.get("query", "")
    forbidden = ["insert", "update", "delete", "drop", "alter", "truncate", "create", "grant"]
    query_lower = query.lower()
    violations = [kw for kw in forbidden if re.search(rf"\b{kw}\b", query_lower)]

    if violations:
        return ValidationCheckResult(
            check_name="ast_safety_audit",
            passed=False,
            score=0.0,
            message=f"AST Security Violation: Query contains prohibited keyword(s): {', '.join(violations)}",
            details={"forbidden_keywords": violations, "query": query}
        )

    return ValidationCheckResult(
        check_name="ast_safety_audit",
        passed=True,
        score=1.0,
        message="SQL query passed AST security audit and read-only policy.",
        details={"query": query}
    )


def check_numerical_consistency(
    sql_result: Optional[Dict[str, Any]],
    analytics_result: Optional[Dict[str, Any]],
    texts_to_check: List[str]
) -> ValidationCheckResult:
    """
    Cross-checks all numerical claims in LLM text explanations against ground-truth data in SQL/Analytics.
    """
    ground_truth_numbers = set()
    if sql_result:
        ground_truth_numbers.update(extract_numbers_from_structured_data(sql_result.get("rows")))
        ground_truth_numbers.update(extract_numbers_from_structured_data(sql_result.get("row_count")))
    if analytics_result:
        ground_truth_numbers.update(extract_numbers_from_structured_data(analytics_result.get("results")))
        ground_truth_numbers.update(extract_numbers_from_structured_data(analytics_result.get("summary")))

    # Collect numbers from text
    unsupported_numbers: List[float] = []
    total_text_numbers = 0

    for text in texts_to_check:
        text_nums = extract_numbers_from_text(text)
        for num in text_nums:
            total_text_numbers += 1
            # Allow common integers 0-10, years (2020-2030), or exact matches / close floats (within 0.01%)
            if 0 <= num <= 10 or 2020 <= num <= 2030:
                continue
            
            is_supported = any(
                abs(num - gt) < 1e-4 or (gt != 0 and abs((num - gt) / gt) < 1e-4)
                for gt in ground_truth_numbers
            )
            if not is_supported and ground_truth_numbers:
                unsupported_numbers.append(num)

    if unsupported_numbers:
        score = max(0.0, 1.0 - (len(unsupported_numbers) / max(total_text_numbers, 1)))
        return ValidationCheckResult(
            check_name="numerical_consistency",
            passed=False,
            score=round(score, 2),
            message=f"Numerical inconsistency: {len(unsupported_numbers)} unsupported figure(s) detected: {unsupported_numbers}",
            details={"unsupported_numbers": unsupported_numbers, "total_text_numbers": total_text_numbers}
        )

    return ValidationCheckResult(
        check_name="numerical_consistency",
        passed=True,
        score=1.0,
        message="All numerical claims in text explanations match raw SQL / Analytics dataset ground truth.",
        details={"total_text_numbers": total_text_numbers}
    )


def check_rag_citation_integrity(
    rag_result: Optional[Dict[str, Any]],
    texts_to_check: List[str]
) -> ValidationCheckResult:
    """
    Verifies quotes/citations in text match retrieved document chunks in RAG result.
    """
    if not rag_result or not rag_result.get("chunks"):
        return ValidationCheckResult(
            check_name="rag_citation_integrity",
            passed=True,
            score=1.0,
            message="No RAG documents involved or empty retrieval.",
            details={"status": "skipped"}
        )

    chunks = rag_result.get("chunks", [])
    chunk_texts = [c.get("content", "").lower() for c in chunks if isinstance(c, dict)]
    all_chunk_text = " ".join(chunk_texts)

    uncited_quotes: List[str] = []
    # Pattern to extract quoted strings "like this" or 'like this'
    quote_pattern = r'["\']([^"\']+)["\']'

    for text in texts_to_check:
        quotes = re.findall(quote_pattern, text)
        for q in quotes:
            if len(q.strip()) >= 15:
                if q.strip().lower() not in all_chunk_text:
                    uncited_quotes.append(q.strip())


    if uncited_quotes:
        return ValidationCheckResult(
            check_name="rag_citation_integrity",
            passed=False,
            score=0.5,
            message=f"Citation integrity warning: {len(uncited_quotes)} quote(s) could not be verified in source document chunks.",
            details={"uncited_quotes": uncited_quotes}
        )

    return ValidationCheckResult(
        check_name="rag_citation_integrity",
        passed=True,
        score=1.0,
        message="All quoted text citations verified against retrieved document chunks.",
        details={"verified_chunks_count": len(chunks)}
    )


def check_contradiction_detection(
    sql_result: Optional[Dict[str, Any]],
    rag_result: Optional[Dict[str, Any]]
) -> ValidationCheckResult:
    """
    Detects potential contradictions between SQL numeric results and RAG text document figures.
    """
    if not sql_result or not rag_result or not sql_result.get("rows") or not rag_result.get("chunks"):
        return ValidationCheckResult(
            check_name="contradiction_detection",
            passed=True,
            score=1.0,
            message="Insufficient dual-source (SQL + RAG) data to check for dataset contradiction.",
            details={"status": "skipped"}
        )

    sql_numbers = extract_numbers_from_structured_data(sql_result.get("rows"))
    rag_text = " ".join([c.get("content", "") for c in rag_result.get("chunks", []) if isinstance(c, dict)])
    rag_numbers = extract_numbers_from_text(rag_text)

    # Filter out trivial small numbers/years
    significant_sql = {n for n in sql_numbers if n > 10 and not (2020 <= n <= 2030)}
    significant_rag = {n for n in rag_numbers if n > 10 and not (2020 <= n <= 2030)}

    # If both SQL and RAG contain numbers, but there's 0 overlap and both are large datasets
    contradictions: List[str] = []
    if significant_sql and significant_rag and not (significant_sql & significant_rag):
        # Potential discrepancy between structured DB metrics and document narrative
        msg = f"Discrepancy: Structured SQL metrics {list(significant_sql)[:3]} do not match unstructured document figures {list(significant_rag)[:3]}"
        contradictions.append(msg)

    if contradictions:
        return ValidationCheckResult(
            check_name="contradiction_detection",
            passed=False,
            score=0.6,
            message="Potential contradiction between database query metrics and document text figures.",
            details={"contradictions": contradictions}
        )

    return ValidationCheckResult(
        check_name="contradiction_detection",
        passed=True,
        score=1.0,
        message="No contradictions detected between SQL database results and RAG documents.",
        details={}
    )
