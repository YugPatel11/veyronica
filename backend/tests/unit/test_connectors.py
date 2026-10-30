"""Unit tests for Connector Hub.

EPIC-05-T13: Unit tests for connector hub (≥ 90% coverage on hub logic).
Tests circuit breaker, retry, registry, dry run, and connector adapters.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from app.connectors import CircuitState, ConnectorResult, ConnectorStatus, DiffResult
from app.connectors.circuit_breaker import CircuitBreaker
from app.connectors.crm import CRMConnector
from app.connectors.email import EmailConnector
from app.connectors.erp import ERPConnector
from app.connectors.http_connector import HTTPConnector
from app.connectors.lms import LMSConnector
from app.connectors.registry import ConnectorRegistry
from app.connectors.retry import ConnectorRetryError, retry_operation
from app.connectors.storage import StorageConnector
from app.connectors.telegram import TelegramConnector


# ── Circuit Breaker Tests ───────────────────────────────────────────────────

class TestCircuitBreaker:
    @pytest.mark.asyncio
    async def test_starts_closed(self) -> None:
        cb = CircuitBreaker("test-conn", failure_threshold=3, recovery_timeout=1.0)
        assert cb.state == CircuitState.CLOSED
        assert cb.can_execute() is True

    @pytest.mark.asyncio
    async def test_opens_after_threshold_failures(self) -> None:
        cb = CircuitBreaker("test-conn", failure_threshold=3, recovery_timeout=1.0)
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        assert cb.can_execute() is False

    @pytest.mark.asyncio
    async def test_transitions_to_half_open_after_timeout(self) -> None:
        cb = CircuitBreaker("test-conn", failure_threshold=2, recovery_timeout=0.05)
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.OPEN

        await asyncio.sleep(0.06)
        assert cb.can_execute() is True
        assert cb.state == CircuitState.HALF_OPEN

    @pytest.mark.asyncio
    async def test_recovers_to_closed_on_success(self) -> None:
        cb = CircuitBreaker("test-conn", failure_threshold=2, recovery_timeout=0.05, half_open_max=1)
        cb.record_failure()
        cb.record_failure()
        await asyncio.sleep(0.06)
        assert cb.can_execute() is True
        assert cb.state == CircuitState.HALF_OPEN

        cb.record_success()
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0


# ── Retry Logic Tests ────────────────────────────────────────────────────────

class TestRetryLogic:
    @pytest.mark.asyncio
    async def test_succeeds_on_first_try(self) -> None:
        call_count = 0

        async def func() -> str:
            nonlocal call_count
            call_count += 1
            return "ok"

        res = await retry_operation(func, max_retries=3, initial_wait=0.01, jitter=0.0)
        assert res == "ok"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retries_and_succeeds(self) -> None:
        call_count = 0

        async def flaky() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectorRetryError("Temporary glitch")
            return "recovered"

        res = await retry_operation(flaky, max_retries=3, initial_wait=0.01, jitter=0.0)
        assert res == "recovered"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_exhausts_retries_and_raises(self) -> None:
        async def always_fails() -> None:
            raise ConnectorRetryError("Fatal error")

        with pytest.raises(ConnectorRetryError, match="Fatal error"):
            await retry_operation(always_fails, max_retries=2, initial_wait=0.01, jitter=0.0)


# ── Connector Registry & Adapters Tests ──────────────────────────────────────

class TestConnectorRegistry:
    @pytest.fixture
    def custom_registry(self) -> ConnectorRegistry:
        reg = ConnectorRegistry()
        reg.register(ERPConnector("campus-erp", "http://localhost:8101", "Campus ERP"))
        reg.register(LMSConnector("lms", "http://localhost:8102", "LMS"))
        reg.register(CRMConnector("student-crm", "http://localhost:8103", "Student CRM"))
        reg.register(EmailConnector("email-smtp", "localhost", "Email"))
        reg.register(TelegramConnector("telegram-bot", "http://localhost", "Telegram"))
        reg.register(StorageConnector("object-storage", "http://localhost:9000", "Storage"))
        return reg

    def test_list_all(self, custom_registry: ConnectorRegistry) -> None:
        connectors = custom_registry.list_all()
        assert len(connectors) == 6
        ids = [c["id"] for c in connectors]
        assert "campus-erp" in ids
        assert "lms" in ids
        assert "student-crm" in ids

    @pytest.mark.asyncio
    async def test_execute_unknown_connector(self, custom_registry: ConnectorRegistry) -> None:
        res = await custom_registry.execute("unknown-sys", "get_data")
        assert res.success is False
        assert "not found" in (res.error or "").lower()

    @pytest.mark.asyncio
    async def test_execute_circuit_breaker_open(self, custom_registry: ConnectorRegistry) -> None:
        breaker = custom_registry.get_circuit_breaker("campus-erp")
        assert breaker is not None
        # Force circuit open
        breaker.failure_threshold = 3
        breaker.record_failure()
        breaker.record_failure()
        breaker.record_failure()

        res = await custom_registry.execute("campus-erp", "get_students")
        assert res.success is False
        assert "circuit breaker" in (res.error or "").lower()

    @pytest.mark.asyncio
    async def test_dry_run_diff_generation(self, custom_registry: ConnectorRegistry) -> None:
        conn = custom_registry.get("campus-erp")
        assert conn is not None
        diff = conn._make_diff({"score": 50}, {"score": 85})
        assert isinstance(diff, DiffResult)
        assert diff.before == {"score": 50}
        assert diff.after == {"score": 85}

    @pytest.mark.asyncio
    async def test_erp_operations_dispatch(self, custom_registry: ConnectorRegistry) -> None:
        conn = custom_registry.get("campus-erp")
        assert conn is not None
        with patch.object(conn, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = (200, [{"id": "s1", "name": "Test Student"}])
            res = await conn.execute("get_students", {"division": "A"})
            assert res.success is True
            assert res.data == [{"id": "s1", "name": "Test Student"}]
