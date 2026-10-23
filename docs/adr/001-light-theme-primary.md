# ADR-001: Light Theme as Primary with Warm Oat Canvas

**Date:** 2026-10-23 · **Status:** Accepted

## Context

project.md §17.3 originally specified "dark theme with one accent colour." The user request explicitly overrides this, requiring a **light theme as primary** with a warm oat/cream palette — not pure white (#FFF) and not cold grey.

Most enterprise/institutional users work in well-lit offices where dark themes cause more eye strain than light themes. The "Editorial Mission Control" visual concept calls for a papery, authoritative look that works better on light backgrounds.

## Decision

- **Light theme is the primary and only theme in v1.**
- Page background: oat `#F2EEE5` (warm, not white).
- Card surfaces: cream `#FBF9F4` (slightly lighter than canvas for depth).
- Dark theme planned for Phase 4+ via semantic token remap only.
- Design tokens structured in 3 layers (global → semantic → component) to make dark theme a simple swap.

## Consequences

- All contrast ratios verified against light backgrounds (all pass WCAG AA).
- Dark-theme-first design patterns from project.md must be reworked.
- Shadows use warm ink-based opacity instead of cold black.
- Status colours optimised for light background visibility.
