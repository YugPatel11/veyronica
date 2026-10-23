# =============================================================================
# NEXUS — Makefile
# Developer commands for local development
# =============================================================================

.PHONY: up down logs migrate seed test lint fmt type-check clean help

# Default target
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Docker ───────────────────────────────────────────────────────────────────

up: ## Start all services (detached)
	docker compose up -d --build
	@echo ""
	@echo "✓ NEXUS is running"
	@echo "  API:     http://localhost:8000/docs"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Mailpit:  http://localhost:8025"
	@echo "  MinIO:    http://localhost:9001"

down: ## Stop all services
	docker compose down

logs: ## Tail logs from all services
	docker compose logs -f

logs-api: ## Tail API logs only
	docker compose logs -f api

logs-worker: ## Tail Celery worker logs only
	docker compose logs -f celery-worker

restart-api: ## Restart the API server
	docker compose restart api

ps: ## Show running services
	docker compose ps

# ── Database ─────────────────────────────────────────────────────────────────

migrate: ## Run database migrations
	docker compose exec api alembic upgrade head

migrate-down: ## Rollback last migration
	docker compose exec api alembic downgrade -1

migrate-create: ## Create a new migration (usage: make migrate-create msg="add users table")
	docker compose exec api alembic revision --autogenerate -m "$(msg)"

seed: ## Seed development data
	@echo "Seed script will be implemented in EPIC-03-T12"

# ── Testing ──────────────────────────────────────────────────────────────────

test: ## Run all tests
	docker compose exec api pytest -v --tb=short

test-unit: ## Run unit tests only
	docker compose exec api pytest -v --tb=short -m unit

test-cov: ## Run tests with coverage report
	docker compose exec api pytest --cov=app --cov-report=term-missing --cov-report=html

test-local: ## Run tests locally (no Docker)
	cd backend && python -m pytest -v --tb=short -m unit

# ── Code Quality ─────────────────────────────────────────────────────────────

lint: ## Run all linters and type checks
	cd backend && python -m ruff check .
	cd backend && python -m mypy app/
	cd frontend && npm run lint

fmt: ## Auto-format code
	cd backend && python -m ruff format .
	cd backend && python -m ruff check --fix .
	cd frontend && npx prettier --write "**/*.{ts,tsx,css,json}"

type-check: ## Run type checkers
	cd backend && python -m mypy app/
	cd frontend && npx tsc --noEmit

# ── Utilities ────────────────────────────────────────────────────────────────

clean: ## Remove build artifacts and caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	rm -rf frontend/.next frontend/node_modules/.cache

shell-api: ## Open a shell in the API container
	docker compose exec api /bin/bash

shell-db: ## Open a psql shell
	docker compose exec postgres psql -U nexus -d nexus_db
