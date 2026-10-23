"""Tests for input validation middleware.

EPIC-04-T10: Verify size limits and content-type enforcement.
"""

import pytest

from app.core.input_validation import (
    ALLOWED_CONTENT_TYPES,
    MAX_BODY_SIZE,
    InputValidationMiddleware,
)


class TestInputValidationConstants:
    """Test input validation configuration."""

    def test_max_body_size_is_10mb(self) -> None:
        assert MAX_BODY_SIZE == 10 * 1024 * 1024

    def test_json_is_allowed(self) -> None:
        assert "application/json" in ALLOWED_CONTENT_TYPES

    def test_multipart_is_allowed(self) -> None:
        assert "multipart/form-data" in ALLOWED_CONTENT_TYPES

    def test_form_urlencoded_is_allowed(self) -> None:
        assert "application/x-www-form-urlencoded" in ALLOWED_CONTENT_TYPES

    def test_octet_stream_is_allowed(self) -> None:
        assert "application/octet-stream" in ALLOWED_CONTENT_TYPES


class TestInputValidationMiddleware:
    """Test InputValidationMiddleware setup."""

    def test_skip_paths_includes_health(self) -> None:
        assert "/health" in InputValidationMiddleware.SKIP_PATHS
        assert "/ready" in InputValidationMiddleware.SKIP_PATHS
