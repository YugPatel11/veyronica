"""Connector registry with health check aggregation.

EPIC-05-T06: Connector registry.
"""

from __future__ import annotations

import time
from typing import Any

import structlog

from app.connectors import BaseConnector, ConnectorResult, ConnectorStatus, CircuitState
from app.connectors.circuit_breaker import CircuitBreaker
from app.connectors.retry import ConnectorRetryError, retry_operation

logger = structlog.get_logger()


class ConnectorRegistry:
    """Central registry for all connector instances.

    Manages connector lifecycle, circuit breakers, health checks,
    and provides a unified execute() interface.
    """

    def __init__(self) -> None:
        self._connectors: dict[str, BaseConnector] = {}
        self._breakers: dict[str, CircuitBreaker] = {}
        self._health_cache: dict[str, ConnectorStatus] = {}

    def register(self, connector: BaseConnector) -> None:
        """Register a connector and create its circuit breaker."""
        self._connectors[connector.connector_id] = connector
        self._breakers[connector.connector_id] = CircuitBreaker(
            connector_id=connector.connector_id
        )
        self._health_cache[connector.connector_id] = ConnectorStatus.UNKNOWN
        logger.info("connector_registered", connector_id=connector.connector_id, name=connector.name)

    def get(self, connector_id: str) -> BaseConnector | None:
        """Get a registered connector by ID."""
        return self._connectors.get(connector_id)

    def get_circuit_breaker(self, connector_id: str) -> CircuitBreaker | None:
        """Get the circuit breaker for a registered connector."""
        return self._breakers.get(connector_id)

    def list_all(self) -> list[dict[str, Any]]:
        """List all connectors with their status."""
        result = []
        for cid, connector in self._connectors.items():
            breaker = self._breakers.get(cid)
            result.append({
                "id": cid,
                "name": connector.name,
                "base_url": connector.base_url,
                "health": self._health_cache.get(cid, ConnectorStatus.UNKNOWN),
                "circuit_state": breaker.state if breaker else CircuitState.CLOSED,
            })
        return result

    async def execute(
        self,
        connector_id: str,
        operation: str,
        payload: dict[str, Any] | None = None,
        *,
        dry_run: bool = False,
        idempotency_key: str | None = None,
        max_retries: int = 3,
    ) -> ConnectorResult:
        """Execute an operation through the registry with circuit breaker + retry."""
        connector = self._connectors.get(connector_id)
        if not connector:
            return ConnectorResult(
                success=False,
                error=f"Connector '{connector_id}' not found",
                connector_id=connector_id,
                operation=operation,
            )

        breaker = self._breakers[connector_id]

        # Circuit breaker check
        if not breaker.can_execute():
            logger.warning("circuit_open", connector_id=connector_id, operation=operation)
            return ConnectorResult(
                success=False,
                error="Circuit breaker is OPEN — connector temporarily unavailable",
                connector_id=connector_id,
                operation=operation,
                status_code=503,
            )

        # Execute with retry
        start = time.perf_counter()
        try:
            result = await retry_operation(
                connector.execute,
                operation,
                payload,
                dry_run=dry_run,
                idempotency_key=idempotency_key,
                max_retries=max_retries,
            )
            result.latency_ms = int((time.perf_counter() - start) * 1000)
            result.connector_id = connector_id
            result.operation = operation

            if result.success:
                breaker.record_success()
            else:
                breaker.record_failure()

            return result

        except ConnectorRetryError as e:
            breaker.record_failure()
            latency = int((time.perf_counter() - start) * 1000)
            return ConnectorResult(
                success=False,
                error=f"Connector call failed after retries: {e}",
                connector_id=connector_id,
                operation=operation,
                latency_ms=latency,
            )
        except Exception as e:
            breaker.record_failure()
            latency = int((time.perf_counter() - start) * 1000)
            logger.error("connector_execute_error", connector_id=connector_id, error=str(e))
            return ConnectorResult(
                success=False,
                error=str(e),
                connector_id=connector_id,
                operation=operation,
                latency_ms=latency,
            )

    async def check_health(self, connector_id: str) -> ConnectorStatus:
        """Run health check for a single connector."""
        connector = self._connectors.get(connector_id)
        if not connector:
            return ConnectorStatus.UNKNOWN

        try:
            status = await connector.health_check()
            self._health_cache[connector_id] = status
            return status
        except Exception:
            self._health_cache[connector_id] = ConnectorStatus.DOWN
            return ConnectorStatus.DOWN

    async def check_all_health(self) -> dict[str, ConnectorStatus]:
        """Run health checks for all connectors."""
        results: dict[str, ConnectorStatus] = {}
        for cid in self._connectors:
            results[cid] = await self.check_health(cid)
        return results


# Singleton instance
registry = ConnectorRegistry()
