# ADR-005: SSE Direct to Backend, Not via Vercel

**Date:** 2026-10-23 · **Status:** Accepted

## Context

project.md §11.1 correctly identifies that Vercel does not support long-lived connections (SSE/WebSocket). The frontend is hosted on Vercel but needs real-time event streaming from the backend.

## Decision

- Frontend SSE connections go **directly to the backend host** (not through Vercel).
- Backend exposes `GET /api/v1/stream/events` with SSE (text/event-stream).
- Authentication via a short-lived token (60s TTL) passed as a query parameter: `/stream/events?token=<jwt>`.
- CORS configured explicitly to allow the Vercel frontend origin.
- Client-side `useNexusEvents` hook handles reconnection with exponential backoff.

## Consequences

- Frontend needs to know the backend host URL (separate from the Vercel URL). This is set via `NEXT_PUBLIC_API_URL` environment variable.
- The short-lived token prevents token leakage in server logs (URLs are logged) — the token is valid for 60 seconds, just enough to establish the connection.
- CORS must be carefully configured; only the exact frontend origin is allowed.
- Backend must handle potentially thousands of concurrent SSE connections. Connection limits and heartbeat timeouts (30s) prevent resource exhaustion.
