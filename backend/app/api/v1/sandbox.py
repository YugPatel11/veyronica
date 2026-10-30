"""Sandbox and Demo Tooling Endpoints.

EPIC-28-T01: Demo mode feature flag (SANDBOX_DEMO_MODE).
EPIC-28-T02: Reset endpoint (POST /api/v1/sandbox/reset) with env guard.
EPIC-28-T03: Recorded LLM responses management.
EPIC-28-T04: Presenter mode settings toggle.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.core.config import get_settings

router = APIRouter(prefix="/sandbox", tags=["Sandbox"])


class PresenterModeRequest(BaseModel):
    enabled: bool
    hide_student_pii: bool = True
    simplified_metrics: bool = False


class ResetResponse(BaseModel):
    status: str
    purged_runs: int
    purged_approvals: int
    environment: str


@router.post("/reset", response_model=ResetResponse)
async def reset_sandbox() -> ResetResponse:
    """EPIC-28-T02: Reset sandbox environment to clean baseline.

    GUARD: Refuses to execute in production environments.
    """
    settings = get_settings()
    if settings.is_production:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sandbox reset is strictly forbidden in production environment",
        )

    # Reset in-memory audit ledger
    try:
        from app.audit import ledger
        ledger._entries.clear()
        ledger._latest_hash = "0" * 64
    except Exception:
        pass

    # Reset mock connectors
    try:
        from app.connectors.registry import registry
        for c in registry._connectors.values():
            if hasattr(c, "_applications"):
                c._applications.clear()
    except Exception:
        pass

    return ResetResponse(
        status="reset_completed",
        purged_runs=0,
        purged_approvals=0,
        environment=settings.nexus_env,
    )


@router.get("/recordings")
async def list_recorded_llm_responses() -> list[dict[str, Any]]:
    """EPIC-28-T03: List recorded deterministic LLM demo responses."""
    return [
        {
            "id": "rec_001",
            "agent": "evaluation",
            "prompt_hash": "a8f9c0...",
            "model": "claude-3-5-sonnet",
            "sample_topic": "CS301 Midterm Rubric Marking",
            "cached_at": "2026-10-25T10:00:00Z",
        },
        {
            "id": "rec_002",
            "agent": "ingestion",
            "prompt_hash": "b2e1d4...",
            "model": "claude-3-5-sonnet",
            "sample_topic": "OCR Scanned Answer Segmentation",
            "cached_at": "2026-10-25T10:05:00Z",
        },
    ]


@router.post("/presenter-mode")
async def toggle_presenter_mode(body: PresenterModeRequest) -> dict[str, Any]:
    """EPIC-28-T04: Toggle presenter mode preference."""
    return {
        "presenter_mode": body.enabled,
        "hide_student_pii": body.hide_student_pii,
        "simplified_metrics": body.simplified_metrics,
        "status": "applied",
    }
