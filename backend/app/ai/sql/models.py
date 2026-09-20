"""
Pydantic Data Models for SQL Agent Requests, Generation, Execution & API Responses (Phase 9).
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class SQLQueryRequest(BaseModel):
    """Client API Request payload for natural language SQL queries."""

    question: str = Field(..., min_length=3, max_length=1000, description="Natural language business question")
    max_rows: Optional[int] = Field(default=100, ge=1, le=1000, description="Maximum rows to return")

    @field_validator("question")
    @classmethod
    def validate_question_not_empty(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Natural language question cannot be empty or blank.")
        return cleaned


class SQLGenerationResult(BaseModel):
    """Structured LLM output schema for SQL generation."""

    sql: str = Field(..., description="PostgreSQL-compliant read-only SQL query")
    explanation: str = Field(..., description="Concise non-technical explanation of what query calculates")
    tables_used: List[str] = Field(default_factory=list, description="Database tables referenced in SQL")
    columns_used: List[str] = Field(default_factory=list, description="Database columns referenced in SQL")


class SQLExecutionResult(BaseModel):
    """Raw PostgreSQL query execution result."""

    columns: List[str] = Field(default_factory=list, description="Column names returned by PostgreSQL")
    rows: List[Dict[str, Any]] = Field(default_factory=list, description="JSON-serialized row records")
    row_count: int = Field(default=0, description="Total rows fetched")
    execution_time_ms: float = Field(default=0.0, description="Execution duration in milliseconds")


class SQLQueryResponse(BaseModel):
    """Final API response payload returned to client."""

    question: str = Field(..., description="Original user business question")
    sql: str = Field(..., description="Validated read-only SQL executed against PostgreSQL")
    explanation: str = Field(..., description="Concise explanation of calculation")
    tables_used: List[str] = Field(default_factory=list, description="List of tables queried")
    columns: List[str] = Field(default_factory=list, description="Columns present in result table")
    rows: List[Dict[str, Any]] = Field(default_factory=list, description="Array of row data objects")
    row_count: int = Field(..., description="Total count of returned rows")
    execution_time_ms: float = Field(..., description="Execution duration in milliseconds")
    status: str = Field(default="success", description="Status string ('success', 'error', 'no_data')")
