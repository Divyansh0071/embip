"""
Visualization Service for EMBIP (Phase 12).
High-level service entry point orchestrating chart decision matrix selection,
Recharts specification generation, server-side validation, and LLM metadata enrichment.
"""

import logging
from typing import Any, Dict, List, Optional

from app.ai.visualization.agent import visualization_agent
from app.ai.visualization.decision_matrix import chart_decision_matrix
from app.ai.visualization.exceptions import VisualizationError
from app.ai.visualization.generator import recharts_spec_generator
from app.ai.visualization.models import (
    ChartType,
    RechartsSpec,
    VisualizationRequest,
    VisualizationResult,
)
from app.ai.visualization.validators import visualization_validator

logger = logging.getLogger(__name__)


class VisualizationService:
    """Core Service managing dynamic chart specification generation and validation."""

    async def generate_spec(
        self,
        question: str,
        sql_result: Optional[Dict[str, Any]] = None,
        analytics_result: Optional[Dict[str, Any]] = None,
        preferred_chart_type: Optional[ChartType] = None,
    ) -> VisualizationResult:
        """
        Generates validated RechartsSpec object from SQL and Analytics outputs.
        """
        rows: List[Dict[str, Any]] = (sql_result or {}).get("rows") or []
        columns: List[str] = (sql_result or {}).get("columns") or []

        # If analytics output exists and has tabular rows, prefer analytics data
        if analytics_result and analytics_result.get("status") in ["success", "warning"]:
            if analytics_result.get("metadata", {}).get("table_rows"):
                rows = analytics_result["metadata"]["table_rows"]

        if not rows and not (analytics_result and analytics_result.get("value") is not None):
            return VisualizationResult(
                status="skipped",
                error="No dataset rows or numerical metrics available to visualize.",
                explanation="Visualization skipped due to empty query results.",
            )

        try:
            # 1. Select Chart Type via Decision Matrix
            selected_type = chart_decision_matrix.select_chart_type(
                rows=rows,
                columns=columns,
                analytics_result=analytics_result,
                preferred_type=preferred_chart_type,
            )

            # 2. Default Titles
            default_title = question.strip().rstrip("?").title()
            if len(default_title) > 60:
                default_title = default_title[:57] + "..."

            # 3. Generate Base Recharts Spec
            spec = recharts_spec_generator.generate_spec(
                chart_type=selected_type,
                rows=rows,
                columns=columns,
                title=default_title,
                analytics_result=analytics_result,
            )

            # 4. Server-Side Validation
            visualization_validator.validate_spec(spec)

            # 5. Optional LLM Title / Subtitle Enrichment
            metadata = await visualization_agent.generate_metadata(
                question=question,
                chart_type=selected_type,
                data_sample=spec.data[:3],
            )
            if metadata:
                spec.title = metadata.title
                spec.subtitle = metadata.subtitle
                explanation = metadata.insight
            else:
                explanation = f"Generated {selected_type.value.replace('_', ' ')} visual representation for analysis."

            return VisualizationResult(
                status="success",
                spec=spec,
                explanation=explanation,
            )

        except VisualizationError as e:
            logger.error(f"VisualizationService validation error: {str(e)}")
            return VisualizationResult(
                status="error",
                error=str(e),
            )
        except Exception as e:
            logger.error(f"VisualizationService unexpected error: {str(e)}", exc_info=True)
            return VisualizationResult(
                status="error",
                error=f"Visualization generation failed: {str(e)}",
            )


# Singleton Instance
visualization_service = VisualizationService()
