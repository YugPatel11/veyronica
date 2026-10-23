"""Health and readiness endpoints for monitoring and orchestration."""

from __future__ import annotations

import asyncio
from typing import Any

import redis.asyncio as aioredis
from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import get_settings
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
