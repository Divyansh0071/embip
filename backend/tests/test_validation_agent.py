"""
Unit Tests for ValidationAgent & ValidationService (Phase 13).
"""

import pytest
from unittest.mock import AsyncMock, patch

from app.ai.validation.models import ValidationRequest
from app.ai.validation.service import validation_service


@pytest.mark.asyncio
async def test_validation_service_full_pass():
    req = ValidationRequest(
        question="What was total revenue?",
        sql_result={"status": "success", "query": "SELECT SUM(amount) FROM sales", "rows": [{"sum": 100000}], "row_count": 1},
        analytics_result={"explanation": "Total sales revenue is $100,000."},
    )

    report = await validation_service.validate(req)
    assert report.is_valid is True
    assert report.confidence_score >= 0.85
    assert report.action == "pass"
    assert len(report.hallucinations_detected) == 0


@pytest.mark.asyncio
async def test_validation_service_retry_on_ast_violation():
    req = ValidationRequest(
        question="Delete all records",
        sql_result={"status": "success", "query": "DELETE FROM sales", "rows": []},
    )

    report = await validation_service.validate(req)
    assert report.is_valid is False
    assert report.action == "retry"
    assert any("forbidden" in w.lower() or "ast" in w.lower() for w in report.warnings)


@pytest.mark.asyncio
async def test_validation_service_flag_on_hallucination():
    req = ValidationRequest(
        question="Show revenue",
        sql_result={"status": "success", "query": "SELECT 50000 AS rev", "rows": [{"rev": 50000}]},
        analytics_result={"explanation": "Revenue was $888,888."},  # Unsupported figure
    )

    report = await validation_service.validate(req)
    assert report.is_valid is False
    assert len(report.hallucinations_detected) > 0
    assert report.action in ["retry", "flag"]
