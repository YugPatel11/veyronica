"""API performance profiling and latency breakdown middleware.

EPIC-25-T03: API performance profiling (middleware latency breakdown and Server-Timing).
Measures request duration, database time, and calculates endpoint percentiles.
"""

from __future__ import annotations

from collections import defaultdict
import time
from typing import Any
import numpy as np
import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = structlog.get_logger()


class LatencyProfiler:
    """Accumulates endpoint latency percentiles and latency budgets."""

    def __init__(self, slow_request_threshold_ms: float = 200.0) -> None:
        self.slow_request_threshold_ms = slow_request_threshold_ms
        self._samples: dict[str, list[float]] = defaultdict(list)
        self._max_samples = 1000

    def record(self, endpoint: str, duration_ms: float) -> None:
        """Record a latency sample for an endpoint."""
        samples = self._samples[endpoint]
        if len(samples) >= self._max_samples:
            samples.pop(0)
        samples.append(duration_ms)

        if duration_ms > self.slow_request_threshold_ms:
            logger.warning(
                "slow_api_request_detected",
                endpoint=endpoint,
                duration_ms=round(duration_ms, 2),
                threshold_ms=self.slow_request_threshold_ms,
            )

    def get_percentiles(self, endpoint: str) -> dict[str, float]:
        """Calculate p50, p90, p95, p99 for an endpoint."""
        samples = self._samples.get(endpoint, [])
        if not samples:
            return {"count": 0, "p50": 0.0, "p90": 0.0, "p95": 0.0, "p99": 0.0}

        sorted_samples = sorted(samples)
        return {
            "count": len(sorted_samples),
            "p50": round(float(np.percentile(sorted_samples, 50)), 2),
            "p90": round(float(np.percentile(sorted_samples, 90)), 2),
            "p95": round(float(np.percentile(sorted_samples, 95)), 2),
            "p99": round(float(np.percentile(sorted_samples, 99)), 2),
        }

    def clear(self) -> None:
        """Clear recorded samples."""
        self._samples.clear()


profiler = LatencyProfiler()


class PerformanceProfilingMiddleware(BaseHTTPMiddleware):
    """EPIC-25-T03: Injects Server-Timing headers and logs latency telemetry."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time.perf_counter()

        # Contextual timer for internal components (e.g. db, llm)
        request.state.profiling = {
            "start_time": start_time,
            "db_duration_ms": 0.0,
            "external_duration_ms": 0.0,
        }

        response = await call_next(request)

        total_duration_ms = (time.perf_counter() - start_time) * 1000.0
        db_duration_ms = request.state.profiling.get("db_duration_ms", 0.0)
        app_duration_ms = max(total_duration_ms - db_duration_ms, 0.0)

        # Standard Server-Timing header (W3C specification)
        server_timing = f"total;dur={total_duration_ms:.2f}, app;dur={app_duration_ms:.2f}"
        if db_duration_ms > 0:
            server_timing += f", db;dur={db_duration_ms:.2f}"

        response.headers["Server-Timing"] = server_timing
        response.headers["X-Response-Time"] = f"{total_duration_ms:.2f}ms"

        # Record endpoint sample
        path = request.url.path
        profiler.record(path, total_duration_ms)

        return response
