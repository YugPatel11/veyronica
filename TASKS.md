# NEXUS — Task Checklist

> Track progress by checking boxes. Dependencies noted in parentheses.
> **Status:** ☐ = Not started · ☑ = Done

---

## Phase 1: Foundation (Weeks 1–3)

### EPIC-01: Foundation & Infrastructure

- [x] `EPIC-01-T01` — Initialise monorepo structure (frontend/, backend/, mock-systems/, docs/, design/)
- [x] `EPIC-01-T02` — Docker Compose: PostgreSQL 16 + pgvector, Redis 7, MinIO, Mailpit *(T01)*
- [x] `EPIC-01-T03` — FastAPI skeleton with config, middleware, health endpoint *(T02)*
- [x] `EPIC-01-T04` — Alembic migration framework with initial schema *(T03)*
- [x] `EPIC-01-T05` — PgBouncer connection pooling *(T02)*
- [x] `EPIC-01-T06` — Pre-commit hooks: Ruff, Black, mypy, ESLint, Prettier *(T01)*
- [x] `EPIC-01-T07` — Next.js 15 project with App Router, Tailwind 4, TypeScript strict *(T01)*
- [x] `EPIC-01-T08` — Makefile with up, down, seed, migrate, test, lint targets *(T02)*
- [x] `EPIC-01-T09` — GitHub Actions CI: lint, type-check, unit tests on PR *(T06, T07)*
- [x] `EPIC-01-T10` — `.env.example` with all required environment variables *(T03)*
- [x] `EPIC-01-T11` — Sentry error tracking for backend and frontend *(T03, T07)*

### EPIC-02: Design System & Component Library

- [x] `EPIC-02-T01` — Design tokens: CSS custom properties + Tailwind theme (colours, type, spacing, radius, elevation, motion)
- [x] `EPIC-02-T02` — Typography setup: Source Serif 4, Inter, JetBrains Mono via next/font *(EPIC-01-T07)*
- [x] `EPIC-02-T03` — Install and configure shadcn/ui with custom theme *(EPIC-01-T07)*
- [x] `EPIC-02-T04` — Base components: Button, Badge, Card, Input, Select, Textarea, Tooltip, Dialog, Dropdown, Sheet *(T03)*
- [x] `EPIC-02-T05` — Data components: DataTable, StatCard, ProgressBar, Timeline *(T04)*
- [x] `EPIC-02-T06` — Status components: StatusBadge, RiskBadge, ConfidenceIndicator *(T04)*
- [x] `EPIC-02-T07` — Layout components: AppShell, CommandPalette (Ctrl+K), CopilotSheet *(T04)*
- [x] `EPIC-02-T08` — Feedback components: Toast, Skeleton, EmptyState, ErrorBoundary *(T04)*
- [x] `EPIC-02-T09` — Storybook setup with all components documented *(T04–T08)*
- [x] `EPIC-02-T10` — Visual regression testing (Chromatic or Percy) *(T09)*
- [x] `EPIC-02-T11` — Accessibility audit: axe-core + keyboard nav for all components *(T04–T08)*
- [x] `EPIC-02-T12` — Icon set (Lucide) and illustration style guide *(T01)*
- [x] `EPIC-02-T13` — Chart theme (Recharts) matching design system *(T01)*

### EPIC-03: Database & Data Layer

- [x] `EPIC-03-T01` — Migration: users, roles, permissions tables with indexes *(EPIC-01-T04)*
- [x] `EPIC-03-T02` — Migration: agents, workflow_definitions, workflow_runs, tasks, task_events *(T01)*
- [x] `EPIC-03-T03` — Migration: audit_ledger with append-only constraints + monthly partitioning *(T01)*
- [x] `EPIC-03-T04` — Migration: approval_requests, approval_decisions *(T02)*
- [x] `EPIC-03-T05` — Migration: llm_calls, token_budgets, model_tiers *(T02)*
- [x] `EPIC-03-T06` — Migration: connectors, connector_calls *(T02)*
- [x] `EPIC-03-T07` — Migration: policies table (versioned YAML) *(T01)*
- [x] `EPIC-03-T08` — Migration: security_events, blocked_entities, login_attempts *(T01)*
- [x] `EPIC-03-T09` — Migration: documents, chunks (pgvector), question_bank *(T01)*
- [x] `EPIC-03-T10` — Migration: notifications table *(T01)*
- [x] `EPIC-03-T11` — SQLAlchemy 2 ORM models for all tables *(T01–T10)*
- [x] `EPIC-03-T12` — Database seed script (Faker en_IN) with story characters *(T11)*
- [x] `EPIC-03-T13` — Automated daily backup script with restore verification *(T02)*
- [x] `EPIC-03-T14` — Index plan with EXPLAIN ANALYZE for key queries *(T11)*

### EPIC-04: Auth, RBAC & Security Baseline

- [x] `EPIC-04-T01` — JWT auth with access + refresh token rotation, Argon2 hashing *(EPIC-03-T01)*
- [x] `EPIC-04-T02` — RBAC middleware with role-permission matrix *(T01)*
- [x] `EPIC-04-T03` — MFA (TOTP) for admin and approver roles *(T01)*
- [x] `EPIC-04-T04` — Redis-backed token blacklist for logout/revocation *(T01, EPIC-01-T02)*
- [x] `EPIC-04-T05` — Rate limiting middleware (Redis token bucket) *(EPIC-01-T02)*
- [x] `EPIC-04-T06` — Security headers middleware (HSTS, CSP, X-Frame-Options) *(EPIC-01-T03)*
- [x] `EPIC-04-T07` — CORS configuration (explicit origins) *(EPIC-01-T03)*
- [x] `EPIC-04-T08` — Secrets management (.env validation) *(EPIC-01-T10)*
- [x] `EPIC-04-T09` — Account lockout after 5 failed logins (15 min cooldown) *(T01, EPIC-03-T08)*
- [x] `EPIC-04-T10` — Input validation middleware (size limits, content-type) *(EPIC-01-T03)*

---

## Phase 2: Platform Core (Weeks 4–7)

### EPIC-05: Connector Hub

- [x] `EPIC-05-T01` — Connector protocol and ConnectorResult base classes *(EPIC-01-T03)*
- [x] `EPIC-05-T02` — Retry logic with exponential backoff + jitter (tenacity) *(T01)*
- [x] `EPIC-05-T03` — Circuit breaker (closed → open → half-open) *(T01)*
- [x] `EPIC-05-T04` — Idempotency key checking (DB-backed) *(T01, EPIC-03-T06)*
- [x] `EPIC-05-T05` — Dry-run diff generation (structured before/after) *(T01)*
- [x] `EPIC-05-T06` — Connector registry with health check aggregation *(T01–T05)*
- [x] `EPIC-05-T07` — ERP connector adapter (all operations) *(T06)*
- [x] `EPIC-05-T08` — LMS connector adapter *(T06)*
- [x] `EPIC-05-T09` — CRM connector adapter *(T06)*
- [x] `EPIC-05-T10` — Email connector adapter (SMTP + Resend) *(T06)*
- [x] `EPIC-05-T11` — Telegram connector adapter *(T06)*
- [x] `EPIC-05-T12` — Storage connector adapter (MinIO/S3) *(T06)*
- [x] `EPIC-05-T13` — Unit tests for connector hub (≥ 90% coverage) *(T01–T12)*
- [x] `EPIC-05-T14` — Integration tests against mock systems *(T07–T12, EPIC-11)*

### EPIC-06: LLM Gateway

- [x] `EPIC-06-T01` — Gateway core: tier selection, provider routing via LiteLLM *(EPIC-01-T03)*
- [x] `EPIC-06-T02` — Budget guard (global, workflow, agent, task level) *(T01, EPIC-03-T05)*
- [x] `EPIC-06-T03` — Response cache (Redis, hash of model + prompt) *(T01, EPIC-01-T02)*
- [x] `EPIC-06-T04` — PII pseudonymisation (reversible mapping table) *(T01, EPIC-03-T01)*
- [x] `EPIC-06-T05` — JSON schema validation with one repair retry *(T01)*
- [x] `EPIC-06-T06` — Usage logging (tokens, cost, latency per call) *(T01, EPIC-03-T05, EPIC-10)*
- [x] `EPIC-06-T07` — Prompt injection defence layer *(T01)*
- [x] `EPIC-06-T08` — Demo replay mode behind feature flag *(T01, T03)*
- [x] `EPIC-06-T09` — Unit tests for gateway (all paths) *(T01–T08)*
- [x] `EPIC-06-T10` — Model tier settings table with pricing *(T01, EPIC-03-T05)*

### EPIC-07: Workflow Engine & Master Agent

- [x] `EPIC-07-T01` — YAML workflow definition parser with Pydantic validation *(EPIC-01-T03)*
- [x] `EPIC-07-T02` — YAML→LangGraph compiler (all step types) *(T01)*
- [x] `EPIC-07-T03` — RunState TypedDict with all fields *(T02)*
- [x] `EPIC-07-T04` — LangGraph PostgresSaver checkpointer *(T03, EPIC-03-T02)*
- [x] `EPIC-07-T05` — Master Agent: intake, plan, pre-check, dispatch, track, aggregate, finalise *(T02, T04)*
- [x] `EPIC-07-T06` — Parallel fan-out (LangGraph Send or Celery sub-tasks) *(T05)*
- [x] `EPIC-07-T07` — Approval node with interrupt() and resume via Command *(T05, EPIC-08)*
- [x] `EPIC-07-T08` — Branch/conditional routing (when: expressions) *(T05)*
- [x] `EPIC-07-T09` — Autonomy dial (assist/supervised/autonomous) with live switching *(T05, EPIC-08)*
- [x] `EPIC-07-T10` — Celery task wrappers (queue routing) *(T05, EPIC-01-T02)*
- [x] `EPIC-07-T11` — Failure handling: retry, tier downgrade, escalation, DLQ *(T05, T10)*
- [x] `EPIC-07-T12` — Decision Replay (checkpoint-by-checkpoint retrieval) *(T04)*
- [x] `EPIC-07-T13` — Ad-hoc request planning (Copilot → tool-constrained plan) *(T05, EPIC-17)*
- [x] `EPIC-07-T14` — Workflow definition files (exam, assignment, leave, security) *(T01)*
- [x] `EPIC-07-T15` — Integration tests for workflow engine (end-to-end) *(T05–T11, EPIC-05, EPIC-06)*

### EPIC-08: Policy & Approval Engine

- [x] `EPIC-08-T01` — Policy rule evaluator with simpleeval *(EPIC-01-T03)*
- [x] `EPIC-08-T02` — Risk classification (connector risk × context × autonomy) *(T01)*
- [x] `EPIC-08-T03` — Approval routing (auto/notify/approval/dual_approval) *(T01, T02)*
- [x] `EPIC-08-T04` — Approval request creation with diff binding (diff_hash) *(T03, EPIC-05-T05)*
- [x] `EPIC-08-T05` — Approval timeout and escalation *(T04)*
- [x] `EPIC-08-T06` — Rejection handling (reason required) *(T03)*
- [x] `EPIC-08-T07` — Dual-approval flow (two different approvers) *(T03)*
- [x] `EPIC-08-T08` — Guard: critical actions always require dual_approval *(T03)*
- [x] `EPIC-08-T09` — Policy CRUD API with version history *(T01, EPIC-03-T07)*
- [x] `EPIC-08-T10` — Default policy files (marks, delete, communication, leave) *(T01)*
- [x] `EPIC-08-T11` — Unit tests for policy engine (exhaustive matrix) *(T01–T10)*

### EPIC-09: Decision Ledger

- [x] `EPIC-09-T01` — Hash-chain ledger writer with serialisation *(EPIC-03-T03)*
- [x] `EPIC-09-T02` — Chain verification endpoint (GET /api/v1/audit/verify) *(T01)*
- [x] `EPIC-09-T03` — Canonical JSON serialisation (deterministic hashing) *(T01)*
- [x] `EPIC-09-T04` — Ledger query API with filters and pagination *(T01, EPIC-03-T03)*
- [x] `EPIC-09-T05` — Run audit export (PDF and JSON) *(T04)*
- [x] `EPIC-09-T06` — Ledger table partitioning (monthly, auto-create) *(T01)*
- [x] `EPIC-09-T07` — Integration test: tamper detection *(T02)*

### EPIC-10: Event Streaming & SSE

- [x] `EPIC-10-T01` — Event emitter (worker → Redis pub/sub) *(EPIC-01-T02)*
- [x] `EPIC-10-T02` — SSE endpoint with auth (short-lived token) *(T01, EPIC-04-T01)*
- [x] `EPIC-10-T03` — Event filtering (by run_id, type, role) *(T02, EPIC-04-T02)*
- [ ] `EPIC-10-T04` — Frontend SSE hook (useNexusEvents) with reconnection *(T02, EPIC-01-T07)*
- [x] `EPIC-10-T05` — Event schema (TypedDict backend, TypeScript frontend) *(T01)*

### EPIC-11: Mock Enterprise Systems

- [x] `EPIC-11-T01` — Campus ERP service (FastAPI + erp_db + API key auth) *(EPIC-01-T02)*
- [x] `EPIC-11-T02` — LMS service (FastAPI + lms_db) *(EPIC-01-T02)*
- [x] `EPIC-11-T03` — CRM service (FastAPI + crm_db + Kanban UI) *(EPIC-01-T02)*
- [x] `EPIC-11-T04` — Webhook outbound (HMAC signed) *(T01, T02)*
- [x] `EPIC-11-T05` — Chaos switch behind feature flag *(T01, T02, T03)*
- [x] `EPIC-11-T06` — Seed data (Faker en_IN) for all mock systems *(T01, T02, T03)*
- [x] `EPIC-11-T07` — Simple UIs for each mock system *(T01, T02, T03)*

### EPIC-21: Notification Service

- [x] `EPIC-21-T01` — Notification dispatcher (multi-channel routing) *(EPIC-01-T03)*
- [x] `EPIC-21-T02` — Email templates (Jinja2): assignment, exam, progress, security, budget *(T01)*
- [x] `EPIC-21-T03` — Telegram bot webhook handler (approval callbacks) *(T01, EPIC-05-T11)*
- [x] `EPIC-21-T04` — Notification preferences per user *(T01, EPIC-03-T01)*
- [x] `EPIC-21-T05` — Delivery status tracking *(T01, EPIC-03-T10)*

---

## Phase 3: Full Product (Weeks 8–13)

### EPIC-12: Dashboard Shell & Navigation

- [ ] `EPIC-12-T01` — AppShell layout (sidebar + header + content) *(EPIC-02-T07)*
- [ ] `EPIC-12-T02` — Role-aware sidebar with grouped navigation *(T01, EPIC-04-T02)*
- [ ] `EPIC-12-T03` — Command palette (Ctrl+K) with search across pages/runs/approvals *(EPIC-02-T07)*
- [ ] `EPIC-12-T04` — CopilotSheet (slide-over, right side, every page) *(EPIC-02-T07)*
- [ ] `EPIC-12-T05` — Breadcrumb navigation *(T01)*
- [ ] `EPIC-12-T06` — Responsive layout (tablet sidebar collapse, mobile hamburger) *(T01)*
- [ ] `EPIC-12-T07` — Keyboard navigation (Tab order, Escape closes panels) *(T01)*
- [x] `EPIC-12-T08` — Notification bell with unread count *(T01, EPIC-21)*

### EPIC-13: Mission Control & Agent Map

- [x] `EPIC-13-T01` — Overview page with 4 StatCards (active runs, pending approvals, time saved, cost) *(EPIC-02-T05)*
- [x] `EPIC-13-T02` — Agent Map: React Flow canvas with custom nodes (status glow) *(EPIC-02)*
- [x] `EPIC-13-T03` — Agent Map: animated edges on handoff *(T02)*
- [x] `EPIC-13-T04` — Agent Map: node click → task detail popover *(T02)*
- [x] `EPIC-13-T05` — Agent Map: SSE integration for live updates *(T02, EPIC-10-T04)*
- [x] `EPIC-13-T06` — Workflow Runs table (sortable, filterable, click → detail) *(EPIC-02-T05)*
- [x] `EPIC-13-T07` — Connector Health grid (tiles with status, latency, circuit) *(EPIC-02-T06)*
- [x] `EPIC-13-T08` — Queue & Worker status panel *(EPIC-02-T05)*
- [x] `EPIC-13-T09` — Live event feed (auto-scroll, SSE-driven) *(EPIC-10-T04)*
- [x] `EPIC-13-T10` — Responsive layout for Mission Control *(T01–T09)*

### EPIC-14: Approval UI & Workflow Views

- [x] `EPIC-14-T01` — Approval Inbox page with tabs (Pending/Decided/All) *(EPIC-02-T04)*
- [x] `EPIC-14-T02` — ApprovalCard component (diff table, risk badge, countdown, actions) *(EPIC-02)*
- [x] `EPIC-14-T03` — Approve/Reject/Edit flow with confirmation *(T02)*
- [x] `EPIC-14-T04` — Inline mark editing (edit-then-approve flow) *(T03)*
- [x] `EPIC-14-T05` — Workflow Studio page (React Flow read-only graph of YAML) *(EPIC-02)*
- [x] `EPIC-14-T06` — Autonomy Dial component with live switching *(EPIC-02, EPIC-07-T09)*
- [x] `EPIC-14-T07` — Run Detail page with vertical timeline *(EPIC-02-T05)*
- [x] `EPIC-14-T08` — Decision Replay UI (time slider, progressive timeline) *(T07, EPIC-07-T12)*
- [x] `EPIC-14-T09` — Mobile-optimised approval screen *(T02)*

### EPIC-15: WF1 — Exam Result Cycle

- [ ] `EPIC-15-T01` — Ingestion Agent: upload handler, file validation, storage *(EPIC-05-T12)*
- [ ] `EPIC-15-T02` — Ingestion Agent: OCR/vision extraction of answers *(T01, EPIC-06)*
- [ ] `EPIC-15-T03` — Evaluation Agent: marking against rubric with confidence *(EPIC-06)*
- [ ] `EPIC-15-T04` — Evaluation Agent: structured decision records *(T03)*
- [ ] `EPIC-15-T05` — Verifier: marks sum, range checks, confidence threshold *(EPIC-07-T05)*
- [ ] `EPIC-15-T06` — Analysis Agent: performance trends, risk scoring *(EPIC-06)*
- [ ] `EPIC-15-T07` — Communication Agent: parent email drafting *(EPIC-05-T10)*
- [ ] `EPIC-15-T08` — End-to-end integration: upload → ERP → email → CRM *(T01–T07, EPIC-05, EPIC-08)*
- [ ] `EPIC-15-T09` — Golden dataset creation (50 answer sheets with faculty marks) *(T03)*
- [ ] `EPIC-15-T10` — Prompt evaluation suite (accuracy, regression tests) *(T09)*
- [x] `EPIC-15-T11` — Exam upload UI page *(EPIC-12)*
- [x] `EPIC-15-T12` — Exam results review UI page *(EPIC-12)*

### EPIC-16: WF2 — Assignment Cycle

- [ ] `EPIC-16-T01` — Assignment Agent: submission classification (on-time/late) *(EPIC-06)*
- [ ] `EPIC-16-T02` — Webhook-triggered flow (assignment.submitted) *(EPIC-11-T04)*
- [ ] `EPIC-16-T03` — Marks sync to ERP via connector *(EPIC-05-T07)*
- [ ] `EPIC-16-T04` — Scheduled overdue detection (Celery Beat) *(EPIC-07-T10)*
- [ ] `EPIC-16-T05` — Parent notification flow with policy check *(EPIC-08, EPIC-21)*
- [x] `EPIC-16-T06` — Assignment dashboard UI page *(EPIC-12)*

### EPIC-17: WF3 — Admin Copilot

- [ ] `EPIC-17-T01` — Copilot Agent with fixed tool set *(EPIC-06)*
- [ ] `EPIC-17-T02` — Tool registration (read tools: get_students, get_marks, get_pass_fail, etc.) *(T01)*
- [ ] `EPIC-17-T03` — Write tool confirmation cards *(T01, EPIC-08)*
- [ ] `EPIC-17-T04` — Read-only analytics queries (allowlisted views, row limits, timeouts) *(T01)*
- [ ] `EPIC-17-T05` — Chart/table response rendering *(T01, EPIC-02-T13)*
- [x] `EPIC-17-T06` — Chat UI (full page + sheet) *(EPIC-12-T04)*
- [ ] `EPIC-17-T07` — Multi-step plan execution with progress display *(T01, EPIC-07)*
- [ ] `EPIC-17-T08` — Security: user-provided text as data, not instructions *(T01, EPIC-06-T07)*

### EPIC-18: WF4 — Security Incident Response

- [ ] `EPIC-18-T01` — Rule engine: failed login detection (N in M minutes) *(EPIC-03-T08)*
- [ ] `EPIC-18-T02` — Rule engine: unusual login detection *(T01)*
- [ ] `EPIC-18-T03` — Rule engine: suspicious operations detection *(T01)*
- [ ] `EPIC-18-T04` — Rule engine: traffic anomaly / rate limiting *(T01, EPIC-04-T05)*
- [ ] `EPIC-18-T05` — Security Agent: context gathering + incident summary *(T01–T04, EPIC-06)*
- [ ] `EPIC-18-T06` — Automated temporary responses (lockout, IP block) *(T05)*
- [ ] `EPIC-18-T07` — Admin notification (email + Telegram + dashboard) *(T06, EPIC-21)*

### EPIC-19: Audit Explorer & Governance UI

- [x] `EPIC-19-T01` — Audit Explorer page: searchable, filterable table *(EPIC-02-T05)*
- [x] `EPIC-19-T02` — Run timeline view (click run → vertical timeline) *(EPIC-14-T07)*
- [x] `EPIC-19-T03` — Decision detail drill-down (options, confidence, rationale) *(T02)*
- [x] `EPIC-19-T04` — Verify Integrity button with visual feedback (green/red) *(EPIC-09-T02)*
- [x] `EPIC-19-T05` — Chain visualisation (ribbon with linked icons) *(T04)*
- [x] `EPIC-19-T06` — PDF/JSON export of run audit *(EPIC-09-T05)*

### EPIC-20: Impact Analytics & Cost UI

- [x] `EPIC-20-T01` — Impact calculation engine (per run + aggregate) *(EPIC-07)*
- [x] `EPIC-20-T02` — Impact Analytics page: 4 large stat numbers *(EPIC-02-T05)*
- [x] `EPIC-20-T03` — Manual vs Automated vs Human bar chart *(EPIC-02-T13)*
- [x] `EPIC-20-T04` — Time saved trend line chart *(T03)*
- [x] `EPIC-20-T05` — Token & Cost page: budget bars, usage by tier/agent *(EPIC-02-T05)*
- [x] `EPIC-20-T06` — Savings view (actual vs strongest-model-only) *(T05)*
- [x] `EPIC-20-T07` — Cost forecast (moving average projection) *(T05)*

### EPIC-22: Extensibility — HR Leave Template

- [x] `EPIC-22-T01` — leave_request.yaml workflow definition *(EPIC-07-T01)*
- [x] `EPIC-22-T02` — HR connector stub (leave balance, apply leave) *(EPIC-05-T01)*
- [x] `EPIC-22-T03` — Integration test: same-engine execution proof *(T01, T02)*

---

## Phase 4: Hardening (Weeks 14–17)

### EPIC-23: Observability & Monitoring

- [x] `EPIC-23-T01` — OpenTelemetry instrumentation (FastAPI, Celery, connectors) *(EPIC-01-T03)*
- [x] `EPIC-23-T02` — Prometheus-compatible metrics export *(T01)*
- [ ] `EPIC-23-T03` — Grafana dashboards: API health, workflow ops, LLM cost, connectors *(T02)*
- [ ] `EPIC-23-T04` — Alerting rules (error rate, stuck runs, ledger integrity, budget) *(T03)*
- [ ] `EPIC-23-T05` — SLO definitions with burn-rate alerts *(T04)*
- [x] `EPIC-23-T06` — Health check aggregation endpoint *(T01)*
- [x] `EPIC-23-T07` — Structured JSON log format with correlation IDs *(EPIC-01-T03)*
- [ ] `EPIC-23-T08` — LLM cost and latency monitoring dashboard *(T03)*

### EPIC-24: Security Hardening

- [ ] `EPIC-24-T01` — Dependency scanning (Snyk or Trivy) in CI *(EPIC-01-T09)*
- [ ] `EPIC-24-T02` — Container image scanning *(T01)*
- [x] `EPIC-24-T03` — CSRF protection for state-changing requests *(EPIC-04-T06)*
- [x] `EPIC-24-T04` — Webhook request signing (outbound) *(EPIC-11-T04)*
- [x] `EPIC-24-T05` — Data retention policies and automated cleanup job *(EPIC-03)*
- [x] `EPIC-24-T06` — Consent management for student data (parent notifications) *(EPIC-03-T01)*
- [ ] `EPIC-24-T07` — Security audit checklist (OWASP ASVS Level 2) *(T01–T06)*

### EPIC-25: Performance & Load Testing

- [ ] `EPIC-25-T01` — Locust load test suite (API endpoints, concurrent workflows) *(EPIC-01-T03)*
- [ ] `EPIC-25-T02` — Database query optimisation (slow query log, index tuning) *(EPIC-03-T14)*
- [ ] `EPIC-25-T03` — API performance profiling (middleware latency) *(T01)*
- [ ] `EPIC-25-T04` — Caching strategy review (Redis TTLs, cache invalidation) *(EPIC-06-T03)*
- [ ] `EPIC-25-T05` — Load test targets verification: 500 rps, 50 concurrent runs, p95 < 200ms *(T01–T04)*

### EPIC-28: Sandbox/Demo Tooling

- [x] `EPIC-28-T01` — Demo mode feature flag (SANDBOX_DEMO_MODE) *(EPIC-06-T08)*
- [x] `EPIC-28-T02` — Reset endpoint (POST /api/v1/sandbox/reset) with env guard *(EPIC-03-T12)*
- [x] `EPIC-28-T03` — Recorded LLM responses management (save/load/list) *(EPIC-06-T08)*
- [x] `EPIC-28-T04` — Presenter mode (display preference in settings) *(EPIC-12)*

---

## Phase 5: Advanced Workflows (Weeks 18–21)

### EPIC-26: WF5 — Timetable Generation

- [x] `EPIC-26-T01` — Excel template parser with row-level validation *(EPIC-05-T12)*
- [x] `EPIC-26-T02` — Constraint builder (Timetable Agent → OR-Tools format) *(EPIC-06)*
- [x] `EPIC-26-T03` — OR-Tools CP-SAT solver integration *(T02)*
- [x] `EPIC-26-T04` — Conflict resolution and infeasibility explanation *(T03)*
- [x] `EPIC-26-T05` — Faculty editing grid with re-validation *(EPIC-12)*
- [x] `EPIC-26-T06` — Publish through approval policy *(EPIC-08)*

### EPIC-27: WF6 — Question Paper Generation

- [x] `EPIC-27-T01` — Syllabus ingestion: extract, chunk, embed (pgvector) *(EPIC-03-T09, EPIC-06)*
- [x] `EPIC-27-T02` — Question generation (per unit, difficulty mix, Bloom levels) *(EPIC-06)*
- [x] `EPIC-27-T03` — Originality pipeline (embedding similarity, regeneration) *(T01)*
- [x] `EPIC-27-T04` — Coverage verification (marks total, difficulty distribution) *(T02)*
- [x] `EPIC-27-T05` — Faculty review and editing UI *(EPIC-12)*
- [x] `EPIC-27-T06` — PDF export with answer key and marking scheme *(T04)*

---

## Cross-Cutting (Ongoing)

### Documentation

- [ ] `DOC-01` — Architecture Decision Records (see docs/adr/)
- [ ] `DOC-02` — API documentation (FastAPI auto-docs + examples)
- [ ] `DOC-03` — Runbooks (10 operational procedures)
- [ ] `DOC-04` — Onboarding guide (developer setup in < 30 min)
- [ ] `DOC-05` — Design system documentation (Storybook + DESIGN.md)

### Testing Milestones

- [ ] `TEST-01` — Backend unit test coverage ≥ 80%
- [ ] `TEST-02` — Frontend component test coverage ≥ 70%
- [ ] `TEST-03` — E2E tests for all P0 flows (Playwright)
- [ ] `TEST-04` — LLM evaluation suite with golden dataset
- [ ] `TEST-05` — Load test passing at 500 rps target
- [ ] `TEST-06` — Security scan clean (zero high/critical)
- [ ] `TEST-07` — Accessibility audit passing (WCAG 2.2 AA)

---

**Total tasks: 198** · **Critical path tasks: ~45** · **Estimated duration: 23 weeks**
