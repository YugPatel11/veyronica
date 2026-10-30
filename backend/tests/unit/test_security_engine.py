"""Unit tests for WF4 Security Incident Response Engine.

Covers EPIC-18-T01 to EPIC-18-T07:
- Failed login detection (EPIC-18-T01)
- Unusual login detection (EPIC-18-T02)
- Suspicious operations detection (EPIC-18-T03)
- Traffic anomaly & rate limiting (EPIC-18-T04)
- Security Agent context & triage (EPIC-18-T05)
- Automated responses (lockout, IP block) (EPIC-18-T06)
- Admin notification routing (EPIC-18-T07)
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
import pytest

from app.audit import ledger
from app.notifications import dispatcher
from app.security_engine.actions import SecurityActionHandler
from app.security_engine.agent import SecurityAgent
from app.security_engine.failed_logins import (
    FailedLoginDetector,
    LoginAttemptData,
    SecurityAlert,
)
from app.security_engine.notifier import SecurityNotifier
from app.security_engine.suspicious_ops import (
    AuditOperation,
    SuspiciousOpsDetector,
)
from app.security_engine.traffic_anomaly import (
    RequestMetric,
    TrafficAnomalyDetector,
)
from app.security_engine.unusual_logins import (
    GeoLocation,
    LoginEvent,
    UnusualLoginDetector,
    UserLoginContext,
)


# ── EPIC-18-T01: Failed Login Detector Tests ─────────────────────────────────

def test_failed_login_detection_under_threshold() -> None:
    detector = FailedLoginDetector(default_threshold=5, default_window_seconds=300)
    now = datetime.now(UTC)

    # 3 failures (below threshold 5)
    attempts = [
        LoginAttemptData(email="user@uni.edu", source_ip="192.168.1.10", success=False, attempted_at=now - timedelta(seconds=60)),
        LoginAttemptData(email="user@uni.edu", source_ip="192.168.1.10", success=False, attempted_at=now - timedelta(seconds=30)),
        LoginAttemptData(email="user@uni.edu", source_ip="192.168.1.10", success=False, attempted_at=now),
    ]

    alerts = detector.evaluate(attempts)
    assert len(alerts) == 0


def test_failed_login_detection_brute_force_and_stuffing() -> None:
    detector = FailedLoginDetector(default_threshold=5, default_window_seconds=300)
    now = datetime.now(UTC)

    # 6 failures on single email from single IP
    brute_force_attempts = [
        LoginAttemptData(email="target@uni.edu", source_ip="10.0.0.5", success=False, attempted_at=now - timedelta(seconds=i * 20))
        for i in range(6)
    ]

    alerts = detector.evaluate(brute_force_attempts)
    assert len(alerts) >= 1
    user_alert = next((a for a in alerts if a.rule_name == "failed_logins_per_user"), None)
    assert user_alert is not None
    assert user_alert.target_value == "target@uni.edu"
    assert user_alert.count == 6

    # Credential stuffing: 5 different emails from 1 IP
    stuffing_attempts = [
        LoginAttemptData(email=f"user_{i}@uni.edu", source_ip="198.51.100.99", success=False, attempted_at=now - timedelta(seconds=i * 10))
        for i in range(5)
    ]
    alerts_stuffing = detector.evaluate(stuffing_attempts)
    ip_alert = next((a for a in alerts_stuffing if a.rule_name == "failed_logins_per_ip"), None)
    assert ip_alert is not None
    assert ip_alert.metadata["attack_type"] == "credential_stuffing"
    assert len(ip_alert.metadata["targeted_accounts"]) == 5


# ── EPIC-18-T02: Unusual Login Detector Tests ─────────────────────────────────

def test_unusual_login_suspicious_user_agent() -> None:
    detector = UnusualLoginDetector()
    event = LoginEvent(
        user_id="usr_123",
        email="student@uni.edu",
        source_ip="203.0.113.1",
        user_agent="sqlmap/1.6.4#stable",
    )
    alerts = detector.evaluate(event)
    assert len(alerts) == 1
    assert alerts[0].rule_name == "suspicious_user_agent"
    assert alerts[0].severity == "warning"


def test_unusual_login_impossible_travel() -> None:
    detector = UnusualLoginDetector()
    now = datetime.now(UTC)

    # First login from New York, then login from London 30 minutes later (impossible speed > 850 km/h)
    ny_loc = GeoLocation(city="New York", country="US", latitude=40.7128, longitude=-74.0060)
    london_loc = GeoLocation(city="London", country="GB", latitude=51.5074, longitude=-0.1278)

    context = UserLoginContext(
        user_id="usr_456",
        email="prof@uni.edu",
        last_login_at=now - timedelta(minutes=30),
        last_login_ip="198.51.100.1",
        last_location=ny_loc,
    )

    event = LoginEvent(
        user_id="usr_456",
        email="prof@uni.edu",
        source_ip="198.51.100.50",
        user_agent="Mozilla/5.0",
        timestamp=now,
        location=london_loc,
    )

    alerts = detector.evaluate(event, context)
    assert any(a.rule_name == "impossible_travel" and a.severity == "critical" for a in alerts)


def test_unusual_login_privileged_new_ip_and_off_hours() -> None:
    detector = UnusualLoginDetector()
    now = datetime(2026, 10, 30, 3, 15, tzinfo=UTC)  # 3:15 AM UTC

    context = UserLoginContext(
        user_id="admin_01",
        email="sysadmin@uni.edu",
        role="admin",
        known_ips={"10.10.1.1", "10.10.1.2"},
        typical_hours=(8, 18),
    )

    event = LoginEvent(
        user_id="admin_01",
        email="sysadmin@uni.edu",
        source_ip="203.0.113.88",  # Brand new unknown IP
        user_agent="Mozilla/5.0 Chrome/120.0",
        timestamp=now,
        is_admin=True,
    )

    alerts = detector.evaluate(event, context)
    rule_names = {a.rule_name for a in alerts}
    assert "privileged_login_new_ip" in rule_names
    assert "off_hours_admin_login" in rule_names


# ── EPIC-18-T03: Suspicious Operations Tests ─────────────────────────────────

def test_suspicious_ops_mass_export_and_probing() -> None:
    detector = SuspiciousOpsDetector(
        export_threshold_records=500,
        forbidden_probe_threshold=5,
        window_seconds=300,
    )
    now = datetime.now(UTC)

    # 1. Mass export of 1200 records
    mass_export = AuditOperation(
        action="export_students",
        user_id="u1",
        user_email="auditor@uni.edu",
        source_ip="192.168.1.50",
        record_count=1200,
        timestamp=now,
    )
    alerts = detector.evaluate([mass_export])
    assert any(a.rule_name == "mass_data_export" and a.severity == "critical" for a in alerts)

    # 2. 403 Probe burst (6 unauthorized attempts)
    probes = [
        AuditOperation(
            action="access_endpoint",
            user_id="u2",
            user_email="intruder@uni.edu",
            source_ip="10.5.5.5",
            status_code=403,
            resource=f"/api/v1/admin/secret_{i}",
            timestamp=now - timedelta(seconds=i * 10),
        )
        for i in range(6)
    ]
    probe_alerts = detector.evaluate(probes)
    assert any(a.rule_name == "authorization_probing" for a in probe_alerts)


# ── EPIC-18-T04: Traffic Anomaly Detector Tests ──────────────────────────────

def test_traffic_anomaly_volume_and_error_rate() -> None:
    detector = TrafficAnomalyDetector(
        rate_limit_per_minute=100,
        error_rate_threshold=0.40,
        min_requests_for_error_check=20,
        window_seconds=60,
    )
    now = datetime.now(UTC)

    # 120 requests from single IP in 60 seconds (spike)
    spike_metrics = [
        RequestMetric(source_ip="10.20.30.40", timestamp=now - timedelta(seconds=i * 0.4))
        for i in range(120)
    ]
    alerts = detector.evaluate(spike_metrics)
    assert any(a.rule_name == "traffic_volume_spike" for a in alerts)

    # 25 requests with 15 errors (60% error rate > 40%)
    error_metrics = [
        RequestMetric(
            source_ip="10.99.99.99",
            status_code=500 if i < 15 else 200,
            timestamp=now - timedelta(seconds=i * 1.5),
        )
        for i in range(25)
    ]
    error_alerts = detector.evaluate(error_metrics)
    assert any(a.rule_name == "high_error_rate_surge" for a in error_alerts)


# ── EPIC-18-T06: Automated Responses (Actions) Tests ─────────────────────────

@pytest.mark.anyio
async def test_security_action_handler_lockout_and_block() -> None:
    handler = SecurityActionHandler()

    # Lock account
    lock_rec = handler.lock_account(
        user_id_or_email="compromised@uni.edu",
        reason="Repeated brute force password attacks",
        duration_minutes=15,
    )
    assert lock_rec.is_active is True
    assert handler.is_blocked("user", "compromised@uni.edu") is True

    # Block IP
    ip_rec = handler.block_ip(
        ip_address="198.51.100.222",
        reason="Malicious port scan & fuzzing",
        duration_minutes=60,
    )
    assert ip_rec.is_active is True
    assert handler.is_blocked("ip", "198.51.100.222") is True

    # Active blocks query
    active = handler.list_active_blocks()
    assert len(active) >= 2

    # Unblock test
    unblocked = handler.unblock("ip", "198.51.100.222")
    assert unblocked is True
    assert handler.is_blocked("ip", "198.51.100.222") is False


# ── EPIC-18-T07: Admin Notifications Tests ────────────────────────────────────

@pytest.mark.anyio
async def test_security_notifier_multi_channel_routing() -> None:
    notifier = SecurityNotifier(admin_user_ids=["admin_sec", "admin_ops"])
    alert = SecurityAlert(
        rule_name="impossible_travel",
        severity="critical",
        title="Impossible travel detected",
        description="User logged in from Tokyo and Toronto within 10 minutes",
        target_type="user",
        target_value="vip@uni.edu",
        source_ip="203.0.113.10",
    )

    sent = await notifier.notify_admins(alert, action_taken="Blocked IP 203.0.113.10")
    assert len(sent) > 0
    assert any(n.channel in {"in_app", "email"} for n in sent)
    assert len(notifier.notification_log) > 0


# ── EPIC-18-T05: End-to-End Security Agent Workflow Tests ────────────────────

@pytest.mark.anyio
async def test_security_agent_triage_containment_and_ledger() -> None:
    agent = SecurityAgent(auto_contain_critical=True, auto_lockout_users=True)

    critical_alert = SecurityAlert(
        rule_name="mass_data_export",
        severity="critical",
        title="Data exfiltration attempt",
        description="Attempted export of entire student grades ledger",
        target_type="user",
        target_value="rogue_user@uni.edu",
        source_ip="198.51.100.77",
        count=2500,
    )

    incident = await agent.triage_and_remediate([critical_alert])
    assert incident is not None
    assert incident.severity == "critical"
    assert len(incident.actions_taken) >= 1
    assert "Blocked IP 198.51.100.77" in incident.actions_taken[0]
    assert incident.ledger_hash is not None

    # Verify decision ledger hash-chain integrity
    is_valid, last_seq = ledger.verify_chain()
    assert is_valid is True
    assert last_seq >= 1
