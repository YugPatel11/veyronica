"""FastAPI application factory.

Creates the NEXUS API application with all middleware, routers, and
lifecycle hooks configured.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import sentry_sdk
import structlog
from fastapi import FastAPI

from app.core.config import get_settings
from app.core.errors import register_error_handlers
from app.core.logging import setup_logging
from app.core.middleware import register_middleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown lifecycle."""
    settings = get_settings()
    logger = structlog.get_logger()

    # ── Startup ──────────────────────────────────────────────────────────
    setup_logging()

    # Validate critical settings
    if settings.is_production and "CHANGE-ME" in settings.jwt_secret_key:
        raise RuntimeError(
            "FATAL: jwt_secret_key has not been changed from default. "
            "Set JWT_SECRET_KEY to a secure random value."
        )

    # Initialise Sentry
    if settings.sentry_dsn:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            traces_sample_rate=settings.sentry_traces_sample_rate,
            environment=settings.nexus_env,
            release="nexus-api@0.1.0",
        )
        logger.info("sentry_initialized", environment=settings.nexus_env)

    logger.info(
        "nexus_api_starting",
        environment=settings.nexus_env,
        debug=settings.debug,
        log_level=settings.log_level,
    )

    yield

    # ── Shutdown ─────────────────────────────────────────────────────────
    logger.info("nexus_api_shutting_down")


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="NEXUS API",
        description="Agentic Workflow Intelligence Platform",
        version="0.1.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # Register middleware (CORS, security headers, logging, request-ID)
    register_middleware(app)

    # Register centralised error handlers
    register_error_handlers(app)

    # Register routers
    from app.api.v1.auth import router as auth_router
    from app.api.v1.health import router as health_router

    # Health endpoints at root (no prefix) for orchestrators
    app.include_router(health_router)

    # API v1 routes
    app.include_router(auth_router, prefix=settings.api_prefix)

    return app


# Application instance for uvicorn
app = create_app()
