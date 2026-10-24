"""Connector Hub API endpoints.

EPIC-05-T06: Connector registry with health check aggregation.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.connectors import ConnectorResult
from app.connectors.registry import registry

router = APIRouter(prefix="/connectors", tags=["Connectors"])


# ── Response Models ──────────────────────────────────────────────────────────

class ConnectorInfo(BaseModel):
    id: str
    name: str
    base_url: str
    health: str
    circuit_state: str


class ExecuteRequest(BaseModel):
    connector_id: str
    operation: str
    payload: dict[str, Any] = Field(default_factory=dict)
    dry_run: bool = False
    idempotency_key: str | None = None


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/", response_model=list[ConnectorInfo])
async def list_connectors() -> list[ConnectorInfo]:
    """List all registered connectors with their status."""
    return [ConnectorInfo(**c) for c in registry.list_all()]


@router.get("/health")
async def all_health() -> dict[str, str]:
    """Run health checks for all connectors."""
    results = await registry.check_all_health()
    return {cid: status.value for cid, status in results.items()}


@router.get("/{connector_id}/health")
async def connector_health(connector_id: str) -> dict[str, str]:
    """Run health check for a single connector."""
    status = await registry.check_health(connector_id)
    return {"connector_id": connector_id, "status": status.value}


@router.post("/execute")
async def execute_operation(body: ExecuteRequest) -> ConnectorResult:
    """Execute a connector operation through the registry.

    Includes circuit breaker + retry logic automatically.
    """
    return await registry.execute(
        connector_id=body.connector_id,
        operation=body.operation,
        payload=body.payload,
        dry_run=body.dry_run,
        idempotency_key=body.idempotency_key,
    )
