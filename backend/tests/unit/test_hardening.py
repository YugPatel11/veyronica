"""Unit tests for Phase 4 Hardening: Observability, Security, and Sandbox Tooling.

EPIC-23: Observability (Prometheus metrics, health aggregation).
EPIC-24: Security (Webhook HMAC signing, data retention, consent management).
EPIC-28: Sandbox tooling (reset guard, presenter mode).
"""

from datetime import UTC, datetime, timedelta
import pytest
from httpx import ASGITransport, AsyncClient

from app.core.consent import ConsentRecord, ConsentStatus, consent_manager
from app.core.retention import DEFAULT_POLICIES, retention_manager
from app.core.telemetry import metrics
from app.core.webhook_signer import sign_webhook_payload, verify_webhook_signature
from app.main import create_app


class TestObservability:
    """EPIC-23: Tests for metrics and health aggregation."""

    def test_prometheus_metrics_registry(self):
        metrics.increment_counter("nexus_workflow_runs_total", 1.0, {"slug": "exam-marks-processing", "status": "completed"})
        metrics.set_gauge("nexus_ledger_blocks_total", 42.0)

        rendered = metrics.render_prometheus_text()
        assert "nexus_workflow_runs_total" in rendered
        assert 'slug="exam-marks-processing"' in rendered
        assert "nexus_ledger_blocks_total 42.0" in rendered

    @pytest.mark.asyncio
    async def test_metrics_endpoint(self):
        app = create_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.get("/metrics")
            assert res.status_code == 200
            assert "text/plain" in res.headers["content-type"]
            assert "nexus_http_requests_total" in res.text

    @pytest.mark.asyncio
    async def test_aggregated_health_endpoint(self):
        app = create_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.get("/health/aggregated")
            assert res.status_code == 200
            data = res.json()
            assert "status" in data
            assert "connectors" in data
            assert "audit_ledger" in data
            assert data["api"] == "ok"


class TestSecurityHardening:
    """EPIC-24: Tests for webhook signing, retention, and consent."""

    def test_webhook_signing_and_verification(self):
        secret = "secret-key-12345"
        payload = {"event": "assignment.submitted", "student_id": "2024-CS-001"}

        sig, ts = sign_webhook_payload(secret, payload)
        assert len(sig) == 64  # SHA-256 hex length

        # Verification passes
        is_valid = verify_webhook_signature(secret, payload, sig, ts)
        assert is_valid is True

        # Fails with wrong secret
        assert verify_webhook_signature("wrong-key", payload, sig, ts) is False

        # Fails with tampered payload
        tampered = {"event": "assignment.submitted", "student_id": "2024-CS-999"}
        assert verify_webhook_signature(secret, tampered, sig, ts) is False

    def test_webhook_replay_window_rejection(self):
        secret = "secret-key-12345"
        payload = {"action": "sync"}
        old_timestamp = int((datetime.now(UTC) - timedelta(seconds=600)).timestamp())

        sig, ts = sign_webhook_payload(secret, payload, timestamp=old_timestamp)
        # Should be rejected because older than 300s
        assert verify_webhook_signature(secret, payload, sig, ts, max_drift_seconds=300) is False

    def test_retention_policy_immutable_audit(self):
        # Audit ledger must never be eligible for purge regardless of age
        two_years_ago = datetime.now(UTC) - timedelta(days=730)
        assert retention_manager.evaluate_item("audit_ledger", two_years_ago) is False

    def test_retention_policy_ephemeral_purge(self):
        twenty_days_ago = datetime.now(UTC) - timedelta(days=20)
        five_days_ago = datetime.now(UTC) - timedelta(days=5)

        # Ephemeral uploads policy is 14 days
        assert retention_manager.evaluate_item("ephemeral_uploads", twenty_days_ago) is True
        assert retention_manager.evaluate_item("ephemeral_uploads", five_days_ago) is False

    def test_student_consent_checks(self):
        record = consent_manager.get_consent("2024-CS-001")
        assert record.can_send_email() is True
        assert record.can_ai_evaluate() is True

        # Revoked SMS
        revoked_rec = consent_manager.get_consent("2024-CS-003")
        assert revoked_rec.can_send_sms() is False


class TestSandboxTooling:
    """EPIC-28: Tests for sandbox environment control."""

    @pytest.mark.asyncio
    async def test_sandbox_reset_in_dev(self):
        app = create_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post("/api/v1/sandbox/reset")
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "reset_completed"

    @pytest.mark.asyncio
    async def test_presenter_mode_toggle(self):
        app = create_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post(
                "/api/v1/sandbox/presenter-mode",
                json={"enabled": True, "hide_student_pii": True},
            )
            assert res.status_code == 200
            data = res.json()
            assert data["presenter_mode"] is True
            assert data["hide_student_pii"] is True
