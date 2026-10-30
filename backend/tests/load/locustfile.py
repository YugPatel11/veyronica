"""Locust load test suite for Nexus API endpoints and concurrent workflows.

EPIC-25-T01: Locust load test suite (API endpoints, concurrent workflows).
Simulates realistic production load patterns against FastAPI backend.
"""

from __future__ import annotations

import json
from locust import HttpUser, between, task


class NexusApiUser(HttpUser):
    """Simulates active academic staff browsing dashboards and reviewing records."""

    wait_time = between(0.1, 0.5)

    def on_start(self) -> None:
        """Setup authentication headers."""
        self.headers = {
            "Authorization": "Bearer mock-load-test-token",
            "Content-Type": "application/json",
            "X-Request-ID": "load-test-agent",
        }

    @task(5)
    def test_health_check(self) -> None:
        """High-frequency health and readiness probe."""
        self.client.get("/health", headers=self.headers, name="/health")

    @task(3)
    def test_metrics_scrape(self) -> None:
        """Prometheus telemetry scrape simulation."""
        self.client.get("/metrics", headers=self.headers, name="/metrics")

    @task(4)
    def test_list_workflows(self) -> None:
        """Dashboard query for active workflow runs."""
        self.client.get("/api/v1/workflows", headers=self.headers, name="/api/v1/workflows")

    @task(3)
    def test_list_approvals(self) -> None:
        """Faculty checking pending approvals inbox."""
        self.client.get("/api/v1/approvals", headers=self.headers, name="/api/v1/approvals")

    @task(2)
    def test_audit_ledger_query(self) -> None:
        """Auditor browsing tamper-evident ledger."""
        self.client.get("/api/v1/audit?limit=20", headers=self.headers, name="/api/v1/audit")


class WorkflowExecutionUser(HttpUser):
    """Simulates autonomous workflow invocations, webhooks, and copilot prompts."""

    wait_time = between(0.2, 1.0)

    def on_start(self) -> None:
        self.headers = {
            "Authorization": "Bearer mock-load-test-token",
            "Content-Type": "application/json",
        }

    @task(3)
    def test_copilot_query(self) -> None:
        """Admin querying copilot agent."""
        payload = {
            "user_query": "What is the pass rate for Data Structures?",
            "user_role": "admin",
        }
        self.client.post(
            "/api/v1/copilot/chat",
            data=json.dumps(payload),
            headers=self.headers,
            name="/api/v1/copilot/chat",
        )

    @task(2)
    def test_assignment_submission_webhook(self) -> None:
        """LMS webhook triggering assignment cycle."""
        payload = {
            "event": "assignment.submitted",
            "student_id": "std_1001",
            "assignment_id": "asg_math_01",
            "submitted_at": "2026-10-30T10:00:00Z",
            "due_date": "2026-10-30T23:59:59Z",
        }
        self.client.post(
            "/api/v1/webhooks/assignment",
            data=json.dumps(payload),
            headers=self.headers,
            name="/api/v1/webhooks/assignment",
        )
