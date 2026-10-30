"""Traffic anomaly and rate limiting detection rule engine.

EPIC-18-T04: Rule engine: traffic anomaly / rate limiting.
Detects sudden request volume spikes, error rate surges, and brute-force scraping patterns.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

from app.security_engine.failed_logins import SecurityAlert


@dataclass
class RequestMetric:
    """Telemetry record for an HTTP request."""
    source_ip: str
    user_id: str | None = None
    path: str = "/"
    status_code: int = 200
    response_time_ms: float = 20.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


class TrafficAnomalyDetector:
    """EPIC-18-T04: Identifies abnormal traffic patterns and rate violations."""

    def __init__(
        self,
        rate_limit_per_minute: int = 120,
        error_rate_threshold: float = 0.40,
        min_requests_for_error_check: int = 20,
        window_seconds: int = 60,
    ):
        self.rate_limit_per_minute = rate_limit_per_minute
        self.error_rate_threshold = error_rate_threshold
        self.min_requests_for_error_check = min_requests_for_error_check
        self.window_seconds = window_seconds

    def evaluate(self, metrics: list[RequestMetric]) -> list[SecurityAlert]:
        """Analyze request stream for volumetric spikes and error surges."""
        alerts: list[SecurityAlert] = []
        if not metrics:
            return alerts

        sorted_metrics = sorted(metrics, key=lambda m: m.timestamp)
        now = sorted_metrics[-1].timestamp
        cutoff = now - timedelta(seconds=self.window_seconds)
        recent_metrics = [m for m in sorted_metrics if m.timestamp >= cutoff]

        by_ip: dict[str, list[RequestMetric]] = defaultdict(list)
        for m in recent_metrics:
            by_ip[m.source_ip].append(m)

        for ip, reqs in by_ip.items():
            req_count = len(reqs)

            # 1. Volumetric Traffic Spike
            if req_count > self.rate_limit_per_minute:
                severity = "critical" if req_count > self.rate_limit_per_minute * 2 else "warning"
                unique_paths = len({r.path for r in reqs})
                alerts.append(
                    SecurityAlert(
                        rule_name="traffic_volume_spike",
                        severity=severity,
                        title=f"Traffic spike from {ip}",
                        description=f"{req_count} requests in {self.window_seconds}s from {ip} (limit: {self.rate_limit_per_minute}/min)",
                        target_type="ip",
                        target_value=ip,
                        source_ip=ip,
                        count=req_count,
                        window_seconds=self.window_seconds,
                        metadata={
                            "request_count": req_count,
                            "unique_endpoints": unique_paths,
                            "rate_per_sec": round(req_count / max(self.window_seconds, 1), 2),
                        },
                    )
                )

            # 2. High Error Rate Surge (4xx / 5xx)
            if req_count >= self.min_requests_for_error_check:
                error_reqs = [r for r in reqs if r.status_code >= 400]
                error_rate = len(error_reqs) / req_count
                if error_rate >= self.error_rate_threshold:
                    alerts.append(
                        SecurityAlert(
                            rule_name="high_error_rate_surge",
                            severity="warning",
                            title=f"High error rate ({error_rate * 100:.1f}%) from {ip}",
                            description=f"{len(error_reqs)} errors out of {req_count} requests ({error_rate * 100:.1f}%) from {ip}",
                            target_type="ip",
                            target_value=ip,
                            source_ip=ip,
                            count=len(error_reqs),
                            window_seconds=self.window_seconds,
                            metadata={
                                "error_count": len(error_reqs),
                                "total_requests": req_count,
                                "error_rate": round(error_rate, 3),
                            },
                        )
                    )

        return alerts
