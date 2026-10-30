"""Index Plan & EXPLAIN ANALYZE Analysis for Key Queries (EPIC-03-T14).

Analyzes query execution plans across key high-throughput tables:
- workflow_runs (lookup by status, user_id, created_at)
- audit_ledger (lookup by run_id, sequence_num, entry_hash)
- approval_requests (lookup by status, urgency, assignee)
- security_events (lookup by event_type, ip_address, timestamp)
- connector_calls (lookup by connector_id, status)
"""

from __future__ import annotations

import logging
import sqlite3
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("index_plan")

KEY_INDEXES_DDL = [
    "CREATE INDEX IF NOT EXISTS idx_workflow_runs_status_created ON workflow_runs(status, created_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_workflow_runs_user ON workflow_runs(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_audit_ledger_run_seq ON audit_ledger(run_id, sequence_num)",
    "CREATE INDEX IF NOT EXISTS idx_audit_ledger_hash ON audit_ledger(entry_hash)",
    "CREATE INDEX IF NOT EXISTS idx_approvals_status_urgency ON approval_requests(status, urgency)",
    "CREATE INDEX IF NOT EXISTS idx_security_events_type_time ON security_events(event_type, timestamp DESC)",
    "CREATE INDEX IF NOT EXISTS idx_security_events_ip ON security_events(ip_address)",
    "CREATE INDEX IF NOT EXISTS idx_connector_calls_status ON connector_calls(connector_id, status)",
]

KEY_BENCHMARK_QUERIES = [
    (
        "Workflow runs by status and recency",
        "SELECT id, status, created_at FROM workflow_runs WHERE status = 'RUNNING' ORDER BY created_at DESC LIMIT 20",
    ),
    (
        "Audit ledger verification lookup",
        "SELECT id, run_id, sequence_num, entry_hash FROM audit_ledger WHERE run_id = 'run-123' ORDER BY sequence_num ASC",
    ),
    (
        "Pending approval queue lookup",
        "SELECT id, run_id, status, urgency FROM approval_requests WHERE status = 'PENDING' ORDER BY urgency DESC",
    ),
    (
        "Recent security incidents by IP",
        "SELECT id, event_type, ip_address, timestamp FROM security_events WHERE ip_address = '192.168.1.100' ORDER BY timestamp DESC LIMIT 50",
    ),
]


def run_explain_plan(db_path: Path | str = ":memory:") -> dict[str, list[dict[str, str]]]:
    """Execute EXPLAIN QUERY PLAN on key queries and report scan vs index usage."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create dummy tables if in-memory or empty
    cursor.execute("CREATE TABLE IF NOT EXISTS workflow_runs (id TEXT PRIMARY KEY, user_id TEXT, status TEXT, created_at TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS audit_ledger (id TEXT PRIMARY KEY, run_id TEXT, sequence_num INTEGER, entry_hash TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS approval_requests (id TEXT PRIMARY KEY, run_id TEXT, status TEXT, urgency INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS security_events (id TEXT PRIMARY KEY, event_type TEXT, ip_address TEXT, timestamp TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS connector_calls (id TEXT PRIMARY KEY, connector_id TEXT, status TEXT)")

    # Apply proposed index plan
    for ddl in KEY_INDEXES_DDL:
        cursor.execute(ddl)
    conn.commit()

    results: dict[str, list[dict[str, str]]] = {}
    for name, query in KEY_BENCHMARK_QUERIES:
        explain_query = f"EXPLAIN QUERY PLAN {query}"
        cursor.execute(explain_query)
        plan_rows = cursor.fetchall()

        plan_details = []
        for row in plan_rows:
            # SQLite EXPLAIN QUERY PLAN returns: id, parent, notused, detail
            detail = row[-1]
            plan_details.append({"detail": detail, "uses_index": "USING INDEX" in detail or "SEARCH" in detail})

        results[name] = plan_details
        logger.info("Query: %s -> %s", name, [p["detail"] for p in plan_details])

    conn.close()
    return results


if __name__ == "__main__":
    db_target = sys.argv[1] if len(sys.argv) > 1 else ":memory:"
    res = run_explain_plan(db_target)
    print("\n=== Index Plan Execution Results ===")
    for q_name, plans in res.items():
        print(f"\n[QUERY] {q_name}")
        for p in plans:
            status = "[OK] INDEX USED" if p["uses_index"] else "- SCAN"
            print(f"  {status}: {p['detail']}")
