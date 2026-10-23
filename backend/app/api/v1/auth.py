"""Authentication endpoints: login, refresh, and logout."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import Response
from pydantic import BaseModel, EmailStr, Field

from app.core.auth import (
    TokenType,
    create_token_pair,
    decode_token,
    hash_password,
    verify_password,
)
from app.core.errors import UnauthorizedError

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ── Request / Response models ────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"  # noqa: S105


class RefreshRequest(BaseModel):
    refresh_token: str


# ── Hardcoded dev user (replaced by DB lookup in Phase 1 EPIC-03) ────────

_DEV_USERS: dict[str, dict[str, str | list[str]]] = {
    "admin@nexus.edu": {
        "id": "usr_admin_001",
        "password_hash": hash_password("nexus_admin_2026"),
        "roles": ["admin"],
        "name": "System Admin",
    },
    "faculty@nexus.edu": {
        "id": "usr_faculty_001",
        "password_hash": hash_password("nexus_faculty_2026"),
        "roles": ["faculty"],
        "name": "Dr. Riya Patel",
    },
}


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest) -> TokenResponse:
    """Authenticate a user and return access + refresh tokens."""
    user = _DEV_USERS.get(body.email)
    if user is None:
        raise UnauthorizedError("Invalid email or password")

    if not verify_password(body.password, str(user["password_hash"])):
        raise UnauthorizedError("Invalid email or password")

    tokens = create_token_pair(
        user_id=str(user["id"]),
        roles=list(user["roles"]),
    )
    return TokenResponse(**tokens)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest) -> TokenResponse:
    """Exchange a valid refresh token for a new token pair (rotation)."""
    payload = decode_token(body.refresh_token, expected_type=TokenType.REFRESH)

    # Issue a completely new pair — old refresh token is effectively invalidated
    # (In Phase 1 EPIC-04, add Redis blacklist for the old refresh token)
    tokens = create_token_pair(
        user_id=payload.sub,
        roles=payload.roles,
    )
    return TokenResponse(**tokens)


@router.post("/logout", status_code=204, response_class=Response)
async def logout() -> Response:
    """Invalidate the current session.

    In Phase 1 EPIC-04, this will add the token JTI to a Redis blacklist.
    For now, the client simply discards the token.
    """
    return Response(status_code=204)
