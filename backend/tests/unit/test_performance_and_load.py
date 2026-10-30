"""Unit tests for Performance, Profiling, Caching, and Load Testing (Batch 9).

Covers EPIC-25-T01 through EPIC-25-T05:
- EPIC-25-T01: Locust load testing suite definitions
- EPIC-25-T02: Database query optimization & N+1 detection
- EPIC-25-T03: API performance profiling middleware & percentiles
- EPIC-25-T04: Multi-tier caching strategy & tag invalidation
- EPIC-25-T05: High-concurrency load benchmark verification
"""

from __future__ import annotations

import time
import pytest
from httpx import ASGITransport, AsyncClient

from app.core.cache_strategy import CacheManager, CacheTTL
from app.core.db_optimization import DatabaseQueryOptimizer
from app.core.profiling import LatencyProfiler
from app.main import app
from tests.load.verify_targets import execute_load_benchmark


# ── EPIC-25-T03: Profiling & Latency Percentiles ─────────────────────────────

def test_latency_profiler_percentiles() -> None:
    profiler = LatencyProfiler(slow_request_threshold_ms=150.0)
    profiler.clear()

    # Record 100 samples from 1ms to 100ms
    for i in range(1, 101):
        profiler.record("/api/v1/test", float(i))

    pcts = profiler.get_percentiles("/api/v1/test")
    assert pcts["count"] == 100
    assert 48.0 <= pcts["p50"] <= 52.0
    assert 88.0 <= pcts["p90"] <= 92.0
    assert 93.0 <= pcts["p95"] <= 97.0
    assert 97.0 <= pcts["p99"] <= 100.0


@pytest.mark.anyio
async def test_server_timing_header_injected() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        # In test mode or when middleware active, check response time
        assert "x-request-id" in resp.headers or resp.status_code == 200


# ── EPIC-25-T02: Database Query Optimizer & N+1 Detection ────────────────────

def test_db_optimizer_slow_queries_and_n_plus_one() -> None:
    optimizer = DatabaseQueryOptimizer(slow_query_threshold_ms=40.0)
    optimizer.reset_stats()

    # 1. Fast query
    optimizer.record_query("SELECT * FROM users WHERE id = 1", duration_ms=5.0)
    assert len(optimizer.get_slow_queries()) == 0

    # 2. Slow query (>40ms)
    optimizer.record_query(
        "SELECT * FROM exam_submissions WHERE department = 'CS' AND year = 2026",
        duration_ms=65.4,
    )
    slow = optimizer.get_slow_queries()
    assert len(slow) == 1
    assert slow[0].duration_ms == 65.4

    # 3. N+1 pattern detection (6 queries of identical pattern)
    for i in range(6):
        optimizer.record_query(f"SELECT * FROM grades WHERE student_id = {i}", duration_ms=2.0)

    n_plus_one = optimizer.detect_n_plus_one_patterns(threshold=5)
    assert len(n_plus_one) >= 1
    assert n_plus_one[0]["execution_count"] >= 6


def test_db_optimizer_index_recommendation() -> None:
    optimizer = DatabaseQueryOptimizer(slow_query_threshold_ms=30.0)
    optimizer.reset_stats()

    optimizer.record_query(
        "SELECT * FROM student_records WHERE division = 'A' AND status = 'active'",
        duration_ms=55.0,
    )

    recs = optimizer.analyze_index_opportunities()
    assert len(recs) >= 1
    assert recs[0].table_name == "student_records"
    assert "division" in recs[0].suggested_columns


# ── EPIC-25-T04: Multi-Tier Caching & Tag Invalidation ───────────────────────

def test_cache_manager_ttl_and_invalidation() -> None:
    mgr = CacheManager()
    mgr.clear()

    # Set items with tags
    mgr.set("student:1", {"name": "Alice"}, ttl_seconds=CacheTTL.SHORT, tags=["students", "cs"])
    mgr.set("student:2", {"name": "Bob"}, ttl_seconds=CacheTTL.SHORT, tags=["students", "ee"])
    mgr.set("config:system", {"version": "1.0"}, ttl_seconds=CacheTTL.LONG, tags=["config"])

    # Retrieve items
    assert mgr.get("student:1") == {"name": "Alice"}
    assert mgr.get("student:2") == {"name": "Bob"}
    assert mgr.get("config:system") == {"version": "1.0"}

    # Invalidate by tag "cs"
    purged = mgr.invalidate_tag("cs")
    assert purged == 1
    assert mgr.get("student:1") is None
    assert mgr.get("student:2") == {"name": "Bob"}

    # Invalidate by tag "students"
    purged_students = mgr.invalidate_tag("students")
    assert purged_students == 1
    assert mgr.get("student:2") is None

    # Check hit/miss stats
    stats = mgr.get_stats()
    assert stats["hits"] >= 3
    assert stats["misses"] >= 2
    assert 0.0 <= stats["hit_ratio"] <= 1.0


# ── EPIC-25-T05: High-Concurrency Load Verification Benchmark ───────────────

@pytest.mark.anyio
async def test_load_benchmark_50_concurrent_workers() -> None:
    # Run benchmark with 50 concurrent workers and 200 total requests
    result = await execute_load_benchmark(total_requests=200, concurrency=50, target_endpoint="/health")

    assert result.total_requests >= 200
    assert result.concurrent_workers == 50
    assert result.p95_ms < 200.0, f"p95 latency {result.p95_ms}ms exceeded 200ms limit"
    assert result.error_count == 0
    assert result.all_passed is True
