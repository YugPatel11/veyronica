"""Admin Copilot Agent with Fixed Tool Set (EPIC-17-T01).

Primary conversational and analytical AI agent orchestrating safe tools,
prompt injection defenses, execution plans, and write confirmation cards.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .sanitization import InputSanitizer, SanitizedInput
from .tools import CopilotToolRegistry, ToolDefinition
from .write_tools import WriteToolConfirmationManager, ConfirmationCardData
from .planner import MultiStepPlanner, ExecutionPlan
from .analytics_queries import ReadOnlyAnalyticsEngine, QueryExecutionResult


@dataclass
class CopilotResponse:
    query_id: str
    original_query: str
    sanitized: SanitizedInput
    plan: ExecutionPlan | None
    confirmation_card: ConfirmationCardData | None
    text_content: str
    structured_data: list[dict[str, Any]] | None = None
    data_format: str = "text"  # "text", "table", "chart", "confirmation"


class CopilotAgent:
    """Core Admin Copilot agent executing under strict safety boundaries."""

    def __init__(self, db_path: str = ":memory:") -> None:
        self.tool_registry = CopilotToolRegistry()
        self.confirmation_mgr = WriteToolConfirmationManager()
        self.planner = MultiStepPlanner()
        self.analytics_engine = ReadOnlyAnalyticsEngine(db_path=db_path)

    def process_query(self, user_text: str, query_id: str = "q_001") -> CopilotResponse:
        """Process user input with defense-in-depth security."""
        # 1. Sanitize text as data, not instruction
        sanitized = InputSanitizer.sanitize(user_text)

        if sanitized.is_suspicious:
            return CopilotResponse(
                query_id=query_id,
                original_query=user_text,
                sanitized=sanitized,
                plan=None,
                confirmation_card=None,
                text_content="Security Notice: Potential prompt injection or forbidden SQL instruction detected. Input neutralized.",
                data_format="text",
            )

        q_low = sanitized.cleaned_text.lower()

        # 2. Check for write operations requiring confirmation card
        if any(w in q_low for w in ["publish", "delete", "post to erp", "broadcast"]):
            card = self.confirmation_mgr.prepare_write_card(
                action_name="publish_marks_action",
                description="Publish student marks and sync to external campus records.",
                risk_level="high",
                affected_entity="Exam Marks CS301",
                parameters={"scope": "All evaluated records", "action": "PUBLISH_ERP"},
                diff_summary={"total_records": 42, "state_change": "DRAFT -> PUBLISHED"},
            )
            return CopilotResponse(
                query_id=query_id,
                original_query=user_text,
                sanitized=sanitized,
                plan=None,
                confirmation_card=card,
                text_content="This is a state-changing operation requiring explicit human confirmation. Please review the details below:",
                data_format="confirmation",
            )

        # 3. Multi-step query planning
        if any(w in q_low for w in ["remedial", "failing", "plan", "steps"]):
            plan = self.planner.create_plan_for_intent(sanitized.cleaned_text)
            # Execute step 1
            self.planner.execute_step(plan)
            return CopilotResponse(
                query_id=query_id,
                original_query=user_text,
                sanitized=sanitized,
                plan=plan,
                confirmation_card=None,
                text_content=f"Created multi-step execution plan for: '{plan.goal}'. Step 1 executed successfully.",
                data_format="text",
            )

        # 4. Standard read tool execution
        if "pass" in q_low or "fail" in q_low or "rate" in q_low:
            tool = self.tool_registry.get_tool("get_pass_fail")
            if tool and tool.handler:
                result = tool.handler(course="CS301")
                return CopilotResponse(
                    query_id=query_id,
                    original_query=user_text,
                    sanitized=sanitized,
                    plan=None,
                    confirmation_card=None,
                    text_content=f"Course {result['course']} Assessment Summary: {result['passed']}/{result['total_students']} students passed ({result['pass_percentage']}%).",
                    structured_data=[result],
                    data_format="chart",
                )

        # Default: list students or marks
        tool = self.tool_registry.get_tool("get_marks")
        data = tool.handler(course="CS301") if tool and tool.handler else []
        return CopilotResponse(
            query_id=query_id,
            original_query=user_text,
            sanitized=sanitized,
            plan=None,
            confirmation_card=None,
            text_content=f"Found {len(data)} student mark records for CS301.",
            structured_data=data,
            data_format="table",
        )
