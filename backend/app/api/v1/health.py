"""Health, readiness, aggregated checks, and Prometheus metrics export.

EPIC-23-T02: Prometheus-compatible metrics export (/metrics).
EPIC-23-T06: Health check aggregation endpoint (/health/aggregated).
"""

from __future__ import annotations

import asyncio
from typing import Any

import redis.asyncio as aioredis
from fastapi import APIRouter, Response
from fastapi.responses import PlainTextResponse
from sqlalchemy import text

from app.core.config import get_settings
from app.core.telemetry import metrics
from app.db.session import engine

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Basic liveness probe — returns 200 if the process is running."""
    return {"status": "ok", "service": "nexus-api"}


@router.get("/ready")
async def readiness() -> dict[str, Any]:
    """Readiness probe — checks database and Redis connectivity."""
    settings = get_settings()
    checks: dict[str, str] = {}

    # Database check
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.close()
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {type(e).__name__}"

    # Redis check
    try:
        r = aioredis.from_url(str(settings.redis_url))  # type: ignore[no-untyped-call]
        await asyncio.wait_for(r.ping(), timeout=2.0)
        await r.aclose()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {type(e).__name__}"

    all_ok = all(v == "ok" for v in checks.values())
    return {
        "status": "ok" if all_ok else "degraded",
        "checks": checks,
        "version": "0.1.0",
        "environment": settings.nexus_env,
    }


@router.get("/health/aggregated")
async def aggregated_health() -> dict[str, Any]:
    """EPIC-23-T06: Full system health check aggregation.

    Aggregates Core API, Database, Redis, Connector Hub, and Audit Ledger Integrity.
    """
    settings = get_settings()
    ready_state = await readiness()

    # Connector hub health aggregation
    connector_checks: dict[str, str] = {}
    try:
        from app.connectors.registry import registry
        statuses = await registry.check_all_health()
        connector_checks = {cid: s.value for cid, s in statuses.items()}
    except Exception as e:
        connector_checks["error"] = str(e)

    # Audit ledger cryptographic integrity check
    ledger_status = "ok"
    try:
        from app.audit import ledger
        is_intact = ledger.verify_chain()
        ledger_status = "intact" if is_intact else "tampered"
    except Exception:
        ledger_status = "uninitialized"

    all_systems_healthy = (
        ready_state.get("status") == "ok"
        and ledger_status in ("intact", "ok")
        and all(s in ("healthy", "ok") for s in connector_checks.values())
    )

    return {
        "status": "healthy" if all_systems_healthy else "degraded",
        "api": "ok",
        "core_infrastructure": ready_state.get("checks", {}),
        "connectors": connector_checks,
        "audit_ledger": ledger_status,
        "environment": settings.nexus_env,
    }


@router.get("/metrics", response_class=PlainTextResponse)
async def prometheus_metrics() -> Response:
    """EPIC-23-T02: Prometheus-compatible metrics export."""
    content = metrics.render_prometheus_text()
    return PlainTextResponse(content=content, media_type="text/plain; version=0.0.4; charset=utf-8")
