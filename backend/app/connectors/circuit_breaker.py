"""Circuit breaker implementation.

EPIC-05-T03: Circuit breaker (closed → open → half-open).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import structlog

from app.connectors import CircuitState

logger = structlog.get_logger()

# Defaults
DEFAULT_FAILURE_THRESHOLD = 5
DEFAULT_RECOVERY_TIMEOUT = 60  # seconds
DEFAULT_HALF_OPEN_MAX_CALLS = 3


@dataclass
class CircuitBreaker:
    """Per-connector circuit breaker.

    - CLOSED: Normal operation, tracking failures.
    - OPEN: All calls rejected immediately after threshold breached.
    - HALF_OPEN: Allow limited test calls after recovery timeout.
    """

    connector_id: str
    failure_threshold: int = DEFAULT_FAILURE_THRESHOLD
    recovery_timeout: int = DEFAULT_RECOVERY_TIMEOUT
    half_open_max: int = DEFAULT_HALF_OPEN_MAX_CALLS

    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: float = 0.0
    half_open_calls: int = 0

    def can_execute(self) -> bool:
        """Check if a call is allowed through the breaker."""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has elapsed
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self._transition(CircuitState.HALF_OPEN)
                return True
            return False

        if self.state == CircuitState.HALF_OPEN:
            return self.half_open_calls < self.half_open_max

        return False

    def record_success(self) -> None:
        """Record a successful call."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            self.half_open_calls += 1
            if self.success_count >= self.half_open_max:
                self._transition(CircuitState.CLOSED)
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0

    def record_failure(self) -> None:
        """Record a failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitState.HALF_OPEN:
            self._transition(CircuitState.OPEN)
        elif self.state == CircuitState.CLOSED:
            if self.failure_count >= self.failure_threshold:
                self._transition(CircuitState.OPEN)

    def _transition(self, new_state: CircuitState) -> None:
        """Transition to a new state."""
        old = self.state
        self.state = new_state
        logger.info(
            "circuit_breaker_transition",
            connector_id=self.connector_id,
            from_state=old,
            to_state=new_state,
        )
        if new_state == CircuitState.CLOSED:
            self.failure_count = 0
            self.success_count = 0
            self.half_open_calls = 0
        elif new_state == CircuitState.HALF_OPEN:
            self.success_count = 0
            self.half_open_calls = 0
