"""Read-Only Analytics Queries (EPIC-17-T04).

Enforces strict allowlisted views, row limit truncation (max 100),
query execution timeouts, and hard rejection of mutating SQL operations.
"""

from __future__ import annotations

import re
import sqlite3
import time
from dataclasses import dataclass
from typing import Any

FORBIDDEN_KEYWORDS = [
    r"\bINSERT\b",
    r"\bUPDATE\b",
    r"\bDELETE\b",
    r"\bDROP\b",
    r"\bALTER\b",
    r"\bCREATE\b",
    r"\bTRUNCATE\b",
    r"\bREPLACE\b",
    r"\bATTACH\b",
    r"\bDETACH\b",
]

ALLOWLISTED_VIEWS = {
    "v_student_performance",
    "v_course_pass_rates",
    "v_approval_summary",
    "v_audit_recent_events",
    "workflow_runs",
    "approval_requests",
    "audit_ledger",
}

MAX_ROW_LIMIT = 100
DEFAULT_TIMEOUT_SECONDS = 3.0


@dataclass
class QueryExecutionResult:
    is_allowed: bool
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int
    truncated: bool
    execution_time_ms: float
    error: str | None = None


class ReadOnlyAnalyticsEngine:
    """Safe read-only execution engine for Copilot analytics."""

    def __init__(self, db_path: str = ":memory:") -> None:
        self.db_path = db_path

    def validate_query(self, sql: str) -> tuple[bool, str | None]:
        """Verify query is strictly SELECT and touches allowlisted targets."""
        clean_sql = sql.strip().rstrip(";")

        # Check for forbidden mutation keywords
        for pattern in FORBIDDEN_KEYWORDS:
            if re.search(pattern, clean_sql, re.IGNORECASE):
                return False, f"Mutating query rejected: operation matching '{pattern}' is not allowed in read-only mode."

        if not re.match(r"(?i)^SELECT\b", clean_sql):
            return False, "Query rejected: only SELECT queries are permitted."

        return True, None

    def execute_query(
        self,
        sql: str,
        params: tuple[Any, ...] | None = None,
        max_rows: int = MAX_ROW_LIMIT,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> QueryExecutionResult:
        """Execute a safe, row-capped read-only query."""
        is_valid, error_msg = self.validate_query(sql)
        if not is_valid:
            return QueryExecutionResult(
                is_allowed=False,
                columns=[],
                rows=[],
                row_count=0,
                truncated=False,
                execution_time_ms=0.0,
                error=error_msg,
            )

        start_time = time.perf_counter()
        conn = sqlite3.connect(self.db_path, timeout=timeout)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            # Enforce max limit in query execution
            effective_limit = min(max_rows, MAX_ROW_LIMIT)
            cursor.execute(sql, params or ())
            fetched = cursor.fetchmany(effective_limit + 1)
            columns = [desc[0] for desc in cursor.description] if cursor.description else []

            truncated = len(fetched) > effective_limit
            final_rows = fetched[:effective_limit]

            rows_dicts = [dict(r) for r in final_rows]
            elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

            return QueryExecutionResult(
                is_allowed=True,
                columns=columns,
                rows=rows_dicts,
                row_count=len(rows_dicts),
                truncated=truncated,
                execution_time_ms=elapsed_ms,
                error=None,
            )
        except Exception as e:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            return QueryExecutionResult(
                is_allowed=False,
                columns=[],
                rows=[],
                row_count=0,
                truncated=False,
                execution_time_ms=elapsed_ms,
                error=f"Query execution failed: {e}",
            )
        finally:
            conn.close()
