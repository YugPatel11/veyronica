# ADR-007: Reversible PII Pseudonymisation for LLM Calls

**Date:** 2026-10-23 · **Status:** Accepted

## Context

project.md §12 describes a PII minimiser that "replaces names and emails." One-way pseudonymisation is lossy — the LLM output containing pseudonyms cannot be mapped back to real entities, making results unusable without manual fixup. India's DPDP Act 2023 also requires data minimisation in processing.

## Decision

- Implement **reversible pseudonymisation** with a secure mapping table.
- Before LLM call: scan prompt for PII patterns (names, emails, phone numbers, student IDs) and replace with deterministic pseudonyms (`P-0001`, `E-0001`).
- Mapping stored in **encrypted Redis** with a TTL matching the workflow run lifetime (max 24h).
- After LLM response: de-pseudonymise output using the mapping.
- Mapping table encrypted with a per-run key derived from the run's JWT.
- PII detection uses a combination of: known entity list (from DB), regex patterns, and optional NER model.

## Consequences

- LLM providers never see real student names or emails.
- Output is automatically restored to real values — no manual fixup needed.
- Redis TTL ensures mappings are garbage-collected after the run completes.
- Detection is imperfect — some PII may slip through if it doesn't match patterns. Regular audit of LLM call logs (with PII scan) catches leaks.
- Performance overhead is minimal (< 5ms per call for scan + replace).
