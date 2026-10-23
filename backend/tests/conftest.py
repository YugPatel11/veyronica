"""Shared test fixtures for the NEXUS backend test suite."""

from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.auth import create_access_token
from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client for testing FastAPI endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def admin_token() -> str:
    """Valid admin access token for authenticated test requests."""
    return create_access_token(
        user_id="usr_admin_001",
        roles=["admin"],
    )


@pytest.fixture
def faculty_token() -> str:
    """Valid faculty access token for authenticated test requests."""
    return create_access_token(
        user_id="usr_faculty_001",
        roles=["faculty"],
    )


@pytest.fixture
def auth_headers(admin_token: str) -> dict[str, str]:
    """Authorization headers with admin token."""
    return {"Authorization": f"Bearer {admin_token}"}
