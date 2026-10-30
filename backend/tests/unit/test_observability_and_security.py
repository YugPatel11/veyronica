"""Unit tests for Observability, Monitoring & Security Hardening (Batch 8).

Validates:
- EPIC-23-T03: Grafana dashboard definitions
- EPIC-23-T04: Prometheus alerting rules
- EPIC-23-T05: SLO definitions with burn-rate alerts
- EPIC-23-T08: LLM cost and latency dashboard
- EPIC-24-T01: Dependency scanning workflow
- EPIC-24-T02: Container image scanning workflow & script
- EPIC-24-T07: OWASP ASVS Level 2 checklist
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def test_grafana_dashboards_validity() -> None:
    dashboards_dir = REPO_ROOT / "deploy" / "grafana" / "dashboards"
    assert dashboards_dir.exists(), "Grafana dashboards directory missing"

    required_dashboards = [
        "api_health.json",
        "workflow_ops.json",
        "connectors.json",
        "llm_cost_latency.json",
    ]

    for dash_name in required_dashboards:
        dash_path = dashboards_dir / dash_name
        assert dash_path.exists(), f"Dashboard {dash_name} missing"

        with open(dash_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "title" in data, f"Dashboard {dash_name} missing title"
        assert "panels" in data and len(data["panels"]) >= 4, f"Dashboard {dash_name} has insufficient panels"

        # Verify panels have targets with PromQL queries
        for panel in data["panels"]:
            assert "title" in panel
            assert "type" in panel
            if "targets" in panel:
                for target in panel["targets"]:
                    assert "expr" in target and len(target["expr"]) > 0


def test_prometheus_alerting_rules_validity() -> None:
    alerts_file = REPO_ROOT / "deploy" / "prometheus" / "alerts.yml"
    assert alerts_file.exists(), "Prometheus alerts.yml missing"

    with open(alerts_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert "groups" in data and len(data["groups"]) > 0
    rules = data["groups"][0].get("rules", [])
    assert len(rules) >= 5, "Expected at least 5 alerting rules"

    rule_names = {r["alert"] for r in rules}
    assert "HighHttpErrorRate" in rule_names
    assert "StuckWorkflowRun" in rule_names
    assert "LedgerIntegrityMismatch" in rule_names
    assert "LLMBudgetExceeded" in rule_names
    assert "ConnectorCircuitOpen" in rule_names

    for rule in rules:
        assert "expr" in rule
        assert "for" in rule
        assert "labels" in rule and "severity" in rule["labels"]
        assert "annotations" in rule and "summary" in rule["annotations"]


def test_slo_definitions_and_burn_rate_alerts() -> None:
    slo_file = REPO_ROOT / "deploy" / "slo" / "slo_definitions.yml"
    assert slo_file.exists(), "SLO definitions YAML missing"

    with open(slo_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert "slos" in data and len(data["slos"]) >= 3
    slo_ids = {s["id"] for s in data["slos"]}
    assert "slo_api_availability" in slo_ids
    assert "slo_api_latency" in slo_ids
    assert "slo_workflow_success" in slo_ids

    for slo in data["slos"]:
        assert 0.9 <= slo["target"] <= 1.0
        assert "burn_rate_alerts" in slo and len(slo["burn_rate_alerts"]) >= 1
        for alert in slo["burn_rate_alerts"]:
            assert "burn_rate_threshold" in alert
            assert alert["burn_rate_threshold"] > 1.0


def test_security_workflows_and_scanning_scripts() -> None:
    ci_dep_scan = REPO_ROOT / ".github" / "workflows" / "security-scan.yml"
    assert ci_dep_scan.exists(), "security-scan.yml missing"
    with open(ci_dep_scan, "r", encoding="utf-8") as f:
        content = f.read()
    assert "trivy-action" in content
    assert "pip-audit" in content
    assert "npm audit" in content

    ci_cont_scan = REPO_ROOT / ".github" / "workflows" / "container-scan.yml"
    assert ci_cont_scan.exists(), "container-scan.yml missing"
    with open(ci_cont_scan, "r", encoding="utf-8") as f:
        cont_content = f.read()
    assert "trivy-action" in cont_content
    assert "docker/build-push-action" in cont_content

    scan_script = REPO_ROOT / "scripts" / "scan_containers.sh"
    assert scan_script.exists(), "scan_containers.sh missing"


def test_owasp_asvs_checklist_document() -> None:
    audit_file = REPO_ROOT / "docs" / "security" / "OWASP_ASVS_LEVEL2_AUDIT.md"
    assert audit_file.exists(), "OWASP_ASVS_LEVEL2_AUDIT.md missing"

    with open(audit_file, "r", encoding="utf-8") as f:
        text = f.read()

    assert "OWASP Application Security Verification Standard" in text
    assert "Level 2" in text
    assert "V1: Architecture" in text
    assert "V2: Authentication" in text
    assert "V3: Session Management" in text
    assert "V4: Input Validation" in text
    assert "V5: Cryptography" in text
    assert "V6: Error Handling" in text
    assert "V7: Data Protection" in text
    assert "PASSED" in text
