"""Communication Agent: parent email drafting (EPIC-15-T07).

Drafts personalized, professional, and empathetic notifications to parents/guardians
tailored to performance level and academic risk profile.
"""

from __future__ import annotations

from dataclasses import dataclass
from .analysis import AcademicRiskLevel, StudentRiskProfile
from .evaluation import EvaluationSummary


@dataclass
class ParentEmailDraft:
    recipient_email: str
    student_roll: str
    student_name: str
    subject: str
    body_plain: str
    body_html: str
    tone: str  # "congratulatory", "encouraging", "supportive_action", "urgent_intervention"
    requires_consent_check: bool = True


class CommunicationAgent:
    """Drafts parent communications based on academic results and risk assessment."""

    def draft_parent_email(
        self,
        summary: EvaluationSummary,
        risk_profile: StudentRiskProfile,
        student_name: str = "Student",
        parent_email: str = "parent@example.edu",
        course_name: str = "Computer Science Fundamentals",
    ) -> ParentEmailDraft:
        """Generate tailored parent email draft matching student trajectory."""
        pct = summary.percentage
        score_str = f"{summary.total_marks_awarded}/{summary.total_max_marks} ({pct}%)"

        if risk_profile.risk_level == AcademicRiskLevel.LOW:
            tone = "congratulatory"
            subject = f"Academic Update: Outstanding Performance in {course_name} — {student_name}"
            intro = f"We are pleased to inform you that {student_name} performed exceptionally well in the recent {course_name} assessment, scoring {score_str}."
            action = "We applaud their dedication and encourage continued exploration in advanced coursework."
        elif risk_profile.risk_level == AcademicRiskLevel.MEDIUM:
            tone = "encouraging"
            subject = f"Academic Progress Report: {course_name} — {student_name}"
            intro = f"This is an update regarding {student_name}'s recent performance in {course_name}. They scored {score_str}."
            action = "With focused review on key concepts, we are confident they will strengthen their grasp in the upcoming units."
        elif risk_profile.risk_level == AcademicRiskLevel.HIGH:
            tone = "supportive_action"
            subject = f"Academic Support Advisory: {course_name} — {student_name}"
            intro = f"We are writing to share {student_name}'s recent evaluation in {course_name}, where they achieved {score_str}."
            action = "To help them improve, our department has arranged targeted academic mentoring and review sessions. We encourage their active participation."
        else:  # CRITICAL
            tone = "urgent_intervention"
            subject = f"Urgent: Academic Review and Meeting Request — {student_name} ({course_name})"
            intro = f"We are writing to urgently discuss {student_name}'s recent performance in {course_name}, where they scored {score_str}, which is below passing threshold."
            action = "We request a parent-faculty meeting this week to formulate an individual academic recovery plan. Please contact the department coordinator to schedule."

        body_plain = f"""Dear Parent / Guardian,

{intro}

Performance Details:
- Roll Number: {summary.student_roll}
- Course: {course_name}
- Total Marks: {summary.total_marks_awarded} out of {summary.total_max_marks}
- Percentage: {pct}%
- Academic Trajectory: {risk_profile.trend.trajectory.title() if risk_profile.trend else 'Current'}

Next Steps:
{action}

Warm regards,
Academic Examination & Mentorship Committee
Nexus Institution
"""

        body_html = f"""<div style="font-family: Arial, sans-serif; line-height: 1.6; color: #1e293b;">
<h2 style="color: #4338ca;">Academic Progress Notification</h2>
<p>Dear Parent / Guardian,</p>
<p>{intro}</p>
<div style="background-color: #f8fafc; border-left: 4px solid #6366f1; padding: 12px 16px; margin: 16px 0;">
  <strong>Assessment Summary:</strong><br />
  • <strong>Student:</strong> {student_name} ({summary.student_roll})<br />
  • <strong>Course:</strong> {course_name}<br />
  • <strong>Score:</strong> {score_str}<br />
  • <strong>Risk Assessment:</strong> {risk_profile.risk_level.value.upper()}
</div>
<p><strong>Next Steps:</strong></p>
<p>{action}</p>
<p style="margin-top: 24px;">Warm regards,<br /><strong>Academic Examination & Mentorship Committee</strong><br />Nexus Institution</p>
</div>"""

        return ParentEmailDraft(
            recipient_email=parent_email,
            student_roll=summary.student_roll,
            student_name=student_name,
            subject=subject,
            body_plain=body_plain.strip(),
            body_html=body_html.strip(),
            tone=tone,
            requires_consent_check=True,
        )
