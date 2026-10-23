"""Unit tests for JWT authentication and password hashing."""

from __future__ import annotations

import pytest

from app.core.auth import (
    TokenType,
    create_access_token,
    create_refresh_token,
    create_token_pair,
    decode_token,
    hash_password,
    verify_password,
)
from app.core.errors import UnauthorizedError


class TestPasswordHashing:
    """Tests for Argon2id password hashing."""

    def test_hash_and_verify_correct_password(self) -> None:
        hashed = hash_password("secure_password_123")
        assert verify_password("secure_password_123", hashed)

    def test_reject_wrong_password(self) -> None:
        hashed = hash_password("correct_password")
        assert not verify_password("wrong_password", hashed)

    def test_hash_is_not_plaintext(self) -> None:
        hashed = hash_password("mypassword")
        assert "mypassword" not in hashed
        assert hashed.startswith("$argon2")

    def test_different_hashes_for_same_password(self) -> None:
        h1 = hash_password("same_password")
        h2 = hash_password("same_password")
        assert h1 != h2  # salt makes them unique


class TestAccessToken:
    """Tests for access token creation and decoding."""

    def test_create_and_decode_access_token(self) -> None:
        token = create_access_token("user_123", ["admin"])
        payload = decode_token(token, TokenType.ACCESS)
        assert payload.sub == "user_123"
        assert payload.token_type == TokenType.ACCESS
        assert "admin" in payload.roles
        assert payload.jti  # JTI must be present

    def test_decode_with_wrong_type_raises(self) -> None:
        token = create_access_token("user_123", ["admin"])
        with pytest.raises(UnauthorizedError, match="Expected refresh"):
            decode_token(token, TokenType.REFRESH)

    def test_decode_invalid_token_raises(self) -> None:
        with pytest.raises(UnauthorizedError, match="Invalid token"):
            decode_token("not.a.valid.token", TokenType.ACCESS)

    def test_access_token_contains_roles(self) -> None:
        token = create_access_token("u1", ["faculty", "approver"])
        payload = decode_token(token, TokenType.ACCESS)
        assert set(payload.roles) == {"faculty", "approver"}


class TestRefreshToken:
    """Tests for refresh token creation and decoding."""

    def test_create_and_decode_refresh_token(self) -> None:
        token = create_refresh_token("user_456", ["faculty"])
        payload = decode_token(token, TokenType.REFRESH)
        assert payload.sub == "user_456"
        assert payload.token_type == TokenType.REFRESH

    def test_refresh_token_not_usable_as_access(self) -> None:
        token = create_refresh_token("user_456", ["faculty"])
        with pytest.raises(UnauthorizedError, match="Expected access"):
            decode_token(token, TokenType.ACCESS)


class TestTokenPair:
    """Tests for token pair creation."""

    def test_create_token_pair_returns_both(self) -> None:
        pair = create_token_pair("user_789", ["admin"])
        assert "access_token" in pair
        assert "refresh_token" in pair
        assert pair["token_type"] == "bearer"

        # Both tokens are valid
        access = decode_token(pair["access_token"], TokenType.ACCESS)
        refresh = decode_token(pair["refresh_token"], TokenType.REFRESH)
        assert access.sub == "user_789"
        assert refresh.sub == "user_789"
