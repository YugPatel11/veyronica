# NEXUS — Agentic Workflow Intelligence Platform

> **Status:** Phase 0 (Foundation) · **Branch:** `phase-0/foundation`

## Quick Start

```bash
# 1. Clone and configure
cp .env.example .env
# Edit .env with your values

# 2. Start all services
make up

# 3. Run migrations
make migrate

# 4. Seed development data
make seed

# 5. Open dashboard
# Frontend: http://localhost:3000
# API docs: http://localhost:8000/docs
# Mailpit:  http://localhost:8025
# MinIO:    http://localhost:9001
```

## Project Structure

```
nexus/
├── frontend/          # Next.js 15 (App Router, Tailwind, shadcn/ui)
├── backend/           # FastAPI + Celery + LangGraph
├── mock-systems/      # Standalone ERP, LMS, CRM services
├── design/            # Design tokens, themes, mockups
├── docs/              # ADRs, runbooks, API docs
├── infra/             # Docker, Caddy, deploy scripts
├── .github/           # CI/CD workflows
├── docker-compose.yml # Local development orchestration
├── Makefile           # Developer commands
└── .env.example       # Environment template
```

## Make Commands

| Command | Description |
|---------|-------------|
| `make up` | Start all services |
| `make down` | Stop all services |
| `make migrate` | Run database migrations |
| `make seed` | Seed development data |
| `make test` | Run all tests |
| `make lint` | Run linters and type checks |
| `make logs` | Tail service logs |

## Documentation

- [PLAN.md](PLAN.md) — Development plan
- [DESIGN.md](DESIGN.md) — Design system
- [TASKS.md](TASKS.md) — Task checklist
- [docs/adr/](docs/adr/) — Architecture Decision Records
