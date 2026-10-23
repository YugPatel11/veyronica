"""Structured JSON logging via structlog.

All log output is JSON in production and human-readable (coloured) in
development.  Correlation IDs are injected automatically from request context.
"""

from __future__ import annotations

import logging
import sys
from typing import Any, cast

import structlog

from app.core.config import get_settings


def setup_logging() -> None:
    """Configure structlog + stdlib logging for the application."""
    settings = get_settings()
    is_dev = settings.is_development

    # Shared processors for both structlog and stdlib
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if is_dev:
        # Human-readable coloured output for local development
        renderer: structlog.types.Processor = structlog.dev.ConsoleRenderer(
            colors=True,
        )
    else:
        # JSON for production (ingestible by log aggregators)
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, settings.log_level))

    # Quieten noisy third-party loggers
    for name in ("uvicorn.access", "sqlalchemy.engine", "httpx"):
        logging.getLogger(name).setLevel(logging.WARNING)


def get_logger(**initial_values: Any) -> structlog.stdlib.BoundLogger:
    """Return a bound logger with optional initial context values."""
    return cast(structlog.stdlib.BoundLogger, structlog.get_logger(**initial_values))
