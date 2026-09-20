"""
Visualization Agent for EMBIP (Phase 12).
Interfaces with Centralized LLMService to generate executive chart titles, subtitles,
and visual insights.
"""

import logging
from typing import Any, Dict, Optional

from app.ai.llm import LLMMessage, LLMRequest, ResponseFormat, llm_service
from app.ai.visualization.models import ChartType, VisualizationMetadata
from app.ai.visualization.prompts import VISUALIZATION_METADATA_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class VisualizationAgent:
    """Agent interface for generating chart titles and executive summary insights."""

    async def generate_metadata(
        self,
        question: str,
        chart_type: ChartType,
        data_sample: Any,
    ) -> Optional[VisualizationMetadata]:
        """
        Generates executive title, subtitle, and visual insight text.
        """
        try:
            prompt = (
                f"Business Question: '{question}'\n"
                f"Selected Chart Type: '{chart_type.value}'\n"
                f"Data Summary/Sample: {data_sample}\n\n"
                f"Generate executive chart title, subtitle, and 1-sentence insight."
            )

            request = LLMRequest(
                messages=[
                    LLMMessage(role="system", content=VISUALIZATION_METADATA_SYSTEM_PROMPT),
                    LLMMessage(role="user", content=prompt),
                ],
                temperature=0.2,
                max_tokens=250,
                response_format=ResponseFormat(
                    type="json_schema",
                    json_schema=VisualizationMetadata.model_json_schema(),
                ),
            )

            response = await llm_service.generate_structured(
                request=request,
                schema_cls=VisualizationMetadata,
            )

            logger.info(f"VisualizationAgent generated metadata: title='{response.title}'")
            return response
        except Exception as e:
            logger.warning(f"VisualizationAgent metadata generation failed: {str(e)}. Falling back to default titles.")
            return None


# Singleton Instance
visualization_agent = VisualizationAgent()
