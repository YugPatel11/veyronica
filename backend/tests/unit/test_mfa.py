"""Tests for MFA (TOTP) module.

EPIC-04-T03: Verify TOTP generation and validation.
"""

import time
from unittest.mock import patch

import pytest

from app.core.mfa import (
    MFA_REQUIRED_ROLES,
    generate_totp_secret,
    get_totp_uri,
    requires_mfa,
    verify_totp,
    _generate_hotp,
)


class TestTOTPSecret:
    """Test TOTP secret generation."""

    def test_generates_base32_string(self) -> None:
        secret = generate_totp_secret()
        assert isinstance(secret, str)
        assert len(secret) >= 20

    def test_generates_unique_secrets(self) -> None:
        secrets = {generate_totp_secret() for _ in range(10)}
        assert len(secrets) == 10


class TestTOTPUri:
    """Test TOTP URI generation."""

    def test_generates_valid_otpauth_uri(self) -> None:
        uri = get_totp_uri("JBSWY3DPEHPK3PXP", "admin@nexus.edu")
        assert uri.startswith("otpauth://totp/NEXUS:admin@nexus.edu")
        assert "secret=" in uri
        assert "issuer=NEXUS" in uri
        assert "digits=6" in uri
        assert "period=30" in uri


class TestTOTPVerification:
    """Test TOTP code verification."""

    def test_valid_code_accepted(self) -> None:
        secret = "JBSWY3DPEHPK3PXP"
        # Generate the current valid code
        current_counter = int(time.time()) // 30
        valid_code = _generate_hotp(secret, current_counter)
        assert verify_totp(secret, valid_code)

    def test_invalid_code_rejected(self) -> None:
        secret = "JBSWY3DPEHPK3PXP"
        assert not verify_totp(secret, "000000")

    def test_wrong_length_rejected(self) -> None:
        assert not verify_totp("JBSWY3DPEHPK3PXP", "12345")
        assert not verify_totp("JBSWY3DPEHPK3PXP", "1234567")

    def test_non_digit_rejected(self) -> None:
        assert not verify_totp("JBSWY3DPEHPK3PXP", "abcdef")

    def test_window_allows_adjacent_codes(self) -> None:
        secret = "JBSWY3DPEHPK3PXP"
        current_counter = int(time.time()) // 30
        # Previous code should be valid with window=1
        prev_code = _generate_hotp(secret, current_counter - 1)
        assert verify_totp(secret, prev_code, window=1)


class TestMFARequirement:
    """Test MFA role requirement checking."""

    def test_admin_requires_mfa(self) -> None:
        assert requires_mfa(["admin"])

    def test_approver_requires_mfa(self) -> None:
        assert requires_mfa(["approver"])

    def test_faculty_does_not_require_mfa(self) -> None:
        assert not requires_mfa(["faculty"])

    def test_operator_does_not_require_mfa(self) -> None:
        assert not requires_mfa(["operator"])

    def test_mixed_roles_with_admin(self) -> None:
        assert requires_mfa(["faculty", "admin"])

    def test_empty_roles(self) -> None:
        assert not requires_mfa([])
