"""Copilot Tool Registration: Read Tools (EPIC-17-T02).

Provides registered, safe read tools for querying students, marks,
pass/fail ratios, pending approvals, and connector health metrics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: dict[str, Any]
    is_write: bool = False
    handler: Callable[..., Any] | None = None


class CopilotToolRegistry:
    """Registry of allowlisted read and write tools for Copilot."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}
        self._register_default_read_tools()

    def register(self, tool: ToolDefinition) -> None:
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> ToolDefinition | None:
        return self._tools.get(name)

    def list_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters,
                "is_write": t.is_write,
            }
            for t in self._tools.values()
        ]

    def _register_default_read_tools(self) -> None:
        # Tool: get_students
        self.register(
            ToolDefinition(
                name="get_students",
                description="List students filtered by division, course, or academic standing.",
                parameters={
                    "type": "object",
                    "properties": {
                        "division": {"type": "string", "description": "e.g. Division A"},
                        "course": {"type": "string", "description": "e.g. CS301"},
                        "status": {"type": "string", "enum": ["active", "probation", "all"]},
                    },
                },
                is_write=False,
                handler=self._handle_get_students,
            )
        )

        # Tool: get_marks
        self.register(
            ToolDefinition(
                name="get_marks",
                description="Query marks obtained by students in a course or exam.",
                parameters={
                    "type": "object",
                    "properties": {
                        "student_roll": {"type": "string"},
                        "course": {"type": "string"},
                        "min_score": {"type": "number"},
                        "max_score": {"type": "number"},
                    },
                },
                is_write=False,
                handler=self._handle_get_marks,
            )
        )

        # Tool: get_pass_fail
        self.register(
            ToolDefinition(
                name="get_pass_fail",
                description="Aggregate pass/fail statistics and percentages for a course assessment.",
                parameters={
                    "type": "object",
                    "properties": {
                        "course": {"type": "string"},
                        "passing_threshold": {"type": "number", "default": 40.0},
                    },
                    "required": ["course"],
                },
                is_write=False,
                handler=self._handle_get_pass_fail,
            )
        )

        # Tool: get_pending_approvals
        self.register(
            ToolDefinition(
                name="get_pending_approvals",
                description="Fetch the list of workflows currently awaiting faculty or admin approval.",
                parameters={"type": "object", "properties": {"urgency": {"type": "string"}}},
                is_write=False,
                handler=self._handle_get_pending_approvals,
            )
        )

    def _handle_get_students(self, division: str | None = None, course: str | None = None, **kwargs: Any) -> list[dict[str, Any]]:
        # Mock structured data query
        return [
            {"roll": "CS-01", "name": "Aarav Sharma", "division": division or "A", "course": course or "CS301", "standing": "good"},
            {"roll": "CS-02", "name": "Vivaan Patel", "division": division or "A", "course": course or "CS301", "standing": "probation"},
            {"roll": "CS-03", "name": "Diya Bhat", "division": division or "B", "course": course or "CS301", "standing": "good"},
        ]

    def _handle_get_marks(self, course: str = "CS301", **kwargs: Any) -> list[dict[str, Any]]:
        return [
            {"roll": "CS-01", "name": "Aarav Sharma", "course": course, "score": 88.0, "max_score": 100.0, "grade": "A"},
            {"roll": "CS-02", "name": "Vivaan Patel", "course": course, "score": 34.0, "max_score": 100.0, "grade": "F"},
            {"roll": "CS-03", "name": "Diya Bhat", "course": course, "score": 92.5, "max_score": 100.0, "grade": "A+"},
        ]

    def _handle_get_pass_fail(self, course: str, passing_threshold: float = 40.0) -> dict[str, Any]:
        marks = self._handle_get_marks(course=course)
        passed = sum(1 for m in marks if m["score"] >= passing_threshold)
        total = len(marks)
        return {
            "course": course,
            "total_students": total,
            "passed": passed,
            "failed": total - passed,
            "pass_percentage": round((passed / total) * 100.0, 1) if total else 0.0,
        }

    def _handle_get_pending_approvals(self, **kwargs: Any) -> list[dict[str, Any]]:
        return [
            {"id": "appr_101", "workflow": "exam_result_cycle", "roll": "CS-02", "urgency": "high", "reason": "Low confidence score"},
            {"id": "appr_102", "workflow": "assignment_cycle", "roll": "CS-05", "urgency": "medium", "reason": "Late penalty override"},
        ]
