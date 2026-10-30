"""OpenTelemetry and Prometheus Metrics Export.

EPIC-23-T01: OpenTelemetry instrumentation and trace contexts.
EPIC-23-T02: Prometheus-compatible metrics export.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any


class MetricsRegistry:
    """Thread-safe Prometheus-compatible metrics collector.

    Exports metrics in standard Prometheus text exposition format (v0.0.4).
    """

    def __init__(self) -> None:
        self._counters: dict[str, dict[tuple[tuple[str, str], ...], float]] = defaultdict(lambda: defaultdict(float))
        self._gauges: dict[str, dict[tuple[tuple[str, str], ...], float]] = defaultdict(lambda: defaultdict(float))

    def increment_counter(self, name: str, value: float = 1.0, labels: dict[str, str] | None = None) -> None:
        """Increment a counter by value."""
        label_tuple = tuple(sorted((labels or {}).items()))
        self._counters[name][label_tuple] += value

    def set_gauge(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """Set a gauge to an absolute value."""
        label_tuple = tuple(sorted((labels or {}).items()))
        self._gauges[name][label_tuple] = value

    def render_prometheus_text(self) -> str:
        """Format all recorded metrics in Prometheus exposition format."""
        lines: list[str] = [
            "# HELP nexus_http_requests_total Total HTTP requests handled",
            "# TYPE nexus_http_requests_total counter",
            "# HELP nexus_workflow_runs_total Total workflow executions initiated",
            "# TYPE nexus_workflow_runs_total counter",
            "# HELP nexus_llm_tokens_total Total tokens consumed by agent and model tier",
            "# TYPE nexus_llm_tokens_total counter",
            "# HELP nexus_llm_cost_usd_total Estimated LLM expenditure in USD",
            "# TYPE nexus_llm_cost_usd_total counter",
            "# HELP nexus_connector_calls_total Total connector invocations",
            "# TYPE nexus_connector_calls_total counter",
            "# HELP nexus_ledger_blocks_total Total cryptographic blocks in audit ledger",
            "# TYPE nexus_ledger_blocks_total gauge",
        ]

        # Render counters
        for metric_name, label_map in sorted(self._counters.items()):
            for label_tuple, val in sorted(label_map.items()):
                label_str = ""
                if label_tuple:
                    pairs = [f'{k}="{v}"' for k, v in label_tuple]
                    label_str = "{" + ",".join(pairs) + "}"
                lines.append(f"{metric_name}{label_str} {val}")

        # Render gauges
        for metric_name, label_map in sorted(self._gauges.items()):
            for label_tuple, val in sorted(label_map.items()):
                label_str = ""
                if label_tuple:
                    pairs = [f'{k}="{v}"' for k, v in label_tuple]
                    label_str = "{" + ",".join(pairs) + "}"
                lines.append(f"{metric_name}{label_str} {val}")

        return "\n".join(lines) + "\n"


# Singleton instance
metrics = MetricsRegistry()

# Initialize base metrics
metrics.set_gauge("nexus_ledger_blocks_total", 0.0)
metrics.increment_counter("nexus_http_requests_total", 0.0, {"method": "GET", "status": "200"})
