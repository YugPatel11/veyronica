# Architecture Decision Records (ADR)
**Nexus Autonomous Academic Operations Platform**

This directory records all high-impact architectural decisions made across the Nexus platform lifecycle. Each ADR follows the standardized Michael Nygard format (Context, Decision, Consequences, Compliance).

---

## Master ADR Index

| ADR ID | Title | Status | Date | Primary Scope |
|:---|:---|:---:|:---:|:---|
| [ADR-001](001-light-theme-primary.md) | Light Theme Primary with Dark-First Dashboard Option | Accepted | Oct 2026 | Frontend UI/UX |
| [ADR-002](002-api-versioning.md) | URL Path-Based API Versioning (`/api/v1`) | Accepted | Oct 2026 | Backend Architecture |
| [ADR-003](003-litellm-provider-agnostic.md) | LiteLLM as Provider-Agnostic Gateway with Local Fallback | Accepted | Oct 2026 | AI / Model Routing |
| [ADR-004](004-ledger-partitioning.md) | Hash-Chained Cryptographic Audit Ledger with Partitioning | Accepted | Oct 2026 | Security & Compliance |
| [ADR-005](005-sse-direct-backend.md) | Direct Backend SSE Streaming for Real-Time Event Bus | Accepted | Oct 2026 | Event Streaming |
| [ADR-006](006-demo-as-feature-flags.md) | Ephemeral Sandbox Demo Mode Governed by Feature Flags | Accepted | Oct 2026 | Reliability & Testing |
| [ADR-007](007-reversible-pseudonymisation.md) | Reversible Pseudonymisation for Student PII | Accepted | Oct 2026 | Privacy & DPDP Act |
| [ADR-008](008-monorepo-structure.md) | Monorepo Structure with Strict Boundary Enforcement | Accepted | Oct 2026 | Repository Architecture |
| [ADR-009](009-shadcn-custom-theming.md) | Tailwind CSS & Radix UI Design System Components | Accepted | Oct 2026 | Design System |
| [ADR-010](010-langgraph-orchestration.md) | State Machine Multi-Agent Orchestration with Human-in-the-Loop | Accepted | Oct 2026 | Autonomous Workflows |
| [ADR-011](011-exam-ingestion-dual-verification.md) | WF1 Exam Result Ingestion with Dual-Pass Verifier | Accepted | Oct 2026 | Academic Operations |
| [ADR-012](012-copilot-safe-write-confirmation.md) | WF3 Admin Copilot Read-Only Analytics & Confirmation Cards | Accepted | Oct 2026 | Conversational AI |
| [ADR-013](013-security-engine-automated-containment.md) | WF4 Autonomous Security Incident Response & Temporary Containment | Accepted | Oct 2026 | Security Operations |

---

## ADR Guidelines
1. Any architectural modification impacting > 1 epic requires a proposed ADR before merge.
2. Decisions must specify performance, security, and maintenance consequences.
3. Every ADR must list verification test files validating the decision in CI.
