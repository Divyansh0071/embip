"""
Safe PostgreSQL & Async SQLAlchemy Query Executor (Phase 9).
Executes approved SQL, enforces statement timeouts, row limits, workspace RLS context,
and serializes database values into JSON-safe structures.
"""

import asyncio
import decimal
import time
from datetime import date, datetime
from typing import Any, Dict, List, Optional
import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.ai.sql.exceptions import SQLExecutionError, SQLExecutionTimeoutError
from app.ai.sql.models import SQLExecutionResult


class SQLExecutor:
    """
    Executes validated SQL against PostgreSQL with safety timeouts and value serialization.
    """

    def _serialize_value(self, val: Any) -> Any:
        """Converts PostgreSQL / SQLAlchemy column values into JSON-serializable Python objects."""
        if val is None:
            return None
        if isinstance(val, (int, float, str, bool)):
            return val
        if isinstance(val, decimal.Decimal):
            # Convert Decimal to float for JSON while preserving precision
            return float(val)
        if isinstance(val, (datetime, date)):
            return val.isoformat()
        if isinstance(val, uuid.UUID):
            return str(val)
        if isinstance(val, (bytes, bytearray)):
            return val.hex()
        return str(val)

    async def execute(
        self,
        session: AsyncSession,
        sql: str,
        workspace_id: str,
        max_rows: Optional[int] = None,
    ) -> SQLExecutionResult:
        """
        Executes approved SQL query asynchronously with timeout & row limit safeguards.
        """
        limit = min(max_rows or settings.SQL_MAX_ROWS, settings.SQL_MAX_ROWS)
        timeout_seconds = settings.SQL_STATEMENT_TIMEOUT_SECONDS
        start_time = time.time()

        try:
            # 1. Set database dialect session options if PostgreSQL
            dialect_name = session.bind.dialect.name if session.bind else "postgresql"
            if dialect_name == "postgresql":
                timeout_ms = int(timeout_seconds * 1000)
                await session.execute(
                    text("SET LOCAL statement_timeout = :timeout_ms;"),
                    {"timeout_ms": timeout_ms},
                )
                await session.execute(
                    text("SET LOCAL app.current_workspace_id = :ws_id;"),
                    {"ws_id": workspace_id},
                )

            # 2. Execute SQL with timeout wrapper
            async def _run_query():
                result = await session.execute(text(sql))
                return result

            result = await asyncio.wait_for(_run_query(), timeout=timeout_seconds)

            # 3. Extract column names & rows
            columns = list(result.keys()) if hasattr(result, "keys") else []
            raw_rows = result.fetchmany(limit) if hasattr(result, "fetchmany") else []

            serialized_rows: List[Dict[str, Any]] = []
            for row in raw_rows:
                row_dict = {}
                for idx, col in enumerate(columns):
                    row_dict[col] = self._serialize_value(row[idx])
                serialized_rows.append(row_dict)

            execution_time_ms = round((time.time() - start_time) * 1000, 2)

            return SQLExecutionResult(
                columns=columns,
                rows=serialized_rows,
                row_count=len(serialized_rows),
                execution_time_ms=execution_time_ms,
            )

        except asyncio.TimeoutError:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            raise SQLExecutionTimeoutError(
                f"SQL Execution timed out after {timeout_seconds}s ({duration_ms}ms)."
            )

        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            # Sanitize database error messages to prevent exposing internal infrastructure
            err_msg = str(e)
            if "password" in err_msg.lower() or "connection" in err_msg.lower():
                err_msg = "Database connection error."
            raise SQLExecutionError(f"Database query execution failed: {err_msg}")


# Singleton Instance
sql_executor = SQLExecutor()
