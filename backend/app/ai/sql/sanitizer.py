"""
SQL Sanitizer & Normalizer for EMBIP AI Engine (Phase 9).
Cleans and normalizes LLM-generated SQL strings before AST validation and execution.
"""

import re
from app.core.config import settings
from app.ai.sql.exceptions import SQLValidationError


class SQLSanitizer:
    """
    Sanitizes and normalizes generated SQL string inputs.
    """

    def sanitize(self, raw_sql: str) -> str:
        """
        Cleans markdown formatting, normalizes whitespace, strips trailing semicolons,
        and enforces length limits.
        """
        if not raw_sql or not raw_sql.strip():
            raise SQLValidationError("Cannot sanitize empty or blank SQL string.")

        sql = raw_sql.strip()

        # 1. Strip markdown code block wrapping if present
        if sql.startswith("```"):
            sql = re.sub(r"^```(?:sql|JSON|json)?\n?", "", sql, flags=re.IGNORECASE)
            sql = re.sub(r"\n?```$", "", sql).strip()

        # 2. Strip trailing semicolons (we enforce single statement execution without ;)
        sql = sql.rstrip(";").strip()

        # 3. Check query length limit
        if len(sql) > settings.SQL_MAX_QUERY_LENGTH:
            raise SQLValidationError(
                f"Generated SQL length ({len(sql)} chars) exceeds maximum allowed threshold of {settings.SQL_MAX_QUERY_LENGTH} chars."
            )

        return sql


# Singleton Instance
sql_sanitizer = SQLSanitizer()
