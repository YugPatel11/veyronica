"""Unusual login detection rule engine.

EPIC-18-T02: Rule engine: unusual login detection.
Detects impossible travel, new IP/device signatures, off-hours access, and suspicious user-agents.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
import uuid

from app.security_engine.failed_logins import SecurityAlert


@dataclass
class GeoLocation:
    """Geographic coordinates and metadata."""
    city: str = ""
    country: str = ""
    latitude: float = 0.0
    longitude: float = 0.0


@dataclass
class UserLoginContext:
    """Historical context for a user to evaluate unusual login attempts."""
    user_id: str
    email: str
    role: str = "faculty"
    known_ips: set[str] = field(default_factory=set)
    known_devices: set[str] = field(default_factory=set)
    last_login_at: datetime | None = None
    last_login_ip: str | None = None
    last_location: GeoLocation | None = None
    typical_hours: tuple[int, int] = (6, 22)  # 6 AM to 10 PM typical


@dataclass
class LoginEvent:
    """Incoming login event to evaluate."""
    user_id: str
    email: str
    source_ip: str
    user_agent: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    location: GeoLocation | None = None
    is_admin: bool = False


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate Great Circle distance in km between two lat/long points."""
    r = 6371.0  # Earth's radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


class UnusualLoginDetector:
    """EPIC-18-T02: Detects anomalies in successful or attempted user logins."""

    SUSPICIOUS_AGENTS = [
        "sqlmap",
        "nikto",
        "nmap",
        "python-requests",
        "curl/",
        "postmanruntime",
        "masscan",
        "headlesschrome",
    ]

    def evaluate(
        self,
        event: LoginEvent,
        user_context: UserLoginContext | None = None,
    ) -> list[SecurityAlert]:
        """Evaluate a login event against baseline patterns."""
        alerts: list[SecurityAlert] = []

        # 1. Suspicious User-Agent / Tool Header Detection
        ua_lower = (event.user_agent or "").lower()
        for pattern in self.SUSPICIOUS_AGENTS:
            if pattern in ua_lower:
                alerts.append(
                    SecurityAlert(
                        rule_name="suspicious_user_agent",
                        severity="warning",
                        title=f"Suspicious client tool: {pattern}",
                        description=f"Login attempt using automated client/scanner: {event.user_agent}",
                        target_type="ip",
                        target_value=event.source_ip,
                        source_ip=event.source_ip,
                        user_id=event.user_id,
                        metadata={
                            "matched_pattern": pattern,
                            "user_agent": event.user_agent,
                            "email": event.email,
                        },
                    )
                )
                break

        if not user_context:
            return alerts

        # 2. Impossible Travel Detection
        if (
            user_context.last_login_at
            and user_context.last_location
            and event.location
            and (event.location.latitude != 0.0 or event.location.longitude != 0.0)
            and (user_context.last_location.latitude != 0.0 or user_context.last_location.longitude != 0.0)
        ):
            time_delta_hours = max(
                (event.timestamp - user_context.last_login_at).total_seconds() / 3600.0,
                0.001,
            )
            dist_km = _haversine_km(
                user_context.last_location.latitude,
                user_context.last_location.longitude,
                event.location.latitude,
                event.location.longitude,
            )

            # Speed requirement > 850 km/h (faster than commercial jetliner) indicates impossible travel
            speed = dist_km / time_delta_hours
            if dist_km > 300 and speed > 850:
                alerts.append(
                    SecurityAlert(
                        rule_name="impossible_travel",
                        severity="critical",
                        title=f"Impossible travel detected for {event.email}",
                        description=(
                            f"Account logged in from {event.location.city or 'Loc2'} "
                            f"{dist_km:.0f}km away from {user_context.last_location.city or 'Loc1'} "
                            f"in {time_delta_hours * 60:.1f} minutes ({speed:.0f} km/h required)"
                        ),
                        target_type="user",
                        target_value=event.email,
                        source_ip=event.source_ip,
                        user_id=event.user_id,
                        metadata={
                            "distance_km": round(dist_km, 1),
                            "hours_elapsed": round(time_delta_hours, 3),
                            "speed_kmh": round(speed, 1),
                            "previous_ip": user_context.last_login_ip,
                            "current_ip": event.source_ip,
                        },
                    )
                )

        # 3. New IP for Privileged Role
        is_privileged = event.is_admin or user_context.role in {"admin", "superadmin", "security_officer"}
        if is_privileged and user_context.known_ips and event.source_ip not in user_context.known_ips:
            alerts.append(
                SecurityAlert(
                    rule_name="privileged_login_new_ip",
                    severity="warning",
                    title=f"Privileged login from new IP: {event.email}",
                    description=f"Admin {event.email} authenticated from previously unseen IP {event.source_ip}",
                    target_type="user",
                    target_value=event.email,
                    source_ip=event.source_ip,
                    user_id=event.user_id,
                    metadata={
                        "user_role": user_context.role,
                        "new_ip": event.source_ip,
                        "known_ips_count": len(user_context.known_ips),
                    },
                )
            )

        # 4. Off-Hours Login for Privileged Accounts
        if is_privileged:
            login_hour = event.timestamp.hour
            start_hour, end_hour = user_context.typical_hours
            if login_hour < start_hour or login_hour > end_hour:
                alerts.append(
                    SecurityAlert(
                        rule_name="off_hours_admin_login",
                        severity="info",
                        title=f"Off-hours admin activity: {event.email}",
                        description=f"Admin {event.email} accessed system at {login_hour:02d}:00 UTC (typical: {start_hour:02d}:00-{end_hour:02d}:00)",
                        target_type="user",
                        target_value=event.email,
                        source_ip=event.source_ip,
                        user_id=event.user_id,
                        metadata={"hour_utc": login_hour},
                    )
                )

        return alerts
