"""Scheduled Overdue Detection Agent for Assignments (EPIC-16-T04).

Periodic scanning routine (compatible with Celery Beat schedule) to identify
students who have missed submission deadlines and flag them for follow-up.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class OverdueStudentInfo:
    student_roll: str
    student_name: str
    parent_email: str
    assignment_id: str
    assignment_title: str
    course_code: str
    due_date: datetime
    hours_overdue: float


@dataclass
class OverdueScanReport:
    scan_timestamp: str
    assignments_scanned: int
    total_overdue_detected: int
    overdue_students: list[OverdueStudentInfo] = field(default_factory=list)


class OverdueDetector:
    """Scans enrolled rosters against assignment deadlines to flag overdue submissions."""

    def scan_overdue_assignments(
        self,
        assignments: list[dict[str, Any]],
        enrolled_students: list[dict[str, Any]],
        submissions: list[dict[str, Any]],
        current_time: datetime | None = None,
    ) -> OverdueScanReport:
        """Identify missing submissions past the due date."""
        now = current_time or datetime.now(timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        # Index submitted keys: (assignment_id, student_roll)
        submitted_keys = {
            (s.get("assignment_id"), s.get("student_roll")) for s in submissions
        }

        overdue_list: list[OverdueStudentInfo] = []

        for asgn in assignments:
            asgn_id = asgn["id"]
            due_date = asgn["due_date"]
            if isinstance(due_date, str):
                due_date = datetime.fromisoformat(due_date)
            if due_date.tzinfo is None:
                due_date = due_date.replace(tzinfo=timezone.utc)

            # Only check if due date has passed
            if now > due_date:
                hours_past = round((now - due_date).total_seconds() / 3600.0, 1)

                # Filter students enrolled in this assignment course
                course = asgn.get("course_code", "GEN-01")
                for student in enrolled_students:
                    roll = student["roll"]
                    if (asgn_id, roll) not in submitted_keys:
                        overdue_list.append(
                            OverdueStudentInfo(
                                student_roll=roll,
                                student_name=student.get("name", "Student"),
                                parent_email=student.get("parent_email", "parent@example.edu"),
                                assignment_id=asgn_id,
                                assignment_title=asgn.get("title", "Assignment"),
                                course_code=course,
                                due_date=due_date,
                                hours_overdue=hours_past,
                            )
                        )

        return OverdueScanReport(
            scan_timestamp=now.isoformat(),
            assignments_scanned=len(assignments),
            total_overdue_detected=len(overdue_list),
            overdue_students=overdue_list,
        )
