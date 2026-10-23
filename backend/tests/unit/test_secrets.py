"""Tests for secrets validation module.

EPIC-04-T08: Verify secret validation catches weak defaults.
"""

from unittest.mock import patch

import pytest

from app.core.secrets_validation import SecretValidationError, validate_secrets


class TestSecretsValidation:
    """Test secrets validation."""

    def test_warns_on_weak_jwt_secret(self) -> None:
        warnings = validate_secrets(strict=False)
        # Default config has "CHANGE-ME" in jwt_secret_key
        assert any("JWT_SECRET_KEY" in w for w in warnings)

    def test_strict_mode_raises(self) -> None:
        with pytest.raises(SecretValidationError):
            validate_secrets(strict=True)

    def test_short_secret_warned(self) -> None:
        with patch(
            "app.core.secrets_validation.get_settings"
        ) as mock_settings:
            mock_settings.return_value.jwt_secret_key = "short"
            mock_settings.return_value.is_production = False
            mock_settings.return_value.is_development = True
            mock_settings.return_value.database_url = "postgresql://x"
            mock_settings.return_value.s3_access_key = "safe_key"
            mock_settings.return_value.sentry_dsn = "https://sentry"

            warnings = validate_secrets(strict=False)
            assert any("32 characters" in w for w in warnings)
