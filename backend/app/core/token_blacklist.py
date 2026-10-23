"""Redis-backed token blacklist for logout/revocation.

EPIC-04-T04: Token blacklist using Redis with TTL matching token expiry.
"""

from __future__ import annotations

from datetime import UTC, datetime

import redis.asyncio as aioredis

from app.core.config import get_settings

_BLACKLIST_PREFIX = "nexus:token:blacklist:"


async def _get_redis() -> aioredis.Redis:
    """Get a Redis connection."""
    settings = get_settings()
    return aioredis.from_url(str(settings.redis_url))  # type: ignore[no-untyped-call]


async def blacklist_token(jti: str, exp: datetime) -> None:
    """Add a token JTI to the blacklist.

    The key expires automatically when the token would have expired,
    so no cleanup is needed.
    """
    r = await _get_redis()
    try:
        ttl = max(int((exp - datetime.now(UTC)).total_seconds()), 1)
        await r.setex(f"{_BLACKLIST_PREFIX}{jti}", ttl, "1")
    finally:
        await r.aclose()


async def is_token_blacklisted(jti: str) -> bool:
    """Check if a token JTI has been blacklisted."""
    r = await _get_redis()
    try:
        return bool(await r.exists(f"{_BLACKLIST_PREFIX}{jti}"))
    finally:
        await r.aclose()
