"""Workflow Executor — step-by-step engine.

EPIC-07-T05: Master Agent dispatch.
EPIC-07-T06: Parallel fan-out.
EPIC-07-T07: Approval node with interrupt.
EPIC-07-T08: Branch/conditional routing.
EPIC-07-T11: Failure handling.
EPIC-07-T12: Decision Replay.
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import UTC, datetime
from typing import Any

import structlog

from app.workflow import (
    AutonomyLevel,
    RunState,
    StepDefinition,
    WorkflowSchema,
    parse_workflow_yaml,
)

logger = structlog.get_logger()


class WorkflowExecutor:
    """Execute a workflow definition step by step.

    Handles sequential, parallel, branch, and approval steps.
    """

    def __init__(self) -> None:
        self._checkpoints: dict[str, list[RunState]] = {}

    async def start_run(
        self,
        workflow: WorkflowSchema,
        *,
        trigger_type: str = "manual",
        trigger_payload: dict[str, Any] | None = None,
        initiated_by: str | None = None,
        autonomy: str = "supervised",
        input_data: dict[str, Any] | None = None,
    ) -> RunState:
        """Start a new workflow run."""
        run_id = str(uuid.uuid4())
        step_names = [s.name for s in workflow.steps]

        state: RunState = {
            "run_id": run_id,
            "definition_id": workflow.slug,
            "workflow_name": workflow.name,
            "status": "running",
            "autonomy": autonomy,
            "current_step": step_names[0] if step_names else "",
            "steps_completed": [],
            "steps_remaining": step_names,
            "trigger_type": trigger_type,
            "trigger_payload": trigger_payload or {},
            "initiated_by": initiated_by or "",
            "started_at": datetime.now(UTC).isoformat(),
            "input_data": input_data or {},
            "output_data": {},
            "errors": [],
            "total_tokens": 0,
            "total_cost_usd": 0.0,
            "approval_pending": None,
            "checkpoint_id": "",
        }

        self._save_checkpoint(state)

        logger.info("workflow_run_started", run_id=run_id, workflow=workflow.name)

        # Execute steps sequentially
        for step in workflow.steps:
            try:
                state["current_step"] = step.name
                state["steps_remaining"] = [
                    s for s in state.get("steps_remaining", []) if s != step.name
                ]

                result = await self._execute_step(step, state)

                if result.get("approval_needed"):
                    state["status"] = "waiting_approval"
                    state["approval_pending"] = result
                    self._save_checkpoint(state)
                    logger.info("workflow_waiting_approval", run_id=run_id, step=step.name)
                    return state

                state["steps_completed"] = state.get("steps_completed", []) + [step.name]
                state["output_data"][step.name] = result  # type: ignore[index]
                self._save_checkpoint(state)

            except Exception as e:
                state["status"] = "failed"
                state["errors"] = state.get("errors", []) + [
                    {"step": step.name, "error": str(e), "timestamp": datetime.now(UTC).isoformat()}
                ]
                self._save_checkpoint(state)

                # EPIC-07-T11: Failure handling
                if workflow.on_failure == "retry" and step.retry_max > 0:
                    logger.warning("workflow_step_retry", step=step.name, error=str(e))
                    continue
                elif workflow.on_failure == "escalate":
                    logger.error("workflow_step_failed_escalate", step=step.name, error=str(e))
                    return state
                else:
                    return state

        state["status"] = "completed"
        self._save_checkpoint(state)
        logger.info("workflow_run_completed", run_id=run_id)
        return state

    async def resume_after_approval(
        self, state: RunState, approved: bool, reason: str = ""
    ) -> RunState:
        """Resume a workflow after an approval decision."""
        if not approved:
            state["status"] = "failed"
            state["errors"] = state.get("errors", []) + [
                {"step": state.get("current_step", ""), "error": f"Approval rejected: {reason}"}
            ]
            return state

        state["status"] = "running"
        state["approval_pending"] = None
        step_name = state.get("current_step", "")
        state["steps_completed"] = state.get("steps_completed", []) + [step_name]
        self._save_checkpoint(state)
        return state

    async def _execute_step(
        self, step: StepDefinition, state: RunState
    ) -> dict[str, Any]:
        """Execute a single workflow step."""
        logger.info("executing_step", step=step.name, type=step.type)

        if step.type == "agent":
            return await self._execute_agent_step(step, state)
        elif step.type == "approval":
            return await self._execute_approval_step(step, state)
        elif step.type == "connector":
            return await self._execute_connector_step(step, state)
        elif step.type == "parallel":
            return await self._execute_parallel_step(step, state)
        elif step.type == "branch":
            return await self._execute_branch_step(step, state)
        else:
            raise ValueError(f"Unknown step type: {step.type}")

    async def _execute_agent_step(
        self, step: StepDefinition, state: RunState
    ) -> dict[str, Any]:
        """Execute an agent step (LLM call)."""
        from app.llm import gateway
        tier = step.model_tier or "standard"
        resp = await gateway.complete(
            prompt=step.description or f"Process step {step.name} for agent {step.agent}",
            tier=tier,
            run_id=state.get("run_id"),
            agent_id=step.agent,
        )
        state["total_tokens"] = state.get("total_tokens", 0) + resp.total_tokens
        state["total_cost_usd"] = round(state.get("total_cost_usd", 0.0) + resp.cost_usd, 6)

        try:
            from app.audit import ledger
            ledger.append(
                event_type="decision",
                action=f"agent_step_{step.name}",
                run_id=state.get("run_id"),
                agent_id=step.agent,
                reasoning=resp.content,
                confidence=0.92,
                model_used=resp.model,
                tokens_used=resp.total_tokens,
            )
        except Exception:
            pass

        return {
            "agent": step.agent,
            "model_tier": tier,
            "status": "completed",
            "output": resp.content,
            "tokens": resp.total_tokens,
            "cost_usd": resp.cost_usd,
        }

    async def _execute_approval_step(
        self, step: StepDefinition, state: RunState
    ) -> dict[str, Any]:
        """EPIC-07-T07: Approval node with interrupt."""
        autonomy = AutonomyLevel(state.get("autonomy", "supervised"))

        if autonomy == AutonomyLevel.AUTONOMOUS:
            return {"auto_approved": True, "reason": "Autonomous mode"}

        approval_id = str(uuid.uuid4())
        try:
            from app.policy import approval_engine
            appr = approval_engine.create_request(
                run_id=state.get("run_id", ""),
                task_id=step.name,
                title=f"Approval needed: {step.name}",
                description=step.description,
                risk_level=step.risk_level or "medium",
                approval_type=step.approval_type or "approval",
            )
            approval_id = appr.id
        except Exception:
            pass

        return {
            "approval_needed": True,
            "approval_id": approval_id,
            "approval_type": step.approval_type,
            "risk_level": step.risk_level,
            "step_name": step.name,
            "description": step.description,
        }

    async def _execute_connector_step(
        self, step: StepDefinition, state: RunState
    ) -> dict[str, Any]:
        """Execute a connector operation."""
        from app.connectors.registry import registry
        connector_id = step.connector or ""
        operation = step.operation or ""
        payload = state.get("input_data", {})
        result = await registry.execute(connector_id, operation, payload)

        try:
            from app.audit import ledger
            ledger.append(
                event_type="connector_call",
                action=f"{connector_id}.{operation}",
                run_id=state.get("run_id"),
                payload=payload,
            )
        except Exception:
            pass

        return {
            "connector": connector_id,
            "operation": operation,
            "status": "completed" if result.success else "failed",
            "data": result.data,
            "error": result.error,
        }

    async def _execute_parallel_step(
        self, step: StepDefinition, state: RunState
    ) -> dict[str, Any]:
        """EPIC-07-T06: Parallel fan-out."""
        if not step.parallel_steps:
            return {"status": "skipped", "reason": "No parallel steps defined"}

        tasks = [self._execute_step(ps, state) for ps in step.parallel_steps]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        outputs = {}
        for ps, result in zip(step.parallel_steps, results):
            if isinstance(result, Exception):
                outputs[ps.name] = {"status": "failed", "error": str(result)}
            else:
                outputs[ps.name] = result

        return {"parallel_results": outputs, "status": "completed"}

    async def _execute_branch_step(
        self, step: StepDefinition, state: RunState
    ) -> dict[str, Any]:
        """EPIC-07-T08: Branch/conditional routing."""
        if step.when and step.branches:
            try:
                # Safe evaluation of condition
                condition_result = eval(step.when, {"__builtins__": {}}, state.get("output_data", {}))  # noqa: S307
                if condition_result and step.branches:
                    return await self._execute_step(step.branches[0], state)
                elif len(step.branches) > 1:
                    return await self._execute_step(step.branches[1], state)
            except Exception as e:
                logger.warning("branch_eval_error", condition=step.when, error=str(e))

        return {"status": "skipped", "reason": "No matching branch"}

    def _save_checkpoint(self, state: RunState) -> None:
        """EPIC-07-T12: Save state checkpoint for Decision Replay."""
        run_id = state.get("run_id", "")
        checkpoint_id = str(uuid.uuid4())
        state["checkpoint_id"] = checkpoint_id

        if run_id not in self._checkpoints:
            self._checkpoints[run_id] = []
        self._checkpoints[run_id].append(dict(state))

    def get_checkpoints(self, run_id: str) -> list[RunState]:
        """EPIC-07-T12: Retrieve checkpoints for Decision Replay."""
        return self._checkpoints.get(run_id, [])


# Singleton
executor = WorkflowExecutor()
