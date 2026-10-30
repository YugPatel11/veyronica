"""Security Incident Response Engine (WF4).

EPIC-18-T01: Rule engine: failed login detection (N in M minutes).
EPIC-18-T02: Rule engine: unusual login detection.
EPIC-18-T03: Rule engine: suspicious operations detection.
EPIC-18-T04: Rule engine: traffic anomaly / rate limiting.
EPIC-18-T05: Security Agent: context gathering + incident summary.
EPIC-18-T06: Automated temporary responses (lockout, IP block).
EPIC-18-T07: Admin notification (email + Telegram + dashboard).
"""

from app.security_engine.actions import (
    BlockRecord,
    SecurityActionHandler,
    action_handler,
)
from app.security_engine.agent import (
    SecurityAgent,
    SecurityIncident,
    ThreatContext,
)
from app.security_engine.failed_logins import (
    FailedLoginDetector,
    LoginAttemptData,
    SecurityAlert,
)
from app.security_engine.notifier import (
    IncidentNotification,
    SecurityNotifier,
    security_notifier,
)
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

__all__ = [
    "AuditOperation",
    "BlockRecord",
    "FailedLoginDetector",
    "GeoLocation",
    "IncidentNotification",
    "LoginAttemptData",
    "LoginEvent",
    "RequestMetric",
    "SecurityActionHandler",
    "SecurityAgent",
    "SecurityAlert",
    "SecurityIncident",
    "SecurityNotifier",
    "SuspiciousOpsDetector",
    "ThreatContext",
    "TrafficAnomalyDetector",
    "UnusualLoginDetector",
    "UserLoginContext",
    "action_handler",
    "security_notifier",
]
