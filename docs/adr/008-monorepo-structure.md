# ADR-008: Monorepo with Separate Services

**Date:** 2026-10-23 · **Status:** Accepted

## Context

NEXUS consists of a Next.js frontend, FastAPI backend, Celery workers, and 3 mock enterprise systems. The question is whether to use a monorepo or multiple repositories.

## Decision

- Use a **single monorepo** with the following top-level directories:
  - `frontend/` — Next.js application
  - `backend/` — FastAPI API + Celery workers (shared codebase)
  - `mock-systems/` — ERP, LMS, CRM services (each a sub-directory)
  - `design/` — Design tokens, themes, mockups
  - `docs/` — ADRs, runbooks, API docs
  - `infra/` — Docker Compose files, Caddyfile, scripts
- Each service has its own `Dockerfile` and dependency file (`pyproject.toml` or `package.json`).
- Docker Compose orchestrates all services for local development.
- CI runs per-directory change detection to avoid rebuilding unchanged services.

## Consequences

- Single PR can include frontend + backend changes for a feature (atomic commits).
- Shared types/schemas (e.g., event types) can be kept in sync without publishing packages.
- CI/CD must handle selective builds — only rebuild what changed.
- Mock systems are co-located but clearly separated — easy to remove when real adapters are ready.
- Monorepo tooling (Turborepo or similar) is optional — Makefile targets sufficient for this team size.
