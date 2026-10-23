# ADR-006: Demo/Sandbox Features as Feature Flags

**Date:** 2026-10-23 · **Status:** Accepted

## Context

project.md §21 describes a "Demo Plan" with pre-recorded LLM responses, seed data, chaos switches, and reset endpoints. These are invaluable for testing and staging but catastrophic if accidentally enabled in production.

## Decision

- All demo/sandbox features are gated behind **feature flags** stored as environment variables.
- Three flags control sandbox behaviour:
  - `SANDBOX_DEMO_MODE` — enables recorded LLM response replay (default: `false`)
  - `SANDBOX_CHAOS_MODE` — enables chaos switch on mock systems (default: `false`)
  - `NEXUS_ENV` — `development | staging | production` — controls which features are available
- The `make reset` command checks `NEXUS_ENV` and refuses to run if set to `production`.
- The `POST /api/v1/sandbox/reset` endpoint requires admin auth AND `NEXUS_ENV != production`.
- Feature flag checks happen at the middleware/service layer, not scattered in business logic.
- An admin-only Settings → Sandbox page provides toggle UI (hidden when `NEXUS_ENV=production`).

## Consequences

- Zero risk of demo features leaking into production (env-based + code guard).
- Sandbox features are testable in staging with the same codebase as production.
- Seed data scripts double as test fixtures, reducing maintenance burden.
- Recorded LLM responses become "golden" test fixtures for the evaluation suite.
