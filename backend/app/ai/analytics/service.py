"""
Analytics Service for EMBIP (Phase 11).
High-level service interface coordinating input validation, operation registry execution,
provenance tracking, LLM explanation generation, and error handling.
"""

import logging
import time
from typing import Any, Dict, List, Optional

from app.ai.analytics.agent import analytics_agent
from app.ai.analytics.exceptions import AnalyticsError
from app.ai.analytics.models import (
    AnalyticsGroupResult,
    AnalyticsInput,
    AnalyticsProvenance,
    AnalyticsResult,
    AnalyticsSeriesPoint,
    AnalyticsSummary,
)
from app.ai.analytics.registry import get_operation_function
from app.ai.analytics.validators import analytics_validator

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Core Analytics Service executing deterministic calculations on structured datasets.
    """

    async def analyze(
        self,
        input_data: AnalyticsInput,
        question: Optional[str] = None,
        sql_request_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> AnalyticsResult:
        """
        Main entry point for analytical calculation execution.
        """
        start_time = time.time()
        rows_input = len(input_data.rows) if input_data.rows else 0
        provenance = AnalyticsProvenance(
            sql_request_id=sql_request_id,
            workspace_id=workspace_id,
            source_columns=input_data.columns or [],
            source_row_count=rows_input,
        )

        try:
            # 1. Classify operation if not specified
            if not input_data.operation or input_data.operation.strip() == "":
                if question and input_data.columns and input_data.rows:
                    classification = await analytics_agent.classify_intent(
                        question=question,
                        columns=input_data.columns,
                        sample_rows=input_data.rows[:2],
                    )
                    if classification:
                        input_data.operation = classification.operation
                        input_data.metric_column = input_data.metric_column or classification.metric_column
                        input_data.group_by = input_data.group_by or classification.group_by
                        input_data.time_column = input_data.time_column or classification.time_column
                        input_data.parameters.update(classification.parameters)

                # Fallback metric/group column inference if missing
                if input_data.rows:
                    first_row = input_data.rows[0]
                    if not input_data.metric_column:
                        num_cols = [k for k, v in first_row.items() if isinstance(v, (int, float)) and not isinstance(v, bool) and k.lower() != "id"]
                        if num_cols:
                            input_data.metric_column = num_cols[0]
                    if not input_data.group_by:
                        str_cols = [k for k, v in first_row.items() if isinstance(v, str) and k.lower() not in ["id", "uuid", "created_at", "transaction_date"]]
                        if str_cols:
                            input_data.group_by = str_cols[0]

                if not input_data.operation or input_data.operation.strip() == "":
                    if input_data.group_by and input_data.metric_column:
                        input_data.operation = "group_sum"
                    else:
                        input_data.operation = "sum" if input_data.metric_column else "count"

            # 2. Validate input and construct DataFrame
            df, op_name = analytics_validator.validate_and_prepare(input_data)

            # 3. Fetch registered operation function & execute
            func = get_operation_function(op_name)
            res_dict, warnings = func(
                df=df,
                metric_col=input_data.metric_column,
                group_by=input_data.group_by,
                time_col=input_data.time_column,
                parameters=input_data.parameters,
            )

            # 4. Extract structured outputs
            scalar_val = res_dict.get("value")
            rows_used = res_dict.get("rows_used", len(df))
            missing_vals = rows_input - rows_used

            groups_out: Optional[List[AnalyticsGroupResult]] = None
            if "groups" in res_dict and res_dict["groups"] is not None:
                groups_out = [AnalyticsGroupResult(**g) for g in res_dict["groups"]]

            series_out: Optional[List[AnalyticsSeriesPoint]] = None
            if "series" in res_dict and res_dict["series"] is not None:
                series_out = [AnalyticsSeriesPoint(**s) for s in res_dict["series"]]

            # Handle extra tabular outputs (e.g. top_n rows)
            metadata = {
                "execution_time_ms": round((time.time() - start_time) * 1000, 2),
                "metric_column": input_data.metric_column,
                "group_by": input_data.group_by,
                "time_column": input_data.time_column,
            }
            if "rows" in res_dict:
                metadata["table_rows"] = res_dict["rows"]
            if "val1" in res_dict:
                metadata["val1"] = res_dict["val1"]
                metadata["val2"] = res_dict["val2"]
            if "cagr" in res_dict or "years" in res_dict:
                metadata.update({k: v for k, v in res_dict.items() if k in ["beginning_value", "ending_value", "years"]})

            summary = AnalyticsSummary(
                rows_input=rows_input,
                rows_used=rows_used,
                missing_values=missing_vals,
                warnings=warnings,
            )

            # 5. Generate executive explanation
            explanation = None
            if question:
                comp_summary = scalar_val if scalar_val is not None else (groups_out or series_out or metadata.get("table_rows"))
                explanation = await analytics_agent.generate_explanation(
                    question=question,
                    operation=op_name,
                    computed_result=comp_summary,
                )

            status = "warning" if warnings else "success"
            return AnalyticsResult(
                operation=op_name,
                status=status,
                metric=input_data.metric_column,
                value=scalar_val,
                groups=groups_out,
                series=series_out,
                summary=summary,
                metadata=metadata,
                provenance=provenance,
                explanation=explanation,
            )

        except AnalyticsError as e:
            logger.error(f"AnalyticsService error: {str(e)}")
            return AnalyticsResult(
                operation=input_data.operation or "unknown",
                status="error",
                metric=input_data.metric_column,
                summary=AnalyticsSummary(rows_input=rows_input, rows_used=0, missing_values=rows_input, warnings=[str(e)]),
                provenance=provenance,
                error=str(e),
            )
        except Exception as e:
            logger.error(f"AnalyticsService unexpected error: {str(e)}", exc_info=True)
            return AnalyticsResult(
                operation=input_data.operation or "unknown",
                status="error",
                metric=input_data.metric_column,
                summary=AnalyticsSummary(rows_input=rows_input, rows_used=0, missing_values=rows_input, warnings=[f"Unexpected error: {str(e)}"]),
                provenance=provenance,
                error=str(e),
            )


# Singleton Instance
analytics_service = AnalyticsService()
