# ADR-009: shadcn/ui with Deep Custom Theming

**Date:** 2026-10-23 · **Status:** Accepted

## Context

The frontend needs a component library that is accessible, composable, and fully customisable. The "Editorial Mission Control" design system requires deep theming — not just accent colour changes but completely custom colour palettes, typography, and component styling that would be impossible with opinionated libraries like MUI or Ant Design.

## Decision

- Use **shadcn/ui** as the component primitive layer (built on Radix UI).
- shadcn/ui components are **copied into the project** (not imported from node_modules), giving full control over styling and behaviour.
- Override all default colours, typography, border radius, and shadows via CSS custom properties defined in `design/tokens.css`.
- Tailwind configuration extends the theme with token references (`var(--color-primary)`) rather than hard-coded values.
- Every shadcn component is re-exported through a `components/ui/` barrel with project-specific defaults.
- Custom components (StatusBadge, ApprovalCard, AgentMapNode) are built on top of shadcn primitives.

## Consequences

- Full design control — the UI looks nothing like "default shadcn" while retaining its accessibility guarantees (Radix).
- Component code lives in the project — maintainable but means manual updates when shadcn releases breaking changes (rare).
- Storybook documents every component with its themed variants.
- The 3-layer token architecture (global → semantic → component) makes dark theme a simple CSS remap.
- Developers use Tailwind utilities referencing semantic tokens, never raw colour values.
