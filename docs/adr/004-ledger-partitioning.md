# ADR-004: Hash-Chained Ledger with Partitioned Table

**Date:** 2026-10-23 · **Status:** Accepted

## Context

project.md §10 specifies a hash-chained audit ledger using SHA-256. The production concern is that a single append-only table with advisory locks becomes a throughput bottleneck under high concurrency, and will grow without bound.

## Decision

- Keep the hash-chain design (each entry's hash = SHA-256(prev_hash + canonical_json(payload))).
- Use **monthly partitioning** (`PARTITION BY RANGE (ts)`) for the ledger table. New partitions are created automatically by a scheduled job.
- Serialise appends using `pg_advisory_xact_lock` on a fixed lock ID. For higher throughput, migrate to a sequence counter table with `SELECT ... FOR UPDATE`.
- `REVOKE UPDATE, DELETE` on the ledger table from the application database role.
- Verification queries use `ORDER BY seq` within partition boundaries for performance.
- Store numeric values as strings or integers (not floats) to ensure deterministic hash recomputation.

## Consequences

- Monthly partitions allow old data to be archived or moved to cold storage.
- Partition pruning makes filtered queries (by date range) efficient.
- The advisory lock creates a serial bottleneck — acceptable for expected throughput (< 100 appends/second). The sequence counter alternative is documented for scale-up.
- Chain verification must process partitions in order across boundaries.
- A separate database role (`ledger_writer`) is recommended for the ledger, with the app role having only INSERT and SELECT.
