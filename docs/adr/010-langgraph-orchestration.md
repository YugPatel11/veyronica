# ADR-010: LangGraph for Agent Orchestration

**Date:** 2026-10-23 · **Status:** Accepted

## Context

project.md §8 specifies LangGraph as the agent framework. The key requirements are: durable checkpoints (crash recovery), human-in-the-loop interrupts (approval pauses), parallel fan-out, and deterministic replay for the Decision Replay feature.

## Decision

- Use **LangGraph** (v0.3+) as the agent orchestration framework.
- Each workflow compiles into a LangGraph `StateGraph` with typed state (`RunState`).
- **PostgresSaver** checkpointer for durable state persistence (crash recovery, replay).
- **`interrupt()`** for approval nodes — pauses the graph, resumes via `Command` when the API receives an approval decision.
- **`Send`** for parallel fan-out (e.g., evaluating multiple answer sheets concurrently).
- Specialist agents are LangGraph subgraphs invoked as tool calls from the Master Agent.
- LangGraph graphs run inside **Celery tasks** — Celery handles queue routing, retries, and concurrency limits. LangGraph handles the agent logic and state.

## Alternatives Considered

| Alternative | Why Not |
|-------------|---------|
| **CrewAI** | Less control over state management, no built-in checkpointing with PostgreSQL, weaker interrupt support |
| **AutoGen** | Multi-agent conversation model doesn't fit NEXUS's structured workflow model |
| **Custom state machine** | Would reinvent checkpointing, interrupts, and parallel execution |
| **Temporal.io** | Excellent workflow engine but overkill for a 4-person team; adds operational complexity |

## Consequences

- LangGraph provides checkpointing "for free" — crash recovery without custom state management code.
- Decision Replay is possible by reading checkpoint history from PostgresSaver.
- The YAML→LangGraph compiler is custom code that must be tested thoroughly (EPIC-07-T02).
- LangGraph's async execution model pairs well with FastAPI's async handlers.
- Vendor dependency on LangChain ecosystem — mitigated by the fact that LangGraph graphs are pure Python functions at the core.
