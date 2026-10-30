"""CSRF Protection Middleware.

EPIC-24-T03: CSRF protection for state-changing requests.
Uses double-submit cookie pattern with Bearer token and webhook signature exemptions.
"""

from __future__ import annotations

import hmac
import secrets
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
EXEMPT_PATHS = {
    "/health",
    "/ready",
    "/health/aggregated",
    "/metrics",
    "/api/v1/auth/login",
    "/api/v1/auth/refresh",
    "/api/v1/webhooks",
}


def generate_csrf_token() -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_hex(32)


class CSRFMiddleware(BaseHTTPMiddleware):
    """Enforce CSRF tokens on state-changing requests from browsers.

    Exempts API requests carrying an Authorization: Bearer token or webhook signatures.
    """

    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        if request.method in SAFE_METHODS:
            return await call_next(request)

        # Skip exempt endpoints
        path = request.url.path
        if any(path.startswith(exempt) for exempt in EXEMPT_PATHS):
            return await call_next(request)

        # If Authorization header with Bearer token is present, request is an API call, not standard cookie session
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return await call_next(request)

        # Check for webhook signature
        if "X-Nexus-Signature" in request.headers:
            return await call_next(request)

        # Validate Double-Submit Cookie / Header
        cookie_token = request.cookies.get("nexus_csrf_token")
        header_token = request.headers.get("X-CSRF-Token")

        if not cookie_token or not header_token or not hmac.compare_digest(cookie_token, header_token):
            return JSONResponse(
                status_code=403,
                content={"error": "CSRF validation failed", "detail": "Missing or mismatched X-CSRF-Token"},
            )

        return await call_next(request)
