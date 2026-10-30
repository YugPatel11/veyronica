"""Secrets management — .env validation at startup.

EPIC-04-T08: Validate that all critical secrets are properly configured.
"""

from __future__ import annotations

import structlog

from app.core.config import get_settings

logger = structlog.get_logger()


class SecretValidationError(Exception):
    """Raised when critical secrets are misconfigured."""


_WEAK_DEFAULTS = {
    "change-me",
    "changeme",
    "secret",
    "password",
    "test",
    "example",
    "default",
}


def validate_secrets(*, strict: bool = False) -> list[str]:
    """Validate all critical secrets are properly set.

    Args:
        strict: If True (production), raise on any misconfiguration.
                If False (development), log warnings only.

    Returns:
        List of warning messages for any issues found.
    """
    settings = get_settings()
    warnings: list[str] = []

    # JWT Secret
    if any(weak in settings.jwt_secret_key.lower() for weak in _WEAK_DEFAULTS):
        warnings.append("JWT_SECRET_KEY uses a weak default value")

    if len(settings.jwt_secret_key) < 32:
        warnings.append("JWT_SECRET_KEY should be at least 32 characters")

    # Database URL
    db_url = str(settings.database_url)
    if "nexus_dev" in db_url and settings.is_production:
        warnings.append("DATABASE_URL uses development credentials in production")

    # S3/MinIO
    if settings.s3_access_key == "minioadmin" and settings.is_production:
        warnings.append("S3_ACCESS_KEY uses MinIO default in production")

    # Sentry
    if not settings.sentry_dsn and settings.is_production:
        warnings.append("SENTRY_DSN is not configured for production")

    # Log results
    if warnings:
        for w in warnings:
            logger.warning("secret_validation_warning", issue=w)

        if strict or settings.is_production:
            raise SecretValidationError(
                f"Critical secret issues: {'; '.join(warnings)}"
            )

    return warnings
