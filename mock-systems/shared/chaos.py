"""Chaos engineering middleware for mock enterprise systems.

EPIC-11-T05: Implement chaos switch (POST /_admin/chaos) behind feature flag.
Modes: outage (503), latency (delayed response), error_rate (random 500s).
Auto-recovers after duration_s.
"""

from __future__ import annotations

import asyncio
import random
import time
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class ChaosState:
    """Manages active chaos simulations."""

    def __init__(self) -> None:
        self.mode: str | None = None  # None, "outage", "latency", "error_rate"
        self.duration_s: float = 0.0
        self.start_time: float = 0.0
        self.latency_ms: int = 2000
        self.error_rate: float = 0.5

    def activate(self, mode: str, duration_s: float = 30.0, **kwargs: Any) -> dict[str, Any]:
        self.mode = mode
        self.duration_s = duration_s
        self.start_time = time.time()
        if "latency_ms" in kwargs:
            self.latency_ms = int(kwargs["latency_ms"])
        if "error_rate" in kwargs:
            self.error_rate = float(kwargs["error_rate"])
        return {
            "status": "activated",
            "mode": self.mode,
            "duration_s": self.duration_s,
            "latency_ms": self.latency_ms,
            "error_rate": self.error_rate,
        }

    def reset(self) -> dict[str, str]:
        self.mode = None
        self.duration_s = 0.0
        self.start_time = 0.0
        return {"status": "reset", "mode": "normal"}

    @property
    def is_active(self) -> bool:
        if not self.mode:
            return False
        if time.time() - self.start_time > self.duration_s:
            self.reset()
            return False
        return True


chaos_state = ChaosState()


class ChaosMiddleware(BaseHTTPMiddleware):
    """Intercepts requests when chaos mode is active."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Admin and health endpoints always bypass chaos
        if request.url.path.startswith("/_admin") or request.url.path == "/health":
            return await call_next(request)

        if chaos_state.is_active:
            if chaos_state.mode == "outage":
                return Response(
                    content='{"error": "Service Unavailable (Simulated Outage)"}',
                    status_code=503,
                    media_type="application/json",
                )
            elif chaos_state.mode == "latency":
                await asyncio.sleep(chaos_state.latency_ms / 1000.0)
            elif chaos_state.mode == "error_rate":
                if random.random() < chaos_state.error_rate:
                    return Response(
                        content='{"error": "Internal Server Error (Simulated Chaos)"}',
                        status_code=500,
                        media_type="application/json",
                    )

        return await call_next(request)
