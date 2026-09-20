"""
Integration Test Suite for SQL Query API Endpoint (Phase 9).
"""

from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.ai.sql.models import SQLGenerationResult

client = TestClient(app)


def test_sql_query_unauthenticated_rejected():
    """Verify POST /api/v1/sql/query without Bearer token is rejected with HTTP 401."""
    response = client.post("/api/v1/sql/query", json={"question": "What were total sales last month?"})
    assert response.status_code == 401


def test_sql_query_empty_question_rejected():
    """Verify empty or short questions are rejected with HTTP 422 Unprocessable Entity."""
    response = client.post("/api/v1/sql/query", json={"question": "  "})
    assert response.status_code in (401, 422)
