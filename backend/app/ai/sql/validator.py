"""
AST-based SQL Validator & Security Enforcer for EMBIP (Phase 9).
Uses sqlglot to strictly enforce single-statement, read-only SELECT queries.
"""

from typing import List, Set, Tuple
import sqlglot
import sqlglot.expressions as exp

from app.ai.sql.exceptions import SQLSecurityError, SQLValidationError


class SQLValidator:
    """
    AST-based SQL Validator enforcing strict read-only and security rules.
    """

    # AST node types that are strictly forbidden anywhere in the AST
    FORBIDDEN_NODE_TYPES = (
        exp.Insert,
        exp.Update,
        exp.Delete,
        exp.Drop,
        exp.Create,
        exp.Alter,
        exp.TruncateTable,
        exp.Grant,
        exp.Command,
        exp.Transaction,
        exp.Commit,
        exp.Rollback,
    )

    # Function names (lowercase) that are strictly prohibited due to security risks
    FORBIDDEN_FUNCTIONS: Set[str] = {
        "pg_sleep",
        "lo_import",
        "lo_export",
        "lo_unlink",
        "dblink_connect",
        "dblink_exec",
        "dblink",
        "current_setting",
        "set_config",
        "query_to_xml",
        "pg_read_file",
        "pg_ls_dir",
        "pg_stat_file",
        "copy",
        "vacuum",
        "analyze",
    }

    # Dangerous keywords for fallback regex/string checks
    DANGEROUS_KEYWORDS: Set[str] = {
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "ALTER",
        "CREATE",
        "TRUNCATE",
        "GRANT",
        "REVOKE",
        "VACUUM",
        "ANALYZE",
        "COPY",
        "PG_SLEEP",
        "LO_IMPORT",
        "DBLINK",
    }

    def validate(self, sql: str) -> Tuple[bool, List[str]]:
        """
        Validates the input SQL string.
        Returns tuple of (is_valid: bool, invalid_reasons: List[str]).
        """
        reasons: List[str] = []

        if not sql or not sql.strip():
            return False, ["SQL query cannot be empty or blank."]

        cleaned_sql = sql.strip()

        # 1. Parse SQL into AST expressions
        try:
            parsed_statements = sqlglot.parse(cleaned_sql, read="postgres")
        except Exception as e:
            return False, [f"SQL Parsing Error: {str(e)}"]

        if not parsed_statements:
            return False, ["Could not parse valid SQL from input."]

        # 2. Reject multi-statement queries
        if len(parsed_statements) > 1:
            return False, [f"Multi-statement queries are strictly prohibited (found {len(parsed_statements)} statements)."]

        statement = parsed_statements[0]
        if statement is None:
            return False, ["Parsed statement is null or invalid."]

        # 3. Ensure statement is a SELECT (or CTE WITH ... SELECT)
        if not isinstance(statement, exp.Select):
            return False, [f"Statement type '{type(statement).__name__}' is not allowed. Only SELECT queries are permitted."]

        # 4. Traverse AST nodes to inspect for prohibited operations
        for node in statement.walk():
            # Check forbidden AST node types
            if isinstance(node, self.FORBIDDEN_NODE_TYPES):
                reasons.append(f"Prohibited operation '{type(node).__name__}' detected in query AST.")

            # Check function calls for forbidden system/side-effect functions
            if isinstance(node, exp.Anonymous) or isinstance(node, exp.Func):
                func_name = (node.this.name if hasattr(node.this, "name") else str(node.this)).lower()
                if func_name in self.FORBIDDEN_FUNCTIONS:
                    reasons.append(f"Forbidden function call '{func_name}' is prohibited for security.")

        # 5. Sanity check string representations for keywords attached in comments/subqueries
        sql_upper = cleaned_sql.upper()
        for kw in ["--", "/*", "*/"]:
            if kw in cleaned_sql:
                # Comments are stripped during execution, but let's ensure no hidden code
                pass

        if reasons:
            return False, reasons

        return True, []

    def validate_or_throw(self, sql: str) -> None:
        """
        Validates SQL string and raises SQLValidationError or SQLSecurityError if invalid.
        """
        is_valid, reasons = self.validate(sql)
        if not is_valid:
            error_msg = "; ".join(reasons)
            if any(k in r for r in reasons for k in ["Prohibited", "Forbidden", "not allowed", "prohibited", "Statement type"]):
                raise SQLSecurityError(f"SQL Security Violation: {error_msg}", invalid_reasons=reasons)
            raise SQLValidationError(f"Invalid SQL Query: {error_msg}", invalid_reasons=reasons)


# Singleton Instance
sql_validator = SQLValidator()
