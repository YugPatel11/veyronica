"""Multi-Step Plan Execution for Copilot (EPIC-17-T07).

Breaks down complex administrative queries into sequential, observable steps
with progress status tracking ('pending', 'running', 'completed', 'failed').
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Callable


class PlanStepStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PlanStep:
    step_id: str
    title: str
    description: str
    tool_name: str | None
    status: PlanStepStatus = PlanStepStatus.PENDING
    result: Any | None = None
    error: str | None = None


@dataclass
class ExecutionPlan:
    plan_id: str
    goal: str
    steps: list[PlanStep] = field(default_factory=list)
    current_step_index: int = 0
    is_finished: bool = False
    status: str = "created"  # "created", "running", "completed", "failed"

    @property
    def progress_percentage(self) -> float:
        if not self.steps:
            return 100.0
        completed = sum(1 for s in self.steps if s.status == PlanStepStatus.COMPLETED)
        return round((completed / len(self.steps)) * 100.0, 1)


class MultiStepPlanner:
    """Creates and tracks multi-step plans for Copilot tasks."""

    def create_plan_for_intent(self, user_intent: str) -> ExecutionPlan:
        """Decompose user query into multi-step execution plan."""
        plan_id = f"plan_{uuid.uuid4().hex[:10]}"
        intent_lower = user_intent.lower()

        steps: list[PlanStep] = []

        if "remedial" in intent_lower or "failing" in intent_lower or "below" in intent_lower:
            steps = [
                PlanStep(
                    step_id="step_1",
                    title="Query Assessment Data",
                    description="Fetch student marks below passing threshold in course.",
                    tool_name="get_marks",
                ),
                PlanStep(
                    step_id="step_2",
                    title="Evaluate Risk & Trends",
                    description="Analyze historical performance to prioritize interventions.",
                    tool_name="analyze_risk",
                ),
                PlanStep(
                    step_id="step_3",
                    title="Prepare Remedial Enrollment",
                    description="Compile roster for targeted tutorial sessions.",
                    tool_name="enroll_remedial",
                ),
            ]
        elif "approval" in intent_lower:
            steps = [
                PlanStep(
                    step_id="step_1",
                    title="Fetch Pending Queue",
                    description="Retrieve all items awaiting coordinator sign-off.",
                    tool_name="get_pending_approvals",
                ),
                PlanStep(
                    step_id="step_2",
                    title="Summarize Urgency Tiers",
                    description="Classify items by countdown timer and risk profile.",
                    tool_name="classify_approvals",
                ),
            ]
        else:
            steps = [
                PlanStep(
                    step_id="step_1",
                    title="Retrieve Relevant Records",
                    description="Query campus database for requested context.",
                    tool_name="get_students",
                ),
                PlanStep(
                    step_id="step_2",
                    title="Synthesize Response",
                    description="Format tabular data and highlights for display.",
                    tool_name=None,
                ),
            ]

        return ExecutionPlan(
            plan_id=plan_id,
            goal=user_intent,
            steps=steps,
        )

    def execute_step(
        self,
        plan: ExecutionPlan,
        executor_func: Callable[[PlanStep], Any] | None = None,
    ) -> ExecutionPlan:
        """Advance the plan by executing the current step."""
        if plan.current_step_index >= len(plan.steps):
            plan.is_finished = True
            plan.status = "completed"
            return plan

        step = plan.steps[plan.current_step_index]
        step.status = PlanStepStatus.RUNNING

        try:
            if executor_func:
                step.result = executor_func(step)
            else:
                step.result = {"status": "ok", "message": f"Step '{step.title}' executed successfully"}

            step.status = PlanStepStatus.COMPLETED
            plan.current_step_index += 1
            if plan.current_step_index >= len(plan.steps):
                plan.is_finished = True
                plan.status = "completed"
            else:
                plan.status = "running"
        except Exception as e:
            step.status = PlanStepStatus.FAILED
            step.error = str(e)
            plan.status = "failed"
            plan.is_finished = True

        return plan
