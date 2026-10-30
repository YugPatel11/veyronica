"""Database query optimization, slow query logging, and index tuning.

EPIC-25-T02: Database query optimisation (slow query log, index tuning, N+1 detection).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
import re
import structlog

logger = structlog.get_logger()


@dataclass
class QueryRecord:
    """Record of an executed database query."""
    statement: str
    duration_ms: float
    parameters: dict | None = None
    rows_returned: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class IndexRecommendation:
    """Automated index recommendation based on slow query patterns."""
    table_name: str
    suggested_columns: list[str]
    index_type: str = "B-TREE"
    reason: str = ""


class DatabaseQueryOptimizer:
    """EPIC-25-T02: Monitors database queries for performance bottlenecks, N+1 patterns, and missing indexes."""

    def __init__(self, slow_query_threshold_ms: float = 50.0) -> None:
        self.slow_query_threshold_ms = slow_query_threshold_ms
        self._slow_queries: list[QueryRecord] = []
        self._query_counter: dict[str, int] = defaultdict(int)

    def sanitize_sql(self, sql: str) -> str:
        """Normalize SQL and remove literal values to group query templates."""
        cleaned = re.sub(r"\s+", " ", sql).strip()
        # Replace string and numeric literals with placeholders
        cleaned = re.sub(r"\'[^\']*\'", "'?'", cleaned)
        cleaned = re.sub(r"\b\d+\b", "?", cleaned)
        return cleaned

    def record_query(
        self,
        statement: str,
        duration_ms: float,
        parameters: dict | None = None,
        rows_returned: int = 0,
    ) -> QueryRecord:
        """Inspect and record an executed query."""
        record = QueryRecord(
            statement=statement,
            duration_ms=duration_ms,
            parameters=parameters,
            rows_returned=rows_returned,
        )

        template = self.sanitize_sql(statement)
        self._query_counter[template] += 1

        if duration_ms > self.slow_query_threshold_ms:
            self._slow_queries.append(record)
            logger.warning(
                "slow_database_query",
                duration_ms=round(duration_ms, 2),
                threshold_ms=self.slow_query_threshold_ms,
                statement=template[:200],
            )

        return record

    def detect_n_plus_one_patterns(self, threshold: int = 5) -> list[dict[str, str | int]]:
        """Identify potential N+1 query loops where identical queries run repeatedly."""
        findings: list[dict[str, str | int]] = []
        for query_template, count in self._query_counter.items():
            if count >= threshold and query_template.upper().startswith("SELECT"):
                findings.append(
                    {
                        "query_template": query_template,
                        "execution_count": count,
                        "diagnosis": "Potential N+1 loop detected; consider eager loading with selectinload / joinedload",
                    }
                )
        return findings

    def analyze_index_opportunities(self) -> list[IndexRecommendation]:
        """Analyze slow queries to recommend missing indexes on WHERE / JOIN clauses."""
        recommendations: list[IndexRecommendation] = []
        seen_tables: set[str] = set()

        for q in self._slow_queries:
            sql_upper = q.statement.upper()
            match = re.search(r"FROM\s+([a-zA-Z_]+)\s+WHERE\s+([a-zA-Z0-9_\s=<>]+)", sql_upper)
            if match:
                table = match.group(1).lower()
                where_clause = match.group(2)
                cols = re.findall(r"([a-zA-Z_]+)\s*=", where_clause)
                cols = [c.lower() for c in cols if c.lower() not in {"select", "and", "or"}]

                if cols and table not in seen_tables:
                    seen_tables.add(table)
                    recommendations.append(
                        IndexRecommendation(
                            table_name=table,
                            suggested_columns=cols,
                            reason=f"Slow query ({q.duration_ms:.1f}ms) filters repeatedly on {', '.join(cols)}",
                        )
                    )

        return recommendations

    def get_slow_queries(self, limit: int = 20) -> list[QueryRecord]:
        """Return the most recent slow queries."""
        return self._slow_queries[-limit:]

    def reset_stats(self) -> None:
        """Clear query logs and counters."""
        self._slow_queries.clear()
        self._query_counter.clear()


# Global optimizer instance
db_optimizer = DatabaseQueryOptimizer()
