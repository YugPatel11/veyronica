"""Caching strategy, TTL tiers, and tag-based invalidation engine.

EPIC-25-T04: Caching strategy review (Redis TTLs, cache invalidation, hit/miss metrics).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
import json
from typing import Any
import structlog

logger = structlog.get_logger()


class CacheTTL:
    """Predefined TTL hierarchies for consistent data freshness."""
    REALTIME = 30       # Live queue status, SSE event buffers (30s)
    SHORT = 120         # Connector health, active approval lists (2m)
    STANDARD = 600      # Student rosters, rubric definitions, workflows (10m)
    LONG = 86400        # Static configurations, academic catalogs (24h)


@dataclass
class CacheEntry:
    """In-memory cache entry with expiry and tags."""
    key: str
    value: Any
    tags: set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def is_expired(self) -> bool:
        return datetime.now(UTC) >= self.expires_at


class CacheManager:
    """EPIC-25-T04: Multi-tier caching layer with tag invalidation and hit/miss observability."""

    def __init__(self) -> None:
        self._store: dict[str, CacheEntry] = {}
        self._tag_index: dict[str, set[str]] = defaultdict(set)
        self._hits = 0
        self._misses = 0

    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: int = CacheTTL.STANDARD,
        tags: list[str] | None = None,
    ) -> None:
        """Store value with specified TTL and optional tags."""
        expires_at = datetime.now(UTC) + timedelta(seconds=ttl_seconds)
        tag_set = set(tags or [])
        entry = CacheEntry(
            key=key,
            value=value,
            tags=tag_set,
            expires_at=expires_at,
        )
        self._store[key] = entry

        # Update tag index
        for tag in tag_set:
            self._tag_index[tag].add(key)

    def get(self, key: str) -> Any | None:
        """Retrieve value by key. Returns None if missing or expired."""
        entry = self._store.get(key)
        if not entry:
            self._misses += 1
            return None

        if entry.is_expired:
            self.delete(key)
            self._misses += 1
            return None

        self._hits += 1
        return entry.value

    def delete(self, key: str) -> bool:
        """Remove a key from cache and clean tag index."""
        entry = self._store.pop(key, None)
        if entry:
            for tag in entry.tags:
                self._tag_index[tag].discard(key)
            return True
        return False

    def invalidate_tag(self, tag: str) -> int:
        """Invalidate all cache entries associated with a tag."""
        keys = list(self._tag_index.get(tag, set()))
        removed_count = 0
        for key in keys:
            if self.delete(key):
                removed_count += 1
        self._tag_index.pop(tag, None)
        logger.info("cache_tag_invalidated", tag=tag, purged_keys=removed_count)
        return removed_count

    def invalidate_pattern(self, pattern_prefix: str) -> int:
        """Invalidate all keys starting with prefix."""
        matching_keys = [k for k in self._store.keys() if k.startswith(pattern_prefix)]
        for k in matching_keys:
            self.delete(k)
        return len(matching_keys)

    def get_stats(self) -> dict[str, Any]:
        """Compute hit/miss ratio and capacity metrics."""
        total = self._hits + self._misses
        hit_ratio = (self._hits / total) if total > 0 else 0.0
        return {
            "hits": self._hits,
            "misses": self._misses,
            "total_requests": total,
            "hit_ratio": round(hit_ratio, 3),
            "stored_keys": len(self._store),
            "indexed_tags": len(self._tag_index),
        }

    def clear(self) -> None:
        """Flush entire cache."""
        self._store.clear()
        self._tag_index.clear()
        self._hits = 0
        self._misses = 0


# Global cache manager
cache = CacheManager()
