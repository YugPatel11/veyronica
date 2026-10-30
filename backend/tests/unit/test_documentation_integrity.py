"""Unit tests for Documentation Verification (Batch 10).

Covers DOC-01 through DOC-05:
- DOC-01: ADRs and master index
- DOC-02: API Reference documentation
- DOC-03: 10 Operational Runbooks
- DOC-04: Developer Onboarding Guide
- DOC-05: Design System Documentation
"""

from __future__ import annotations

from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def test_adr_documentation_and_index() -> None:
    adr_dir = REPO_ROOT / "docs" / "adr"
    assert adr_dir.exists(), "docs/adr directory missing"

    index_file = adr_dir / "README.md"
    assert index_file.exists(), "docs/adr/README.md missing"
    with open(index_file, "r", encoding="utf-8") as f:
        text = f.read()

    for adr_num in ["001", "002", "003", "004", "005", "006", "007", "008", "009", "010", "011", "012", "013"]:
        assert f"ADR-{adr_num}" in text, f"ADR-{adr_num} missing from index"

    for adr_file in [
        "011-exam-ingestion-dual-verification.md",
        "012-copilot-safe-write-confirmation.md",
        "013-security-engine-automated-containment.md",
    ]:
        path = adr_dir / adr_file
        assert path.exists(), f"ADR file {adr_file} missing"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "Context" in content
        assert "Decision" in content
        assert "Consequences" in content


def test_api_reference_documentation() -> None:
    api_doc = REPO_ROOT / "docs" / "api" / "API_REFERENCE.md"
    assert api_doc.exists(), "docs/api/API_REFERENCE.md missing"

    with open(api_doc, "r", encoding="utf-8") as f:
        text = f.read()

    assert "/api/v1/auth/login" in text
    assert "/api/v1/exam-workflow/trigger" in text
    assert "/api/v1/copilot/chat" in text
    assert "/api/v1/audit" in text
    assert "/health" in text


def test_operational_runbooks() -> None:
    runbooks_doc = REPO_ROOT / "docs" / "runbooks" / "RUNBOOKS.md"
    assert runbooks_doc.exists(), "docs/runbooks/RUNBOOKS.md missing"

    with open(runbooks_doc, "r", encoding="utf-8") as f:
        text = f.read()

    for i in range(1, 11):
        rb_id = f"RB-{i:02d}"
        assert rb_id in text, f"Runbook {rb_id} missing from RUNBOOKS.md"


def test_developer_onboarding_guide() -> None:
    setup_doc = REPO_ROOT / "docs" / "onboarding" / "DEVELOPER_SETUP.md"
    assert setup_doc.exists(), "docs/onboarding/DEVELOPER_SETUP.md missing"

    with open(setup_doc, "r", encoding="utf-8") as f:
        text = f.read()

    assert "Prerequisites" in text
    assert "docker compose up -d" in text
    assert "npm run dev" in text
    assert "pytest" in text


def test_design_system_documentation() -> None:
    design_doc = REPO_ROOT / "docs" / "design" / "DESIGN_SYSTEM.md"
    assert design_doc.exists(), "docs/design/DESIGN_SYSTEM.md missing"

    with open(design_doc, "r", encoding="utf-8") as f:
        text = f.read()

    assert "--background" in text
    assert "--primary" in text
    assert "Component Catalog" in text
    assert "Storybook" in text
    assert "WCAG 2.2 AA" in text
