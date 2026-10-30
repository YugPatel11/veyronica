"""Connector Hub — base protocol and result types.

EPIC-05-T01: Connector protocol and ConnectorResult base classes.
"""

from __future__ import annotations

import abc
import hashlib
import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field


class ConnectorStatus(StrEnum):
    """Health status of a connector."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"


class CircuitState(StrEnum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class ConnectorResult(BaseModel):
    """Standardised result from any connector operation."""

    success: bool
    data: Any = None
    error: str | None = None
    status_code: int | None = None
    latency_ms: int = 0
    connector_id: str = ""
    operation: str = ""
    idempotency_key: str | None = None
    is_dry_run: bool = False
    diff: DiffResult | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @property
    def failed(self) -> bool:
        return not self.success


class DiffResult(BaseModel):
    """Structured before/after diff for dry-run operations.

    EPIC-05-T05: Dry-run diff generation.
    """

    before: dict[str, Any] = Field(default_factory=dict)
    after: dict[str, Any] = Field(default_factory=dict)
    changes: list[DiffChange] = Field(default_factory=list)
    diff_hash: str = ""

    def compute_hash(self) -> str:
        """Compute deterministic hash of the diff for approval binding."""
        import json
        canonical = json.dumps(
            {"before": self.before, "after": self.after},
            sort_keys=True,
            default=str,
        )
        self.diff_hash = hashlib.sha256(canonical.encode()).hexdigest()
        return self.diff_hash


class DiffChange(BaseModel):
    """Individual field change in a diff."""

    field: str
    old_value: Any = None
    new_value: Any = None
    change_type: str = "modify"  # add, modify, remove


# Rebuild ConnectorResult now that DiffResult is defined
ConnectorResult.model_rebuild()


def generate_idempotency_key(connector_id: str, operation: str, payload: dict[str, Any]) -> str:
    """Generate deterministic idempotency key from operation params.

    EPIC-05-T04: Idempotency key generation.
    """
    import json
    canonical = json.dumps(
        {"connector": connector_id, "op": operation, "payload": payload},
        sort_keys=True,
        default=str,
    )
    return hashlib.sha256(canonical.encode()).hexdigest()


class BaseConnector(abc.ABC):
    """Abstract base class for all connectors.

    Every connector must implement:
    - execute(): Perform an operation
    - health_check(): Return connector health status
    """

    def __init__(
        self,
        connector_id: str,
        name: str,
        base_url: str,
        auth_config: dict[str, Any] | None = None,
    ):
        self.connector_id = connector_id
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.auth_config = auth_config or {}

    @abc.abstractmethod
    async def execute(
        self,
        operation: str,
        payload: dict[str, Any] | None = None,
        *,
        dry_run: bool = False,
        idempotency_key: str | None = None,
    ) -> ConnectorResult:
        """Execute a connector operation."""
        ...

    @abc.abstractmethod
    async def health_check(self) -> ConnectorStatus:
        """Check if the connector is healthy."""
        ...

    def _build_headers(self) -> dict[str, str]:
        """Build auth headers from config."""
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if "api_key" in self.auth_config:
            headers["X-API-Key"] = self.auth_config["api_key"]
        if "bearer_token" in self.auth_config:
            headers["Authorization"] = f"Bearer {self.auth_config['bearer_token']}"
        return headers
