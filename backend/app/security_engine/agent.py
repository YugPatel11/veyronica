"""Security incident triage and response agent.

EPIC-18-T05: Security Agent: context gathering + incident summary.
Aggregates alert signals, gathers threat context, executes automated containment,
appends tamper-evident audit records, and alerts system administrators.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
import uuid

import structlog

from app.audit import ledger
from app.security_engine.actions import action_handler
from app.security_engine.failed_logins import FailedLoginDetector, LoginAttemptData, SecurityAlert
from app.security_engine.notifier import security_notifier
from app.security_engine.suspicious_ops import AuditOperation, SuspiciousOpsDetector
from app.security_engine.traffic_anomaly import RequestMetric, TrafficAnomalyDetector
from app.security_engine.unusual_logins import LoginEvent, UnusualLoginDetector, UserLoginContext

logger = structlog.get_logger()


@dataclass
class ThreatContext:
    """Enriched context surrounding a security event."""
    user_id: str | None = None
    email: str | None = None
    role: str | None = None
    source_ip: str | None = None
    is_ip_previously_blocked: bool = False
    prior_alert_count: int = 0
    account_locked: bool = False


@dataclass
class SecurityIncident:
    """Consolidated security incident."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    severity: str = "warning"  # info, warning, critical
    title: str = ""
    summary: str = ""
    target_user: str | None = None
    source_ip: str | None = None
    alerts: list[SecurityAlert] = field(default_factory=list)
    actions_taken: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    ledger_hash: str | None = None


class SecurityAgent:
    """EPIC-18-T05: Intelligent autonomous security agent for threat triage and containment."""

    def __init__(
        self,
        auto_contain_critical: bool = True,
        auto_lockout_users: bool = True,
    ) -> None:
        self.auto_contain_critical = auto_contain_critical
        self.auto_lockout_users = auto_lockout_users
        self.failed_login_detector = FailedLoginDetector()
        self.unusual_login_detector = UnusualLoginDetector()
        self.suspicious_ops_detector = SuspiciousOpsDetector()
        self.traffic_anomaly_detector = TrafficAnomalyDetector()
        self._incidents: list[SecurityIncident] = []

    def gather_context(
        self,
        target_user: str | None = None,
        source_ip: str | None = None,
        user_context: UserLoginContext | None = None,
    ) -> ThreatContext:
        """Enrich incident with user identity, roles, and past security record."""
        is_ip_blocked = False
        if source_ip:
            is_ip_blocked = action_handler.is_blocked("ip", source_ip)

        is_user_locked = False
        if target_user:
            is_user_locked = action_handler.is_blocked("user", target_user)

        prior_alerts = sum(
            1 for inc in self._incidents
            if (target_user and inc.target_user == target_user) or (source_ip and inc.source_ip == source_ip)
        )

        return ThreatContext(
            user_id=user_context.user_id if user_context else None,
            email=target_user or (user_context.email if user_context else None),
            role=user_context.role if user_context else None,
            source_ip=source_ip,
            is_ip_previously_blocked=is_ip_blocked,
            prior_alert_count=prior_alerts,
            account_locked=is_user_locked,
        )

    async def triage_and_remediate(
        self,
        alerts: list[SecurityAlert],
        user_context: UserLoginContext | None = None,
    ) -> SecurityIncident | None:
        """Process triggered alerts, form an incident report, and execute containment."""
        if not alerts:
            return None

        # Determine overall severity
        has_critical = any(a.severity == "critical" for a in alerts)
        has_warning = any(a.severity == "warning" for a in alerts)
        severity = "critical" if has_critical else ("warning" if has_warning else "info")

        # Extract primary identifiers
        primary_alert = alerts[0]
        source_ip = next((a.source_ip for a in alerts if a.source_ip), None)
        target_user = next((a.target_value for a in alerts if a.target_type == "user"), None)

        threat_ctx = self.gather_context(target_user, source_ip, user_context)

        # Elevate to critical if multiple prior alerts exist or privileged target
        if threat_ctx.prior_alert_count >= 2 and severity == "warning":
            severity = "critical"

        # Build incident narrative
        rule_names = ", ".join({a.rule_name for a in alerts})
        title = f"[{severity.upper()}] Security Incident: {primary_alert.title}"
        summary = (
            f"Detected {len(alerts)} alert signal(s) ({rule_names}). "
            f"Source IP: {source_ip or 'unknown'}, Target: {target_user or 'system'}. "
            f"Prior alerts on record: {threat_ctx.prior_alert_count}."
        )

        actions_taken: list[str] = []
        recommendations: list[str] = []

        # Execute automated containment for critical threats
        if severity == "critical" and self.auto_contain_critical:
            if source_ip and not threat_ctx.is_ip_previously_blocked:
                action_handler.block_ip(
                    ip_address=source_ip,
                    reason=f"Automated block due to critical incident: {title}",
                    duration_minutes=60,
                )
                actions_taken.append(f"Blocked IP {source_ip} for 60 minutes")

            if target_user and self.auto_lockout_users and not threat_ctx.account_locked:
                action_handler.lock_account(
                    user_id_or_email=target_user,
                    reason=f"Automated lockout following threat detection: {title}",
                    duration_minutes=30,
                )
                actions_taken.append(f"Locked account {target_user} for 30 minutes")
        else:
            recommendations.append("Review suspicious IP activity in Mission Control")
            recommendations.append("Verify user session validity with two-factor authentication")

        action_summary_str = "; ".join(actions_taken) if actions_taken else "No automated action taken (monitoring)"

        # Notify administrators across all channels
        try:
            await security_notifier.notify_admins(
                alert=primary_alert,
                action_taken=action_summary_str,
            )
        except Exception as e:
            logger.error("admin_notification_error", error=str(e))

        # Append audit entry to Hash-Chained Decision Ledger
        entry = ledger.append(
            event_type="security_incident",
            action="containment_and_triage",
            entity_type="security_alert",
            entity_id=primary_alert.id,
            reasoning=summary,
            confidence=0.98 if severity == "critical" else 0.85,
            payload={
                "incident_severity": severity,
                "rules_triggered": [a.rule_name for a in alerts],
                "source_ip": source_ip,
                "target_user": target_user,
                "actions_taken": actions_taken,
                "recommendations": recommendations,
            },
        )

        incident = SecurityIncident(
            severity=severity,
            title=title,
            summary=summary,
            target_user=target_user,
            source_ip=source_ip,
            alerts=alerts,
            actions_taken=actions_taken,
            recommendations=recommendations,
            ledger_hash=entry.entry_hash,
        )
        self._incidents.append(incident)

        logger.info(
            "security_incident_processed",
            incident_id=incident.id,
            severity=severity,
            actions_count=len(actions_taken),
            ledger_seq=entry.sequence_number,
        )
        return incident

    def get_incidents(self, limit: int = 20) -> list[SecurityIncident]:
        """Retrieve recent security incidents."""
        return self._incidents[-limit:]
