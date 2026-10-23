"""Typed application configuration loaded from environment variables.

All settings are validated at startup via Pydantic. The app refuses to start
if required values are missing or malformed.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings — loaded from environment / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Environment ──────────────────────────────────────────────────────
    nexus_env: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # ── API ──────────────────────────────────────────────────────────────
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    allowed_origins: list[str] = Field(default=["http://localhost:3000"])

    # ── Database ─────────────────────────────────────────────────────────
    database_url: PostgresDsn | str = Field(
        default="postgresql+asyncpg://nexus:nexus_dev@localhost:5432/nexus_db"
    )
    db_pool_size: int = 20
    db_max_overflow: int = 10
    db_echo: bool = False

    # ── Redis ────────────────────────────────────────────────────────────
    redis_url: RedisDsn | str = Field(default="redis://localhost:6379/0")
    redis_cache_ttl: int = 3600  # seconds

    # ── Auth (JWT) ───────────────────────────────────────────────────────
    jwt_secret_key: str = Field(
        default="CHANGE-ME-IN-PRODUCTION-use-openssl-rand-hex-64"
    )
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7

    # ── Object Storage (S3 / MinIO) ──────────────────────────────────────
    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"  # noqa: S105
    s3_bucket: str = "nexus-uploads"

    # ── Email (SMTP) ─────────────────────────────────────────────────────
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@nexus.edu"

    # ── Celery ───────────────────────────────────────────────────────────
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # ── Sentry ───────────────────────────────────────────────────────────
    sentry_dsn: str = ""
    sentry_traces_sample_rate: float = 0.1

    # ── Feature Flags ────────────────────────────────────────────────────
    sandbox_demo_mode: bool = False
    sandbox_chaos_mode: bool = False

    # ── Rate Limiting ────────────────────────────────────────────────────
    rate_limit_per_user: int = 100  # requests per minute
    rate_limit_per_ip: int = 200

    @field_validator("jwt_secret_key")
    @classmethod
    def warn_default_secret(cls, v: str) -> str:
        """Refuse to start in production with the default secret."""
        # Validation is done at startup; see main.py lifespan
        return v

    @property
    def is_production(self) -> bool:
        return self.nexus_env == "production"

    @property
    def is_development(self) -> bool:
        return self.nexus_env == "development"

    @property
    def database_url_sync(self) -> str:
        """Synchronous database URL for Alembic."""
        return str(self.database_url).replace("+asyncpg", "")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
