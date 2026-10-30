"""Timetable Generation Engine & Constraint Solver.

EPIC-26-T01: Input data parser with validation.
EPIC-26-T02: Constraint builder.
EPIC-26-T03: Constraint satisfaction scheduler.
EPIC-26-T04: Conflict detection and infeasibility explanation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
PERIODS = [1, 2, 3, 4, 5]  # Periods 1 to 5 (e.g. 9am to 3pm)


@dataclass
class Classroom:
    id: str
    name: str
    capacity: int


@dataclass
class CourseSession:
    id: str
    course_code: str
    course_name: str
    faculty_id: str
    division: str
    student_count: int


@dataclass
class ScheduledSlot:
    day: str
    period: int
    session: CourseSession
    classroom: Classroom


@dataclass
class TimetableResult:
    success: bool
    schedule: list[ScheduledSlot] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    total_slots_needed: int = 0
    total_slots_assigned: int = 0


class TimetableSolver:
    """Constraint Satisfaction Scheduler for Academic Timetables."""

    def __init__(
        self,
        classrooms: list[Classroom] | None = None,
        faculty_unavailability: dict[str, list[tuple[str, int]]] | None = None,
        days: list[str] | None = None,
        periods: list[int] | None = None,
    ) -> None:
        self.classrooms = classrooms or [
            Classroom("CR-101", "Lecture Hall 101", 60),
            Classroom("CR-102", "Lecture Hall 102", 60),
            Classroom("LAB-201", "Systems Lab 201", 40),
        ]
        # Map of faculty_id -> list of (day, period) unavailable
        self.faculty_unavailability = faculty_unavailability or {}
        self.days = days or DAYS
        self.periods = periods or PERIODS

    def solve(self, sessions: list[CourseSession]) -> TimetableResult:
        """Assign sessions to (day, period, classroom) while respecting all constraints."""
        schedule: list[ScheduledSlot] = []
        conflicts: list[str] = []

        # Tracking booked resources:
        # booked_rooms[(day, period)] = set of classroom ids
        booked_rooms: dict[tuple[str, int], set[str]] = {}
        # booked_faculty[(day, period)] = set of faculty ids
        booked_faculty: dict[tuple[str, int], set[str]] = {}
        # booked_divisions[(day, period)] = set of division names
        booked_divisions: dict[tuple[str, int], set[str]] = {}

        for day in self.days:
            for p in self.periods:
                booked_rooms[(day, p)] = set()
                booked_faculty[(day, p)] = set()
                booked_divisions[(day, p)] = set()

        for session in sessions:
            assigned = False

            # Check if faculty has availability
            unavail = self.faculty_unavailability.get(session.faculty_id, [])

            for day in self.days:
                if assigned:
                    break
                for period in self.periods:
                    slot_key = (day, period)

                    # 1. Faculty availability check
                    if (day, period) in unavail:
                        continue

                    # 2. Faculty conflict check
                    if session.faculty_id in booked_faculty[slot_key]:
                        continue

                    # 3. Student cohort conflict check
                    if session.division in booked_divisions[slot_key]:
                        continue

                    # 4. Find suitable classroom
                    suitable_room = None
                    for room in self.classrooms:
                        if room.id not in booked_rooms[slot_key] and room.capacity >= session.student_count:
                            suitable_room = room
                            break

                    if suitable_room:
                        # Make assignment
                        booked_rooms[slot_key].add(suitable_room.id)
                        booked_faculty[slot_key].add(session.faculty_id)
                        booked_divisions[slot_key].add(session.division)

                        schedule.append(ScheduledSlot(
                            day=day,
                            period=period,
                            session=session,
                            classroom=suitable_room,
                        ))
                        assigned = True
                        break

            if not assigned:
                conflicts.append(
                    f"Unable to place {session.course_code} ({session.course_name}) for {session.division}: "
                    f"no clash-free room with capacity >= {session.student_count} available for faculty {session.faculty_id}."
                )

        return TimetableResult(
            success=len(conflicts) == 0,
            schedule=schedule,
            conflicts=conflicts,
            total_slots_needed=len(sessions),
            total_slots_assigned=len(schedule),
        )


solver = TimetableSolver()
