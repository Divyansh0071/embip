"""
SQL Agent for EMBIP AI Architecture (Phase 9).
Coordinates schema context retrieval, LLM SQL generation via centralized LLMService,
AST security validation, and single-attempt retry correction loops.
"""

import json
import logging
from typing import Optional

from app.core.config import settings
from app.ai.llm import llm_service
from app.ai.llm.models import LLMMessage, LLMRequest
from app.ai.sql.exceptions import SQLAgentError, SQLValidationError
from app.ai.sql.models import SQLGenerationResult
from app.ai.sql.prompts import (
    SQL_SYSTEM_PROMPT,
    build_sql_retry_prompt,
    build_sql_user_prompt,
)
from app.ai.sql.sanitizer import sql_sanitizer
from app.ai.sql.schema_context import schema_context_service
from app.ai.sql.validator import sql_validator

logger = logging.getLogger(__name__)


class SQLAgent:
    """
    Agent responsible for translating business questions into validated read-only SQL queries.
    """

    def _parse_llm_json(self, raw_text: str) -> SQLGenerationResult:
        """Parses raw text response from LLM into SQLGenerationResult model."""
        text_content = raw_text.strip()
        # Clean markdown wrappers if present
        if text_content.startswith("```"):
            lines = text_content.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text_content = "\n".join(lines).strip()

        try:
            data = json.loads(text_content)
            return SQLGenerationResult(
                sql=data.get("sql", ""),
                explanation=data.get("explanation", "Query generated to calculate requested business metrics."),
                tables_used=data.get("tables_used", []),
                columns_used=data.get("columns_used", []),
            )
        except json.JSONDecodeError as e:
            raise SQLValidationError(f"LLM returned invalid non-JSON output for SQL query: {str(e)}")

    async def generate_sql(
        self,
        question: str,
        workspace_id: str,
        provider_name: Optional[str] = None,
    ) -> SQLGenerationResult:
        """
        Translates user business question into validated read-only SQL with validation retries.
        """
        schema_context = schema_context_service.get_formatted_schema_context()
        user_prompt = build_sql_user_prompt(question, schema_context)

        messages = [
            LLMMessage(role="system", content=SQL_SYSTEM_PROMPT),
            LLMMessage(role="user", content=user_prompt),
        ]

        max_retries = settings.SQL_MAX_RETRIES
        last_error_reasons: list = []
        last_failed_sql: str = ""

        for attempt in range(max_retries + 1):
            if attempt > 0:
                logger.warning(f"SQL Generation Retry Attempt {attempt}/{max_retries} due to validation errors.")
                retry_user_prompt = build_sql_retry_prompt(
                    question=question,
                    schema_context=schema_context,
                    failed_sql=last_failed_sql,
                    error_reasons=last_error_reasons,
                )
                messages = [
                    LLMMessage(role="system", content=SQL_SYSTEM_PROMPT),
                    LLMMessage(role="user", content=retry_user_prompt),
                ]

            llm_req = LLMRequest(
                messages=messages,
                temperature=0.0,
                max_tokens=1500,
            )

            llm_resp = await llm_service.generate(llm_req, provider_name=provider_name)
            gen_result = self._parse_llm_json(llm_resp.content)

            # Sanitize and Validate generated SQL
            try:
                sanitized_sql = sql_sanitizer.sanitize(gen_result.sql)
                gen_result.sql = sanitized_sql
            except SQLValidationError as e:
                last_failed_sql = gen_result.sql
                last_error_reasons = [e.message]
                continue

            is_valid, reasons = sql_validator.validate(gen_result.sql)
            if is_valid:
                logger.info(f"SQL Agent Success | tables={gen_result.tables_used} sql='{gen_result.sql[:100]}...'")
                return gen_result

            last_failed_sql = gen_result.sql
            last_error_reasons = reasons

        # If retries exhausted without valid SQL
        error_msg = f"SQL Agent failed to generate valid read-only SQL query after {max_retries} retries: {'; '.join(last_error_reasons)}"
        logger.error(f"SQL Agent Validation Exhausted | error='{error_msg}'")
        raise SQLValidationError(error_msg, invalid_reasons=last_error_reasons)


# Singleton Instance
sql_agent = SQLAgent()
