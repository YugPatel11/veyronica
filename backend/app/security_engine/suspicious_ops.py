"""Suspicious operations detection rule engine.

EPIC-18-T03: Rule engine: suspicious operations detection.
Detects mass data export, privilege escalation, authorization probing (403 bursts), and sensitive key access.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

from app.security_engine.failed_logins import SecurityAlert


@dataclass
class AuditOperation:
    """An operation or event recorded in the audit/access log."""
    action: str  # export_students, change_role, get_credentials, read_resource, etc.
    user_id: str
    user_email: str
    source_ip: str
    status_code: int = 200
    resource: str = ""
    record_count: int = 1
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    details: dict[str, Any] = field(default_factory=dict)


class SuspiciousOpsDetector:
    """EPIC-18-T03: Evaluates operations to detect exfiltration, probing, and privilege escalation."""

    def __init__(
        self,
        export_threshold_records: int = 500,
        export_burst_count: int = 3,
        forbidden_probe_threshold: int = 8,
        window_seconds: int = 300,
    ):
        self.export_threshold_records = export_threshold_records
        self.export_burst_count = export_burst_count
        self.forbidden_probe_threshold = forbidden_probe_threshold
        self.window_seconds = window_seconds

    def evaluate(self, operations: list[AuditOperation]) -> list[SecurityAlert]:
        """Evaluate a window of audit operations."""
        alerts: list[SecurityAlert] = []
        if not operations:
            return alerts

        sorted_ops = sorted(operations, key=lambda o: o.timestamp)
        now = sorted_ops[-1].timestamp
        cutoff = now - timedelta(seconds=self.window_seconds)
        recent_ops = [op for op in sorted_ops if op.timestamp >= cutoff]

        # 1. Mass Data Export / Exfiltration Detection
        user_exports: dict[str, list[AuditOperation]] = defaultdict(list)
        for op in recent_ops:
            if "export" in op.action.lower() or "download_bulk" in op.action.lower():
                user_exports[op.user_email].append(op)
                # Single massive export check
                if op.record_count >= self.export_threshold_records:
                    alerts.append(
                        SecurityAlert(
                            rule_name="mass_data_export",
                            severity="critical",
                            title=f"Mass data export by {op.user_email}",
                            description=f"User exported {op.record_count} records in action '{op.action}' from IP {op.source_ip}",
                            target_type="user",
                            target_value=op.user_email,
                            source_ip=op.source_ip,
                            user_id=op.user_id,
                            count=op.record_count,
                            metadata={
                                "action": op.action,
                                "resource": op.resource,
                                "records": op.record_count,
                            },
                        )
                    )

        # Repeated export burst check
        for email, exports in user_exports.items():
            if len(exports) >= self.export_burst_count:
                total_records = sum(e.record_count for e in exports)
                alerts.append(
                    SecurityAlert(
                        rule_name="export_burst_detected",
                        severity="warning",
                        title=f"Rapid export burst by {email}",
                        description=f"User triggered {len(exports)} export operations ({total_records} total records) within {self.window_seconds // 60}m",
                        target_type="user",
                        target_value=email,
                        source_ip=exports[0].source_ip,
                        user_id=exports[0].user_id,
                        count=len(exports),
                        metadata={"total_records": total_records, "burst_count": len(exports)},
                    )
                )

        # 2. Authorization Probing / 403 Burst Detection
        forbidden_by_ip: dict[str, list[AuditOperation]] = defaultdict(list)
        forbidden_by_user: dict[str, list[AuditOperation]] = defaultdict(list)
        for op in recent_ops:
            if op.status_code == 403:
                forbidden_by_ip[op.source_ip].append(op)
                if op.user_email:
                    forbidden_by_user[op.user_email].append(op)

        for ip, probes in forbidden_by_ip.items():
            if len(probes) >= self.forbidden_probe_threshold:
                endpoints = list({p.resource for p in probes if p.resource})
                alerts.append(
                    SecurityAlert(
                        rule_name="authorization_probing",
                        severity="critical",
                        title=f"Permission probing detected from {ip}",
                        description=f"{len(probes)} unauthorized (403) requests across {len(endpoints)} endpoint(s) within {self.window_seconds // 60}m",
                        target_type="ip",
                        target_value=ip,
                        source_ip=ip,
                        count=len(probes),
                        metadata={"probed_resources": endpoints[:10], "attempt_count": len(probes)},
                    )
                )

        # 3. Privilege Escalation / Sensitive Role Changes
        for op in recent_ops:
            action_lower = op.action.lower()
            if "role_change" in action_lower or "grant_role" in action_lower or "promote" in action_lower:
                granted_role = op.details.get("role", "").lower()
                if granted_role in {"admin", "superadmin", "system_admin"}:
                    alerts.append(
                        SecurityAlert(
                            rule_name="privilege_escalation",
                            severity="warning",
                            title=f"Privilege escalation to {granted_role}",
                            description=f"User {op.user_email} granted {granted_role} role to target {op.details.get('target_user', 'unknown')}",
                            target_type="user",
                            target_value=op.user_email,
                            source_ip=op.source_ip,
                            user_id=op.user_id,
                            metadata=op.details,
                        )
                    )

            # 4. Sensitive Key / Secret Access Probing
            if "secret" in action_lower or "key_access" in action_lower or "credential_read" in action_lower:
                if not op.details.get("authorized", True):
                    alerts.append(
                        SecurityAlert(
                            rule_name="secret_access_attempt",
                            severity="critical",
                            title=f"Unauthorized secrets access attempt by {op.user_email}",
                            description=f"Blocked attempt to access secret '{op.resource}' from IP {op.source_ip}",
                            target_type="user",
                            target_value=op.user_email,
                            source_ip=op.source_ip,
                            user_id=op.user_id,
                            metadata={"resource": op.resource, "action": op.action},
                        )
                    )

        return alerts
