"""Centralised error handling and structured error taxonomy.

Every error response follows the same JSON shape:
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Human-readable message",
        "details": [...],  // optional
        "correlation_id": "abc-123"
    }
}
"""

from __future__ import annotations

from typing import Any
from uuid import uuid4

import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = structlog.get_logger()


# ── Error codes ──────────────────────────────────────────────────────────────

class ErrorCode:
    """Structured error codes for the API."""

    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    CONFLICT = "CONFLICT"
    RATE_LIMITED = "RATE_LIMITED"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    BAD_REQUEST = "BAD_REQUEST"


# ── Error response model ─────────────────────────────────────────────────────

class ErrorDetail(BaseModel):
    """Single error detail (e.g., one field validation error)."""

    field: str | None = None
    message: str
    code: str | None = None


class ErrorResponse(BaseModel):
    """Standard error envelope."""

    code: str
    message: str
    details: list[ErrorDetail] | None = None
    correlation_id: str


class ErrorEnvelope(BaseModel):
    """Top-level error wrapper."""

    error: ErrorResponse


# ── Application exceptions ───────────────────────────────────────────────────

class AppError(Exception):
    """Base application exception with structured error info."""

    def __init__(
        self,
        message: str,
        code: str = ErrorCode.INTERNAL_ERROR,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: list[ErrorDetail] | None = None,
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, resource: str, identifier: Any = None) -> None:
        msg = f"{resource} not found"
        if identifier is not None:
            msg = f"{resource} '{identifier}' not found"
        super().__init__(
            message=msg,
            code=ErrorCode.NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Authentication required") -> None:
        super().__init__(
            message=message,
            code=ErrorCode.UNAUTHORIZED,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class ForbiddenError(AppError):
    def __init__(self, message: str = "Insufficient permissions") -> None:
        super().__init__(
            message=message,
            code=ErrorCode.FORBIDDEN,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class ConflictError(AppError):
    def __init__(self, message: str = "Resource conflict") -> None:
        super().__init__(
            message=message,
            code=ErrorCode.CONFLICT,
            status_code=status.HTTP_409_CONFLICT,
        )


class RateLimitedError(AppError):
    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(
            message=message,
            code=ErrorCode.RATE_LIMITED,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


# ── Error response builder ──────────────────────────────────────────────────

def _build_error_response(
    status_code: int,
    code: str,
    message: str,
    details: list[ErrorDetail] | None = None,
) -> JSONResponse:
    correlation_id = str(uuid4())
    return JSONResponse(
        status_code=status_code,
        content=ErrorEnvelope(
            error=ErrorResponse(
                code=code,
                message=message,
                details=details,
                correlation_id=correlation_id,
            )
        ).model_dump(),
    )


# ── Exception handlers ──────────────────────────────────────────────────────

async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    """Handle application-defined errors."""
    logger.warning(
        "app_error",
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
    )
    return _build_error_response(
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
        details=exc.details,
    )


async def validation_error_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic / FastAPI validation errors."""
    details = [
        ErrorDetail(
            field=" → ".join(str(loc) for loc in err.get("loc", [])),
            message=err.get("msg", "Invalid value"),
            code=err.get("type"),
        )
        for err in exc.errors()
    ]
    return _build_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code=ErrorCode.VALIDATION_ERROR,
        message="Request validation failed",
        details=details,
    )


async def unhandled_error_handler(
    _request: Request, exc: Exception
) -> JSONResponse:
    """Catch-all for unhandled exceptions.  Never leak internals."""
    logger.exception("unhandled_exception", exc_info=exc)
    return _build_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code=ErrorCode.INTERNAL_ERROR,
        message="An unexpected error occurred",
    )


def register_error_handlers(app: FastAPI) -> None:
    """Attach all exception handlers to the FastAPI app."""
    app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_error_handler)
