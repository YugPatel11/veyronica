"""Redis token-bucket rate limiter middleware.

EPIC-04-T05: Rate limiting per user and per IP via Redis.
"""

from __future__ import annotations

import time
from typing import Any

import redis.asyncio as aioredis
import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.config import get_settings
from app.core.errors import RateLimitedError

logger = structlog.get_logger()

_RATE_PREFIX = "nexus:ratelimit:"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Token-bucket rate limiter backed by Redis.

    Enforces per-IP limits on all requests and per-user limits
    on authenticated requests. Skips health endpoints.
    """

    SKIP_PATHS = {"/health", "/ready", "/docs", "/redoc", "/openapi.json"}

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Skip health and docs endpoints
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        settings = get_settings()

        # Identify the requester
        client_ip = request.client.host if request.client else "unknown"
        user_id = getattr(request.state, "user_id", None)

        try:
            r = aioredis.from_url(str(settings.redis_url))  # type: ignore[no-untyped-call]
            try:
                # Per-IP rate limit
                ip_key = f"{_RATE_PREFIX}ip:{client_ip}"
                ip_count = await self._increment_window(r, ip_key, window=60)

                if ip_count > settings.rate_limit_per_ip:
                    logger.warning(
                        "rate_limit_exceeded",
                        source="ip",
                        client_ip=client_ip,
                        count=ip_count,
                    )
                    raise RateLimitedError(
                        "Too many requests. Please try again later."
                    )

                # Per-user rate limit (if authenticated)
                if user_id:
                    user_key = f"{_RATE_PREFIX}user:{user_id}"
                    user_count = await self._increment_window(r, user_key, window=60)

                    if user_count > settings.rate_limit_per_user:
                        logger.warning(
                            "rate_limit_exceeded",
                            source="user",
                            user_id=user_id,
                            count=user_count,
                        )
                        raise RateLimitedError(
                            "Too many requests. Please try again later."
                        )
            finally:
                await r.aclose()
        except RateLimitedError:
            raise
        except Exception:
            # If Redis is down, fail open (don't block requests)
            logger.warning("rate_limiter_redis_error", exc_info=True)

        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(settings.rate_limit_per_ip)
        return response

    @staticmethod
    async def _increment_window(
        r: aioredis.Redis, key: str, window: int = 60
    ) -> int:
        """Increment a sliding-window counter and return current count."""
        pipe = r.pipeline()
        pipe.incr(key)
        pipe.expire(key, window)
        results: list[Any] = await pipe.execute()
        return int(results[0])
