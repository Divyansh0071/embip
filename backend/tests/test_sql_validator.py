"""
Unit Test Suite for AST-based SQL Validator & Security Enforcer (Phase 9).
"""

import pytest
from app.ai.sql.exceptions import SQLSecurityError, SQLValidationError
from app.ai.sql.validator import SQLValidator, sql_validator


def test_sql_validator_accepts_valid_select():
    """Verify clean SELECT queries are accepted."""
    sql = "SELECT id, name, city FROM stores WHERE workspace_id = 'ws-123' ORDER BY name ASC;"
    is_valid, reasons = sql_validator.validate(sql)
    assert is_valid is True
    assert len(reasons) == 0


def test_sql_validator_accepts_valid_cte_with_aggregates():
    """Verify CTEs (WITH ... SELECT) and aggregate functions are accepted."""
    sql = """
    WITH store_revenue AS (
        SELECT store_id, SUM(total_amount) AS revenue
        FROM sales_transactions
        GROUP BY store_id
    )
    SELECT s.name, r.revenue
    FROM stores s
    JOIN store_revenue r ON s.id = r.store_id
    ORDER BY r.revenue DESC
    LIMIT 10;
    """
    is_valid, reasons = sql_validator.validate(sql)
    assert is_valid is True
    assert len(reasons) == 0


@pytest.mark.parametrize(
    "prohibited_sql,expected_keyword",
    [
        ("INSERT INTO stores (name) VALUES ('Hacked');", "Insert"),
        ("UPDATE stores SET name = 'Hacked';", "Update"),
        ("DELETE FROM sales_transactions;", "Delete"),
        ("DROP TABLE stores;", "Drop"),
        ("ALTER TABLE stores ADD COLUMN hack TEXT;", "Alter"),
        ("CREATE TABLE hacked (id INT);", "Create"),
        ("TRUNCATE TABLE sales_items;", "Truncate"),
        ("GRANT ALL ON stores TO public;", "Grant"),
        ("REVOKE SELECT ON stores FROM public;", "Revoke"),
    ],
)
def test_sql_validator_rejects_mutation_and_ddl(prohibited_sql: str, expected_keyword: str):
    """Verify all data mutation and DDL statements are strictly rejected."""
    is_valid, reasons = sql_validator.validate(prohibited_sql)
    assert is_valid is False
    assert any(expected_keyword.lower() in r.lower() or "not allowed" in r.lower() for r in reasons)


def test_sql_validator_rejects_multi_statement():
    """Verify multi-statement queries separated by semicolons are rejected."""
    sql = "SELECT * FROM stores; DELETE FROM stores;"
    is_valid, reasons = sql_validator.validate(sql)
    assert is_valid is False
    assert any("multi-statement" in r.lower() for r in reasons)


@pytest.mark.parametrize(
    "dangerous_sql,expected_func",
    [
        ("SELECT pg_sleep(10);", "pg_sleep"),
        ("SELECT lo_import('/etc/passwd');", "lo_import"),
        ("SELECT dblink_connect('myconn');", "dblink_connect"),
        ("SELECT current_setting('server_version');", "current_setting"),
    ],
)
def test_sql_validator_rejects_dangerous_functions(dangerous_sql: str, expected_func: str):
    """Verify dangerous system & side-effect functions are rejected."""
    is_valid, reasons = sql_validator.validate(dangerous_sql)
    assert is_valid is False
    assert any(expected_func.lower() in r.lower() for r in reasons)


def test_sql_validator_validate_or_throw_raises_security_error():
    """Verify validate_or_throw raises SQLSecurityError for prohibited queries."""
    with pytest.raises(SQLSecurityError):
        sql_validator.validate_or_throw("DROP TABLE sales_transactions;")
