"""Authentication endpoints: login, refresh, and logout.

EPIC-04-T01: JWT auth with access + refresh token rotation, Argon2 hashing.
EPIC-04-T04: Redis-backed token blacklist for logout/revocation.
EPIC-04-T09: Account lockout after 5 failed logins (15 min cooldown).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Request
from fastapi.responses import Response
from pydantic import BaseModel, EmailStr, Field

from app.core.auth import (
    TokenPayload,
    TokenType,
    create_token_pair,
    decode_token,
    hash_password,
    verify_password,
)
from app.core.errors import UnauthorizedError
from app.core.token_blacklist import blacklist_token, is_token_blacklisted
from app.core.rbac import CurrentUser

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ── Constants ────────────────────────────────────────────────────────────────

MAX_FAILED_LOGINS = 5
LOCKOUT_DURATION_MINUTES = 15


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


# ── Hardcoded dev user (replaced by DB lookup in EPIC-03) ────────────────────

_DEV_USERS: dict[str, dict[str, str | list[str] | int | datetime | None]] = {
    "admin@nexus.edu": {
        "id": "usr_admin_001",
        "password_hash": hash_password("nexus_admin_2026"),
        "roles": ["admin"],
        "name": "Dr. Ananya Krishnan",
        "failed_login_count": 0,
        "locked_until": None,
    },
    "faculty@nexus.edu": {
        "id": "usr_faculty_001",
        "password_hash": hash_password("nexus_faculty_2026"),
        "roles": ["faculty"],
        "name": "Dr. Riya Patel",
        "failed_login_count": 0,
        "locked_until": None,
    },
    "approver@nexus.edu": {
        "id": "usr_approver_001",
        "password_hash": hash_password("nexus_approver_2026"),
        "roles": ["approver"],
        "name": "Dr. Meera Iyer",
        "failed_login_count": 0,
        "locked_until": None,
    },
    "operator@nexus.edu": {
        "id": "usr_operator_001",
        "password_hash": hash_password("nexus_operator_2026"),
        "roles": ["operator"],
        "name": "Vikram Desai",
        "failed_login_count": 0,
        "locked_until": None,
    },
}


def _check_lockout(user: dict[str, str | list[str] | int | datetime | None]) -> None:
    """Check if user account is locked out."""
    locked_until = user.get("locked_until")
    if locked_until and isinstance(locked_until, datetime):
        if datetime.now(UTC) < locked_until:
            remaining = int((locked_until - datetime.now(UTC)).total_seconds() / 60) + 1
            raise UnauthorizedError(
                f"Account locked due to too many failed attempts. Try again in {remaining} minutes."
            )
        else:
            # Lockout expired — reset
            user["failed_login_count"] = 0
            user["locked_until"] = None


def _record_failed_login(user: dict[str, str | list[str] | int | datetime | None]) -> None:
    """Record a failed login attempt and lock if threshold reached."""
    count = int(user.get("failed_login_count", 0)) + 1
    user["failed_login_count"] = count

    if count >= MAX_FAILED_LOGINS:
        user["locked_until"] = datetime.now(UTC) + timedelta(
            minutes=LOCKOUT_DURATION_MINUTES
        )


def _record_successful_login(user: dict[str, str | list[str] | int | datetime | None]) -> None:
    """Reset failed login count on successful login."""
    user["failed_login_count"] = 0
    user["locked_until"] = None


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, request: Request) -> TokenResponse:
    """Authenticate a user and return access + refresh tokens.

    Implements account lockout after 5 failed attempts (15 min cooldown).
    """
    user = _DEV_USERS.get(body.email)
    if user is None:
        raise UnauthorizedError("Invalid email or password")

    # Check lockout
    _check_lockout(user)

    if not verify_password(body.password, str(user["password_hash"])):
        _record_failed_login(user)
        raise UnauthorizedError("Invalid email or password")

    _record_successful_login(user)

    tokens = create_token_pair(
        user_id=str(user["id"]),
        roles=list(user["roles"]),
    )
    return TokenResponse(**tokens)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest) -> TokenResponse:
    """Exchange a valid refresh token for a new token pair (rotation).

    The old refresh token is blacklisted to prevent reuse.
    """
    payload = decode_token(body.refresh_token, expected_type=TokenType.REFRESH)

    # Check if the old refresh token has been blacklisted
    if await is_token_blacklisted(payload.jti):
        raise UnauthorizedError("Token has been revoked")

    # Blacklist the old refresh token
    await blacklist_token(payload.jti, payload.exp)

    # Issue a completely new pair
    tokens = create_token_pair(
        user_id=payload.sub,
        roles=payload.roles,
    )
    return TokenResponse(**tokens)


@router.post("/logout", status_code=204, response_class=Response)
async def logout(user: CurrentUser) -> Response:
    """Invalidate the current session by blacklisting the token."""
    await blacklist_token(user.jti, user.exp)
    return Response(status_code=204)


@router.get("/me")
async def get_current_user_info(user: CurrentUser) -> dict:
    """Return information about the currently authenticated user."""
    return {
        "user_id": user.sub,
        "roles": user.roles,
        "token_type": user.token_type,
        "issued_at": user.iat.isoformat(),
        "expires_at": user.exp.isoformat(),
    }
