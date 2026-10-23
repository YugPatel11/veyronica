"""Multi-Factor Authentication (TOTP) support.

EPIC-04-T03: MFA (TOTP) for admin and approver roles.
Uses pyotp for TOTP generation and verification.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import struct
import time
from typing import Any


def generate_totp_secret() -> str:
    """Generate a new base32-encoded TOTP secret."""
    import secrets
    random_bytes = secrets.token_bytes(20)
    return base64.b32encode(random_bytes).decode("utf-8").rstrip("=")


def get_totp_uri(secret: str, email: str, issuer: str = "NEXUS") -> str:
    """Generate an otpauth:// URI for QR code generation."""
    # Pad secret to valid base32
    padded = secret + "=" * (8 - len(secret) % 8) if len(secret) % 8 else secret
    return f"otpauth://totp/{issuer}:{email}?secret={padded}&issuer={issuer}&digits=6&period=30"


def _generate_hotp(secret: str, counter: int) -> str:
    """Generate an HOTP value for the given counter."""
    # Decode base32 secret
    padded = secret + "=" * (8 - len(secret) % 8) if len(secret) % 8 else secret
    key = base64.b32decode(padded.upper())

    # HMAC-SHA1
    msg = struct.pack(">Q", counter)
    h = hmac.new(key, msg, hashlib.sha1).digest()

    # Dynamic truncation
    offset = h[-1] & 0x0F
    code = struct.unpack(">I", h[offset : offset + 4])[0]
    code = (code & 0x7FFFFFFF) % 1000000

    return str(code).zfill(6)


def verify_totp(secret: str, code: str, window: int = 1) -> bool:
    """Verify a TOTP code against the secret.

    Args:
        secret: Base32-encoded TOTP secret.
        code: The 6-digit code to verify.
        window: Number of time steps to check before/after current.

    Returns:
        True if the code is valid within the window.
    """
    if len(code) != 6 or not code.isdigit():
        return False

    current_time = int(time.time())
    time_step = 30

    for offset in range(-window, window + 1):
        counter = (current_time // time_step) + offset
        expected = _generate_hotp(secret, counter)
        if hmac.compare_digest(expected, code):
            return True

    return False


# Roles that require MFA
MFA_REQUIRED_ROLES = {"admin", "approver"}


def requires_mfa(roles: list[str]) -> bool:
    """Check if any of the user's roles require MFA."""
    return bool(set(roles) & MFA_REQUIRED_ROLES)
