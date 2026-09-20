"""
Unit Test Suite for SQLAgent & Prompt Orchestration (Phase 9).
IMPORTANT: 100% of LLM calls are mocked. 0 external API calls made.
"""

import json
from unittest.mock import AsyncMock, patch
import pytest

from app.ai.llm.models import LLMResponse
from app.ai.sql.agent import SQLAgent
from app.ai.sql.exceptions import SQLValidationError


@pytest.mark.asyncio
async def test_sql_agent_successful_generation():
    """Verify SQLAgent translates question into validated SQLGenerationResult."""
    mock_llm_text = json.dumps({
        "sql": "SELECT store_id, SUM(total_amount) AS revenue FROM sales_transactions GROUP BY store_id;",
        "explanation": "Calculates total revenue aggregated by store.",
        "tables_used": ["sales_transactions"],
        "columns_used": ["store_id", "total_amount"],
    })

    mock_llm_response = LLMResponse(
        content=mock_llm_text,
        model="gpt-4o",
        provider="openai",
    )

    agent = SQLAgent()
    with patch("app.ai.llm.service.llm_service.generate", new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = mock_llm_response

        res = await agent.generate_sql(
            question="What is total revenue by store?",
            workspace_id="ws-test",
        )

        assert res.sql == "SELECT store_id, SUM(total_amount) AS revenue FROM sales_transactions GROUP BY store_id"
        assert res.explanation == "Calculates total revenue aggregated by store."
        assert res.tables_used == ["sales_transactions"]
        assert mock_generate.call_count == 1


@pytest.mark.asyncio
async def test_sql_agent_retry_on_invalid_sql():
    """Verify SQLAgent retries generation when first LLM attempt produces prohibited SQL."""
    invalid_llm_text = json.dumps({
        "sql": "DELETE FROM sales_transactions; SELECT * FROM stores;",
        "explanation": "Attempted illegal delete.",
        "tables_used": ["sales_transactions"],
        "columns_used": [],
    })

    valid_llm_text = json.dumps({
        "sql": "SELECT * FROM stores;",
        "explanation": "Returns all stores.",
        "tables_used": ["stores"],
        "columns_used": [],
    })

    agent = SQLAgent()
    with patch("app.ai.llm.service.llm_service.generate", new_callable=AsyncMock) as mock_generate:
        mock_generate.side_effect = [
            LLMResponse(content=invalid_llm_text, model="gpt-4o", provider="openai"),
            LLMResponse(content=valid_llm_text, model="gpt-4o", provider="openai"),
        ]

        res = await agent.generate_sql(
            question="List all stores.",
            workspace_id="ws-test",
        )

        assert res.sql == "SELECT * FROM stores"
        assert mock_generate.call_count == 2
