"""Unit tests for health endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.unit
async def test_health_returns_200(client: AsyncClient) -> None:
    """GET /health returns 200 with correct structure."""
    response = await client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "nexus-api"


@pytest.mark.unit
async def test_health_no_auth_required(client: AsyncClient) -> None:
    """Health endpoint is publicly accessible."""
    response = await client.get("/health")
    assert response.status_code == 200
