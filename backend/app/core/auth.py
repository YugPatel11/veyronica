"""JWT authentication: token creation, validation, and refresh rotation.

Implements:
- Short-lived access tokens (15 min default)
- Long-lived refresh tokens (7 days default) with rotation
- Argon2id password hashing (OWASP recommended)
- Token type enforcement (access vs refresh)
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings
from app.core.errors import UnauthorizedError

# ── Password hashing ────────────────────────────────────────────────────────

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=65536,  # 64 MB
    argon2__time_cost=3,
    argon2__parallelism=4,
)


def hash_password(password: str) -> str:
    """Hash a plaintext password using Argon2id."""
    return str(pwd_context.hash(password))


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a stored hash."""
    return bool(pwd_context.verify(plain, hashed))


# ── JWT tokens ───────────────────────────────────────────────────────────────


class TokenType:
    ACCESS = "access"
    REFRESH = "refresh"


class TokenPayload:
    """Parsed and validated JWT payload."""

    def __init__(
        self,
        sub: str,
        token_type: str,
        roles: list[str],
        jti: str,
        exp: datetime,
        iat: datetime,
    ) -> None:
        self.sub = sub
        self.token_type = token_type
        self.roles = roles
        self.jti = jti
        self.exp = exp
        self.iat = iat


def create_access_token(
    user_id: str,
    roles: list[str],
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Create a short-lived access token."""
    settings = get_settings()
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=settings.jwt_access_token_expire_minutes)

    claims: dict[str, Any] = {
        "sub": user_id,
        "type": TokenType.ACCESS,
        "roles": roles,
        "jti": str(uuid4()),
        "iat": now,
        "exp": expire,
    }
    if extra_claims:
        claims.update(extra_claims)

    return str(
        jwt.encode(
            claims,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )
    )


def create_refresh_token(user_id: str, roles: list[str]) -> str:
    """Create a long-lived refresh token for rotation."""
    settings = get_settings()
    now = datetime.now(UTC)
    expire = now + timedelta(days=settings.jwt_refresh_token_expire_days)

    claims: dict[str, Any] = {
        "sub": user_id,
        "type": TokenType.REFRESH,
        "roles": roles,
        "jti": str(uuid4()),
        "iat": now,
        "exp": expire,
    }

    return str(
        jwt.encode(
            claims,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )
    )


def decode_token(token: str, expected_type: str = TokenType.ACCESS) -> TokenPayload:
    """Decode and validate a JWT token.

    Raises UnauthorizedError on invalid, expired, or wrong-type tokens.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as e:
        raise UnauthorizedError(f"Invalid token: {e}") from e

    token_type = payload.get("type")
    if token_type != expected_type:
        raise UnauthorizedError(
            f"Expected {expected_type} token, got {token_type}"
        )

    return TokenPayload(
        sub=payload["sub"],
        token_type=token_type,
        roles=payload.get("roles", []),
        jti=payload.get("jti", ""),
        exp=datetime.fromtimestamp(payload["exp"], tz=UTC),
        iat=datetime.fromtimestamp(payload["iat"], tz=UTC),
    )


def create_token_pair(
    user_id: str, roles: list[str]
) -> dict[str, str]:
    """Create an access + refresh token pair."""
    return {
        "access_token": create_access_token(user_id, roles),
        "refresh_token": create_refresh_token(user_id, roles),
        "token_type": "bearer",
    }
