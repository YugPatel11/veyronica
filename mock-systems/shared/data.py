"""Mock enterprise systems seed data generator.

EPIC-11-T06: Seed data with story characters (Riya Patel, Karan Mehta, 3 divisions).
"""

from __future__ import annotations

from typing import Any

# ── Divisions & Subjects ─────────────────────────────────────────────────────

DIVISIONS = [
    {"id": "div_a", "name": "Division A", "year": "3rd Year", "department": "Computer Science"},
    {"id": "div_b", "name": "Division B", "year": "3rd Year", "department": "Computer Science"},
    {"id": "div_c", "name": "Division C", "year": "3rd Year", "department": "Computer Science"},
]

SUBJECTS = [
    {"id": "sub_cs301", "code": "CS301", "name": "Data Structures & Algorithms", "credits": 4},
    {"id": "sub_cs302", "code": "CS302", "name": "Database Management Systems", "credits": 4},
    {"id": "sub_cs303", "code": "CS303", "name": "Operating Systems", "credits": 3},
]

FACULTY = [
    {"id": "fac_001", "name": "Dr. Ananya Krishnan", "email": "admin@nexus.edu", "role": "HOD"},
    {"id": "fac_002", "name": "Dr. Riya Patel", "email": "faculty@nexus.edu", "role": "Associate Professor"},
    {"id": "fac_003", "name": "Prof. Rajesh Sharma", "email": "rajesh@nexus.edu", "role": "Assistant Professor"},
]

# ── Students ─────────────────────────────────────────────────────────────────

STUDENTS: list[dict[str, Any]] = [
    # Story character 1: Riya Patel, Division B (sharp drop in new exam, triggers at-risk CRM ticket)
    {
        "id": "stu_b_001",
        "roll_number": "CS23B001",
        "name": "Riya Patel",
        "email": "riya.patel@student.nexus.edu",
        "parent_email": "parent.riya@example.com",
        "parent_name": "Sanjay Patel",
        "division": "Division B",
        "division_id": "div_b",
        "attendance_pct": 88.5,
        "is_active": True,
    },
    # Story character 2: Karan Mehta, Division A (borderline answer, low confidence approval trigger)
    {
        "id": "stu_a_001",
        "roll_number": "CS23A001",
        "name": "Karan Mehta",
        "email": "karan.mehta@student.nexus.edu",
        "parent_email": "parent.karan@example.com",
        "parent_name": "Dinesh Mehta",
        "division": "Division A",
        "division_id": "div_a",
        "attendance_pct": 74.0,
        "is_active": True,
    },
    # Story character 3: Aditya Rao, Division C (late assignment submitter)
    {
        "id": "stu_c_001",
        "roll_number": "CS23C001",
        "name": "Aditya Rao",
        "email": "aditya.rao@student.nexus.edu",
        "parent_email": "parent.aditya@example.com",
        "parent_name": "Venkatesh Rao",
        "division": "Division C",
        "division_id": "div_c",
        "attendance_pct": 91.0,
        "is_active": True,
    },
    {
        "id": "stu_a_002",
        "roll_number": "CS23A002",
        "name": "Aarav Sharma",
        "email": "aarav.sharma@student.nexus.edu",
        "parent_email": "parent.aarav@example.com",
        "parent_name": "Manoj Sharma",
        "division": "Division A",
        "division_id": "div_a",
        "attendance_pct": 95.0,
        "is_active": True,
    },
    {
        "id": "stu_b_002",
        "roll_number": "CS23B002",
        "name": "Pooja Verma",
        "email": "pooja.verma@student.nexus.edu",
        "parent_email": "parent.pooja@example.com",
        "parent_name": "Sunil Verma",
        "division": "Division B",
        "division_id": "div_b",
        "attendance_pct": 82.0,
        "is_active": True,
    },
]

# ── Marks ────────────────────────────────────────────────────────────────────

MARKS: list[dict[str, Any]] = [
    {
        "id": "mrk_001",
        "student_id": "stu_b_001",
        "student_name": "Riya Patel",
        "subject_id": "sub_cs301",
        "subject_code": "CS301",
        "exam_type": "Mid-Term",
        "score": 38.0,
        "max_score": 100.0,
        "historical_avg": 84.5,
        "status": "pending_approval",
        "source": "nexus_agent",
        "last_updated": "2026-10-24T10:30:00Z",
    },
    {
        "id": "mrk_002",
        "student_id": "stu_a_001",
        "student_name": "Karan Mehta",
        "subject_id": "sub_cs301",
        "subject_code": "CS301",
        "exam_type": "Mid-Term",
        "score": 41.5,
        "max_score": 100.0,
        "historical_avg": 55.0,
        "status": "pending_approval",
        "source": "nexus_agent",
        "last_updated": "2026-10-24T10:31:00Z",
    },
    {
        "id": "mrk_003",
        "student_id": "stu_a_002",
        "student_name": "Aarav Sharma",
        "subject_id": "sub_cs301",
        "subject_code": "CS301",
        "exam_type": "Mid-Term",
        "score": 92.0,
        "max_score": 100.0,
        "historical_avg": 90.0,
        "status": "published",
        "source": "manual",
        "last_updated": "2026-10-23T14:00:00Z",
    },
]

# ── LMS Courses & Assignments ────────────────────────────────────────────────

COURSES = [
    {"id": "crs_cs301", "name": "Data Structures & Algorithms", "code": "CS301", "instructor": "Dr. Riya Patel"},
    {"id": "crs_cs302", "name": "Database Management Systems", "code": "CS302", "instructor": "Prof. Rajesh Sharma"},
]

ASSIGNMENTS = [
    {"id": "asg_001", "course_id": "crs_cs301", "title": "B-Tree Implementation", "due_date": "2026-10-22T23:59:59Z", "max_points": 50},
    {"id": "asg_002", "course_id": "crs_cs302", "title": "SQL Query Optimization", "due_date": "2026-10-28T23:59:59Z", "max_points": 50},
]

SUBMISSIONS = [
    {"id": "subm_001", "assignment_id": "asg_001", "student_id": "stu_b_001", "submitted_at": "2026-10-21T18:20:00Z", "status": "graded", "grade": 46},
    {"id": "subm_002", "assignment_id": "asg_001", "student_id": "stu_c_001", "submitted_at": "2026-10-23T04:15:00Z", "status": "late", "grade": None},
    {"id": "subm_003", "assignment_id": "asg_001", "student_id": "stu_a_001", "submitted_at": "2026-10-22T20:00:00Z", "status": "submitted", "grade": None},
]

# ── CRM Contacts & Tickets ───────────────────────────────────────────────────

CONTACTS = [
    {"id": "cnt_001", "student_id": "stu_b_001", "name": "Riya Patel", "email": "riya.patel@student.nexus.edu", "phone": "9876543210", "stage": "counselling_needed"},
    {"id": "cnt_002", "student_id": "stu_a_001", "name": "Karan Mehta", "email": "karan.mehta@student.nexus.edu", "phone": "9876543211", "stage": "academic_probation"},
    {"id": "cnt_003", "student_id": "stu_c_001", "name": "Aditya Rao", "email": "aditya.rao@student.nexus.edu", "phone": "9876543212", "stage": "attendance_warning"},
]

TICKETS = [
    {
        "id": "tkt_001",
        "contact_id": "cnt_001",
        "student_name": "Riya Patel",
        "title": "Academic Risk: Sharp Drop in CS301 Mid-term (38% vs 85% avg)",
        "priority": "high",
        "stage": "New",  # New, In Progress, Resolved
        "created_by": "NEXUS Analysis Agent",
        "created_at": "2026-10-24T10:35:00Z",
    },
    {
        "id": "tkt_002",
        "contact_id": "cnt_002",
        "student_name": "Karan Mehta",
        "title": "Attendance & Borderline Marks Review",
        "priority": "medium",
        "stage": "In Progress",
        "created_by": "Faculty Dr. Riya Patel",
        "created_at": "2026-10-22T11:00:00Z",
    },
]

PIPELINE = [
    {"stage": "New", "tickets": ["tkt_001"]},
    {"stage": "In Progress", "tickets": ["tkt_002"]},
    {"stage": "Resolved", "tickets": []},
]
