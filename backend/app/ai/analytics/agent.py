"""
Analytics Agent Class for EMBIP (Phase 11).
Uses Centralized LLMService to classify analytical intent and generate executive explanations.
Never executes Python code from LLM outputs.
"""

import logging
from typing import Any, Dict, List, Optional

from app.ai.analytics.models import AnalyticsIntentClassification
from app.ai.analytics.prompts import (
    ANALYTICS_EXPLANATION_SYSTEM_PROMPT,
    ANALYTICS_INTENT_SYSTEM_PROMPT,
)
from app.ai.llm import LLMMessage, LLMRequest, ResponseFormat, llm_service

logger = logging.getLogger(__name__)


class AnalyticsAgent:
    """Agent interface for classification and explanation generation using LLMService."""

    async def classify_intent(
        self,
        question: str,
        columns: List[str],
        sample_rows: List[Dict[str, Any]],
    ) -> Optional[AnalyticsIntentClassification]:
        """
        Interprets user question and dataset columns to select operation from registry.
        """
        try:
            prompt = (
                f"User Question: '{question}'\n"
                f"Available Dataset Columns: {columns}\n"
                f"Sample Rows (First 2): {sample_rows[:2]}\n\n"
                f"Classify the analytical intent and select the appropriate operation."
            )

            request = LLMRequest(
                messages=[
                    LLMMessage(role="system", content=ANALYTICS_INTENT_SYSTEM_PROMPT),
                    LLMMessage(role="user", content=prompt),
                ],
                temperature=0.0,
                response_format=ResponseFormat(
                    type="json_schema",
                    json_schema=AnalyticsIntentClassification.model_json_schema(),
                ),
            )

            response = await llm_service.generate_structured(
                request=request,
                schema_cls=AnalyticsIntentClassification,
            )

            logger.info(f"AnalyticsAgent classified intent: op='{response.operation}', metric='{response.metric_column}'")
            return response
        except Exception as e:
            logger.warning(f"AnalyticsAgent intent classification failed: {str(e)}. Falling back to deterministic heuristics.")
            return None

    async def generate_explanation(
        self,
        question: str,
        operation: str,
        computed_result: Any,
    ) -> str:
        """
        Generates a 1-2 sentence executive explanation of the computed numerical result.
        """
        try:
            prompt = (
                f"User Question: '{question}'\n"
                f"Operation: '{operation}'\n"
                f"Computed Numerical Results: {computed_result}\n\n"
                f"Provide a 1-2 sentence executive explanation."
            )

            request = LLMRequest(
                messages=[
                    LLMMessage(role="system", content=ANALYTICS_EXPLANATION_SYSTEM_PROMPT),
                    LLMMessage(role="user", content=prompt),
                ],
                temperature=0.2,
                max_tokens=200,
            )

            response = await llm_service.generate(request)
            return response.content.strip()
        except Exception as e:
            logger.warning(f"AnalyticsAgent explanation generation failed: {str(e)}.")
            return f"Analysis completed for operation '{operation}' with result: {computed_result}."


# Singleton Instance
analytics_agent = AnalyticsAgent()
