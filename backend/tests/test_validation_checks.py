"""
Unit Tests for EMBIP Validation & Guardrails Pure Checks (Phase 13).
"""

import pytest
from app.ai.validation.checks import (
    check_ast_safety_audit,
    check_contradiction_detection,
    check_numerical_consistency,
    check_rag_citation_integrity,
    extract_numbers_from_text,
)


def test_extract_numbers_from_text():
    text = "Revenue in Q3 2024 was $1,250,500.50 with a growth rate of 12.5%."
    nums = extract_numbers_from_text(text)
    assert 2024.0 in nums
    assert 1250500.5 in nums
    assert 12.5 in nums


def test_check_ast_safety_audit_pass():
    res = check_ast_safety_audit({
        "status": "success",
        "query": "SELECT name, total FROM sales WHERE amount > 100",
    })
    assert res.passed is True
    assert res.score == 1.0


def test_check_ast_safety_audit_fail():
    res = check_ast_safety_audit({
        "status": "success",
        "query": "DROP TABLE sales; SELECT * FROM users",
    })
    assert res.passed is False
    assert res.score == 0.0
    assert "prohibited" in res.message.lower()



def test_check_numerical_consistency_pass():
    sql_res = {"rows": [{"revenue": 500000}], "row_count": 1}
    analytics_res = {"results": {"total": 500000}, "summary": {}}
    texts = ["Total revenue calculated is $500,000."]
    
    res = check_numerical_consistency(sql_res, analytics_res, texts)
    assert res.passed is True
    assert res.score == 1.0


def test_check_numerical_consistency_hallucination():
    sql_res = {"rows": [{"revenue": 500000}], "row_count": 1}
    analytics_res = {"results": {"total": 500000}, "summary": {}}
    texts = ["Total revenue calculated is $999,999."] # Unsupported number
    
    res = check_numerical_consistency(sql_res, analytics_res, texts)
    assert res.passed is False
    assert 999999.0 in res.details["unsupported_numbers"]


def test_check_rag_citation_integrity():
    rag_res = {
        "chunks": [{"content": "Our official return policy allows returns within 30 days of purchase."}]
    }
    valid_texts = ['The policy states "returns within 30 days of purchase."']
    res_valid = check_rag_citation_integrity(rag_res, valid_texts)
    assert res_valid.passed is True

    invalid_texts = ['The policy states "returns within 900 days of purchase without receipt."']
    res_invalid = check_rag_citation_integrity(rag_res, invalid_texts)
    assert res_invalid.passed is False
    assert len(res_invalid.details["uncited_quotes"]) > 0


def test_check_contradiction_detection():
    sql_res = {"rows": [{"total_revenue": 5000000}]}
    rag_res = {"chunks": [{"content": "In 2024, our reported annual revenue was 1500000."}]}

    res = check_contradiction_detection(sql_res, rag_res)
    assert res.passed is False
    assert len(res.details["contradictions"]) > 0
