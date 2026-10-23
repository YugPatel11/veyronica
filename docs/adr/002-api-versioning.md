# ADR-002: API Versioning via URL Path Prefix

**Date:** 2026-10-23 · **Status:** Accepted

## Context

project.md §16 defines API endpoints without versioning. As NEXUS moves to production, breaking API changes will affect the frontend and any external consumers (Telegram webhook, future integrations).

## Decision

- All API endpoints use the prefix `/api/v1/`.
- Version is in the URL path (not headers or query params) for simplicity and cache-friendliness.
- When a breaking change is needed, `/api/v2/` routes are added alongside `/api/v1/` with deprecation headers.
- FastAPI `APIRouter` with prefix handles routing.

## Consequences

- Frontend API client uses a `BASE_URL` constant including `/api/v1`.
- Webhook callbacks from external systems (Telegram) use versioned URLs.
- Old versions can coexist for a deprecation period.
- Minor overhead in router configuration, but prevents painful migrations later.
