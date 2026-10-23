"""Unit tests for auth API endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.unit
async def test_login_success(client: AsyncClient) -> None:
    """Valid credentials return a token pair."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@nexus.edu", "password": "nexus_admin_2026"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


@pytest.mark.unit
async def test_login_wrong_password(client: AsyncClient) -> None:
    """Wrong password returns 401."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@nexus.edu", "password": "wrong_password"},
    )
    assert response.status_code == 401
    body = response.json()
    assert body["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.unit
async def test_login_unknown_email(client: AsyncClient) -> None:
    """Unknown email returns 401 (not 404 — don't leak user existence)."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@nexus.edu", "password": "any_password"},
    )
    assert response.status_code == 401


@pytest.mark.unit
async def test_login_short_password_rejected(client: AsyncClient) -> None:
    """Password shorter than 8 chars is rejected by validation."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@nexus.edu", "password": "short"},
    )
    assert response.status_code == 422


@pytest.mark.unit
async def test_refresh_returns_new_pair(client: AsyncClient) -> None:
    """Refresh endpoint returns a new token pair."""
    # First login to get a refresh token
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@nexus.edu", "password": "nexus_admin_2026"},
    )
    refresh_token = login_resp.json()["refresh_token"]

    # Use refresh token to get new pair
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body


@pytest.mark.unit
async def test_refresh_with_access_token_fails(client: AsyncClient) -> None:
    """Access token cannot be used as refresh token."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@nexus.edu", "password": "nexus_admin_2026"},
    )
    access_token = login_resp.json()["access_token"]

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": access_token},
    )
    assert response.status_code == 401
