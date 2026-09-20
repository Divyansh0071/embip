"""
Unit Test Suite for PlannerAgent Intent Classification (Phase 10).
IMPORTANT: All LLM calls are 100% mocked. 0 paid API calls made.
"""

import json
from unittest.mock import AsyncMock, patch
import pytest

from app.ai.llm.models import LLMResponse
from app.ai.orchestration.exceptions import PlannerError
from app.ai.orchestration.planner import PlannerAgent


@pytest.mark.asyncio
async def test_planner_agent_sql_intent():
    """Verify PlannerAgent classifies database question as requiring SQL capability."""
    mock_json = json.dumps({
        "intent": "sql_query",
        "requires_sql": True,
        "requires_rag": False,
        "requires_analytics": False,
        "requires_visualization": False,
        "reason": "Question asks for store revenue metric stored in database.",
    })

    agent = PlannerAgent()
    with patch("app.ai.llm.service.llm_service.generate", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = LLMResponse(content=mock_json, model="gpt-4o", provider="openai")

        plan = await agent.plan("What was total revenue by store in 2024?")

        assert plan.intent == "sql_query"
        assert plan.requires_sql is True
        assert plan.requires_rag is False
        assert plan.requires_analytics is False
        assert plan.requires_visualization is False


@pytest.mark.asyncio
async def test_planner_agent_combined_intent():
    """Verify PlannerAgent classifies combined question requiring both SQL and RAG."""
    mock_json = json.dumps({
        "intent": "combined",
        "requires_sql": True,
        "requires_rag": True,
        "requires_analytics": False,
        "requires_visualization": False,
        "reason": "Question asks for sales numbers and return policy document context.",
    })

    agent = PlannerAgent()
    with patch("app.ai.llm.service.llm_service.generate", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = LLMResponse(content=mock_json, model="gpt-4o", provider="openai")

        plan = await agent.plan("What was revenue last quarter and what does our return policy say?")

        assert plan.intent == "combined"
        assert plan.requires_sql is True
        assert plan.requires_rag is True


@pytest.mark.asyncio
async def test_planner_agent_invalid_json_raises_planner_error():
    """Verify non-JSON response from LLM raises PlannerError."""
    agent = PlannerAgent()
    with patch("app.ai.llm.service.llm_service.generate", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = LLMResponse(content="Sorry, I cannot answer.", model="gpt-4o", provider="openai")

        with pytest.raises(PlannerError):
            await agent.plan("Some question")
