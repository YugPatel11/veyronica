"""Retry logic with exponential backoff + jitter.

EPIC-05-T02: Retry wrapper using tenacity.
"""

from __future__ import annotations

import random
from typing import Any, Callable, TypeVar

import structlog
from tenacity import (
    RetryCallState,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

logger = structlog.get_logger()

T = TypeVar("T")

# Default retry config
MAX_RETRIES = 3
INITIAL_WAIT = 1  # seconds
MAX_WAIT = 30  # seconds
JITTER = 2  # max random jitter seconds


class ConnectorRetryError(Exception):
    """Raised when a connector call should be retried."""


def _log_retry(retry_state: RetryCallState) -> None:
    """Log each retry attempt."""
    logger.warning(
        "connector_retry",
        attempt=retry_state.attempt_number,
        wait=round(retry_state.next_action.sleep if retry_state.next_action else 0, 2),  # type: ignore[union-attr]
    )


def with_retry(
    max_retries: int = MAX_RETRIES,
    initial_wait: float = INITIAL_WAIT,
    max_wait: float = MAX_WAIT,
    jitter: float = JITTER,
):
    """Decorator for retrying connector calls with exponential backoff + jitter."""
    return retry(
        retry=retry_if_exception_type(ConnectorRetryError),
        stop=stop_after_attempt(max_retries + 1),
        wait=wait_exponential_jitter(
            initial=initial_wait,
            max=max_wait,
            jitter=jitter,
        ),
        before_sleep=_log_retry,
        reraise=True,
    )


async def retry_operation(
    func: Callable[..., Any],
    *args: Any,
    max_retries: int = MAX_RETRIES,
    **kwargs: Any,
) -> Any:
    """Execute a function with retry logic (imperative style)."""
    last_error: Exception | None = None

    for attempt in range(1, max_retries + 2):
        try:
            return await func(*args, **kwargs)
        except ConnectorRetryError as e:
            last_error = e
            if attempt <= max_retries:
                wait = min(INITIAL_WAIT * (2 ** (attempt - 1)), MAX_WAIT)
                wait += random.uniform(0, JITTER)
                logger.warning(
                    "connector_retry",
                    attempt=attempt,
                    wait=round(wait, 2),
                    error=str(e),
                )
                import asyncio
                await asyncio.sleep(wait)
            else:
                raise

    raise last_error or RuntimeError("Retry exhausted")
