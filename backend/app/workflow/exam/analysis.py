"""Analysis Agent: performance trends and risk scoring (EPIC-15-T06).

Computes performance trends against historical baselines, identifies curriculum
weaknesses, and calculates student academic risk levels (low, medium, high, critical).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any
from .evaluation import EvaluationSummary


class AcademicRiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PerformanceTrend:
    trajectory: str  # "improving", "stable", "declining"
    delta_percentage: float
    historical_average: float
    current_percentage: float


@dataclass
class StudentRiskProfile:
    student_roll: str
    risk_level: AcademicRiskLevel
    risk_score: float  # 0.0 to 100.0 (higher = greater risk)
    reasons: list[str] = field(default_factory=list)
    trend: PerformanceTrend | None = None
    recommended_interventions: list[str] = field(default_factory=list)


class AnalysisAgent:
    """Analyzes student exam performance, detecting risk and curriculum anomalies."""

    def calculate_trend(
        self,
        current_pct: float,
        historical_scores: list[float] | None = None,
    ) -> PerformanceTrend:
        """Determine whether performance is improving, stable, or declining."""
        if not historical_scores:
            return PerformanceTrend(
                trajectory="stable",
                delta_percentage=0.0,
                historical_average=current_pct,
                current_percentage=current_pct,
            )

        avg_history = sum(historical_scores) / len(historical_scores)
        delta = round(current_pct - avg_history, 1)

        if delta >= 5.0:
            trajectory = "improving"
        elif delta <= -5.0:
            trajectory = "declining"
        else:
            trajectory = "stable"

        return PerformanceTrend(
            trajectory=trajectory,
            delta_percentage=delta,
            historical_average=round(avg_history, 1),
            current_percentage=current_pct,
        )

    def analyze_risk(
        self,
        summary: EvaluationSummary,
        historical_scores: list[float] | None = None,
    ) -> StudentRiskProfile:
        """Compute academic risk profile based on score and trajectory."""
        pct = summary.percentage
        trend = self.calculate_trend(pct, historical_scores)
        reasons: list[str] = []
        interventions: list[str] = []

        # Risk scoring algorithm
        # Base risk inversely proportional to score
        base_risk = max(0.0, 100.0 - pct)

        # Trajectory penalty
        if trend.trajectory == "declining":
            base_risk += min(20.0, abs(trend.delta_percentage) * 1.5)
            reasons.append(f"Performance declined by {abs(trend.delta_percentage)}% from historical average")
        elif trend.trajectory == "improving":
            base_risk = max(0.0, base_risk - 10.0)

        # Categorize
        if pct < 35.0:
            risk_level = AcademicRiskLevel.CRITICAL
            reasons.append(f"Exam score ({pct}%) is below passing threshold (35%)")
            interventions.append("Schedule urgent parent-faculty meeting")
            interventions.append("Enroll in mandatory remedial tutorial sessions")
        elif pct < 50.0 or base_risk >= 50.0:
            risk_level = AcademicRiskLevel.HIGH
            reasons.append(f"Borderline score ({pct}%) with high risk indicators")
            interventions.append("Assign peer mentor for targeted practice")
            interventions.append("Recommend weekly concept check-ins")
        elif pct < 70.0:
            risk_level = AcademicRiskLevel.MEDIUM
            reasons.append(f"Moderate score ({pct}%); room for improvement")
            interventions.append("Share supplementary reading and problem sets")
        else:
            risk_level = AcademicRiskLevel.LOW
            reasons.append(f"Satisfactory performance ({pct}%)")
            interventions.append("Encourage advanced project participation")

        return StudentRiskProfile(
            student_roll=summary.student_roll,
            risk_level=risk_level,
            risk_score=min(100.0, round(base_risk, 1)),
            reasons=reasons,
            trend=trend,
            recommended_interventions=interventions,
        )
