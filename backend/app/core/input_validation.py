"""Input validation middleware.

EPIC-04-T10: Size limits, content-type enforcement.
"""

from __future__ import annotations

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.errors import AppError, ErrorCode

logger = structlog.get_logger()

# Maximum request body size: 10 MB
MAX_BODY_SIZE = 10 * 1024 * 1024

# Allowed content types for POST/PUT/PATCH
ALLOWED_CONTENT_TYPES = {
    "application/json",
    "multipart/form-data",
    "application/x-www-form-urlencoded",
    "application/octet-stream",
}


class InputValidationMiddleware(BaseHTTPMiddleware):
    """Validate request body size and content type."""

    SKIP_PATHS = {"/health", "/ready"}

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        # Check content-length on body-carrying requests
        if request.method in ("POST", "PUT", "PATCH"):
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > MAX_BODY_SIZE:
                raise AppError(
                    message=f"Request body too large (max {MAX_BODY_SIZE // (1024 * 1024)} MB)",
                    code=ErrorCode.BAD_REQUEST,
                    status_code=413,
                )

            # Check content-type
            content_type = request.headers.get("content-type", "")
            base_type = content_type.split(";")[0].strip().lower()
            if base_type and base_type not in ALLOWED_CONTENT_TYPES:
                raise AppError(
                    message=f"Unsupported content type: {base_type}",
                    code=ErrorCode.BAD_REQUEST,
                    status_code=415,
                )

        return await call_next(request)
