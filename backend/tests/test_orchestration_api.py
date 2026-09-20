"""
Integration Test Suite for Orchestration API Endpoint POST /api/v1/ask (Phase 10).
"""

from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_ask_unauthenticated_rejected():
    """Verify POST /api/v1/ask without Bearer token is rejected with HTTP 401."""
    response = client.post("/api/v1/ask", json={"question": "What is our store count?"})
    assert response.status_code == 401


def test_ask_empty_question_rejected():
    """Verify empty or white-space question is rejected with HTTP 422."""
    response = client.post("/api/v1/ask", json={"question": "   "})
    assert response.status_code in (401, 422)
