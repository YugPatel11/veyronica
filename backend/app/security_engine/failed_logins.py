"""Failed login detection rule engine.

EPIC-18-T01: Rule engine: failed login detection (N in M minutes).
Flags brute-force attacks and credential stuffing.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any
import uuid


@dataclass
class LoginAttemptData:
    """Record of a single login attempt."""
    email: str
    source_ip: str
    success: bool
    user_agent: str = ""
    attempted_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    failure_reason: str | None = None


@dataclass
class SecurityAlert:
    """Alert raised by the security detection rules."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    rule_name: str = "failed_logins"
    severity: str = "warning"  # info, warning, critical
    title: str = ""
    description: str = ""
    target_type: str = "ip"  # ip, user, endpoint
    target_value: str = ""
    source_ip: str | None = None
    user_id: str | None = None
    count: int = 0
    window_seconds: int = 300
    detected_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)


class FailedLoginDetector:
    """EPIC-18-T01: Detects brute-force and credential stuffing login attempts."""

    def __init__(self, default_threshold: int = 5, default_window_seconds: int = 300):
        self.default_threshold = default_threshold
        self.default_window_seconds = default_window_seconds

    def evaluate(
        self,
        attempts: list[LoginAttemptData],
        threshold: int | None = None,
        window_seconds: int | None = None,
    ) -> list[SecurityAlert]:
        """Analyze a sequence of login attempts and identify threshold breaches."""
        thresh = threshold or self.default_threshold
        window = window_seconds or self.default_window_seconds
        alerts: list[SecurityAlert] = []

        if not attempts:
            return alerts

        # Sort attempts by timestamp
        sorted_attempts = sorted(attempts, key=lambda a: a.attempted_at)
        now = sorted_attempts[-1].attempted_at
        cutoff = now - timedelta(seconds=window)

        # 1. Check by Email (Targeted Brute-Force)
        by_email: dict[str, list[LoginAttemptData]] = defaultdict(list)
        for att in sorted_attempts:
            if not att.success and att.attempted_at >= cutoff:
                by_email[att.email.lower()].append(att)

        for email, failures in by_email.items():
            if len(failures) >= thresh:
                sources = list({f.source_ip for f in failures})
                severity = "critical" if len(failures) >= thresh * 2 else "warning"
                alerts.append(
                    SecurityAlert(
                        rule_name="failed_logins_per_user",
                        severity=severity,
                        title=f"Brute force detected for {email}",
                        description=f"{len(failures)} failed logins in {window // 60}m for account {email}",
                        target_type="user",
                        target_value=email,
                        source_ip=sources[0] if len(sources) == 1 else None,
                        count=len(failures),
                        window_seconds=window,
                        metadata={
                            "email": email,
                            "unique_ips": sources,
                            "attack_type": "targeted_brute_force" if len(sources) == 1 else "distributed_brute_force",
                        },
                    )
                )

        # 2. Check by Source IP (Credential Stuffing / IP Spraying)
        by_ip: dict[str, list[LoginAttemptData]] = defaultdict(list)
        for att in sorted_attempts:
            if not att.success and att.attempted_at >= cutoff:
                by_ip[att.source_ip].append(att)

        for ip, failures in by_ip.items():
            if len(failures) >= thresh:
                target_emails = list({f.email.lower() for f in failures})
                severity = "critical" if len(failures) >= thresh * 2 or len(target_emails) >= 3 else "warning"
                attack_type = "credential_stuffing" if len(target_emails) > 1 else "brute_force"
                alerts.append(
                    SecurityAlert(
                        rule_name="failed_logins_per_ip",
                        severity=severity,
                        title=f"Suspicious failed login burst from {ip}",
                        description=f"{len(failures)} failed attempts from IP {ip} targeting {len(target_emails)} account(s)",
                        target_type="ip",
                        target_value=ip,
                        source_ip=ip,
                        count=len(failures),
                        window_seconds=window,
                        metadata={
                            "source_ip": ip,
                            "targeted_accounts": target_emails,
                            "attack_type": attack_type,
                        },
                    )
                )

        return alerts
