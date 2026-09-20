"""
High-Level SQL Service Orchestrator (Phase 9).
Coordinates SQL Agent generation, SQLExecutor database execution,
workspace multi-tenant isolation, and query audit logging.
"""

import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.sql.agent import SQLAgent, sql_agent
from app.ai.sql.exceptions import SQLAgentError, SQLValidationError
from app.ai.sql.executor import SQLExecutor, sql_executor
from app.ai.sql.models import SQLQueryRequest, SQLQueryResponse
from app.models.system import Query, QueryExecution

logger = logging.getLogger(__name__)


class SQLService:
    """
    Orchestrator managing natural language business queries, SQL generation,
    execution, audit logging, and error handling.
    """

    def __init__(
        self,
        agent: Optional[SQLAgent] = None,
        executor: Optional[SQLExecutor] = None,
    ):
        self.agent = agent or sql_agent
        self.executor = executor or sql_executor

    async def execute_question(
        self,
        session: AsyncSession,
        request: SQLQueryRequest,
        workspace_id: str,
        user_id: Optional[str] = None,
        provider_name: Optional[str] = None,
    ) -> SQLQueryResponse:
        """
        Processes natural language question, generates safe SQL, executes against PostgreSQL,
        logs query execution, and returns structured API response.
        """
        query_record = Query(
            workspace_id=workspace_id,
            user_id=user_id,
            natural_query=request.question,
            status="pending",
        )
        session.add(query_record)
        await session.flush()

        try:
            # 1. Generate & validate SQL via SQLAgent
            gen_result = await self.agent.generate_sql(
                question=request.question,
                workspace_id=workspace_id,
                provider_name=provider_name,
            )

            # 2. Execute SQL query against database
            exec_result = await self.executor.execute(
                session=session,
                sql=gen_result.sql,
                workspace_id=workspace_id,
                max_rows=request.max_rows,
            )

            # 3. Update query audit records
            query_record.status = "completed"
            query_record.execution_time_ms = int(exec_result.execution_time_ms)

            query_exec = QueryExecution(
                query_id=query_record.id,
                generated_sql=gen_result.sql,
                sql_valid=True,
                analytics_summary={
                    "explanation": gen_result.explanation,
                    "tables_used": gen_result.tables_used,
                    "columns_used": gen_result.columns_used,
                    "row_count": exec_result.row_count,
                },
            )
            session.add(query_exec)
            await session.commit()

            status_str = "success" if exec_result.row_count > 0 else "no_data"

            return SQLQueryResponse(
                question=request.question,
                sql=gen_result.sql,
                explanation=gen_result.explanation,
                tables_used=gen_result.tables_used,
                columns=exec_result.columns,
                rows=exec_result.rows,
                row_count=exec_result.row_count,
                execution_time_ms=exec_result.execution_time_ms,
                status=status_str,
            )

        except SQLAgentError as e:
            await session.rollback()
            query_record.status = "failed"
            session.add(query_record)
            query_exec = QueryExecution(
                query_id=query_record.id,
                sql_valid=False,
                sql_error=e.message,
            )
            session.add(query_exec)
            await session.commit()
            raise e

        except Exception as e:
            await session.rollback()
            query_record.status = "failed"
            session.add(query_record)
            query_exec = QueryExecution(
                query_id=query_record.id,
                sql_valid=False,
                sql_error=str(e),
            )
            session.add(query_exec)
            await session.commit()
            raise e


# Singleton Instance
sql_service = SQLService()
