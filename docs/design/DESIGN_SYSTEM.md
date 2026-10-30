# Nexus Design System Documentation

**Version:** 2.0  
**Design Direction:** High-Density Academic Mission Control  
**Theme:** Premium Dark Slate with Electric Cyan & Indigo Accents  
**Typography:** Inter (Sans), JetBrains Mono (Monospace)  

---

## 1. Visual Foundation & Design Tokens

Nexus uses Tailwind CSS v4 with custom HSL CSS variables configured in `frontend/app/globals.css`.

### 1.1 Color Tokens

| Token | HSL Value | Hex Approx | Usage |
|:---|:---|:---:|:---|
| `--background` | `222 47% 11%` | `#0B1120` | Root application background |
| `--card` | `217 33% 17%` | `#1E293B` | Surface cards, dialogs, drawers |
| `--primary` | `199 89% 48%` | `#0284C7` | Key CTAs, active selections, focus rings |
| `--success` | `142 76% 36%` | `#16A34A` | Completed runs, valid hash chains |
| `--warning` | `38 92% 50%` | `#F59E0B` | Pending approvals, borderline confidence |
| `--destructive` | `0 84% 60%` | `#EF4444` | High risk alerts, errors, account lockouts |
| `--border` | `217 33% 22%` | `#24324A` | Card borders, dividers, table headers |

---

## 2. Typography

We pair **Inter** for readable numerical data and interface labels with **JetBrains Mono** for transaction hashes, correlation IDs, and code blocks.

- **Headings:** `text-2xl font-bold tracking-tight text-white`
- **Subheadings:** `text-sm font-medium text-slate-400`
- **Body:** `text-sm leading-relaxed text-slate-200`
- **Captions & Metadata:** `text-xs font-mono text-slate-400`

---

## 3. Core Component Catalog

### 3.1 Button (`components/ui/button.tsx`)
Supports 6 distinct variants and 4 sizes:
- `variant="primary"` — Electric blue filled CTA
- `variant="secondary"` — Slate outline for secondary options
- `variant="outline"` — Subtle border for utility actions
- `variant="danger"` — Crimson button for destructive actions
- `variant="ghost"` — Borderless hover highlight
- `variant="link"` — Underlined text button

### 3.2 Status Badge (`components/ui/status-badge.tsx`)
Real-time status chip with subtle glow animation:
- `COMPLETED` / `ACTIVE` — Emerald green with pulsing indicator
- `PENDING` / `IN_PROGRESS` — Amber yellow
- `FAILED` / `REJECTED` — Crimson red with alert icon

### 3.3 Confirmation Card (`components/copilot/ConfirmationCard.tsx`)
Two-phase approval UI for state-changing operations:
- Displays proposed operation name, target resource, and risk badge
- Renders JSON parameter preview and expiration countdown (5m TTL)
- Requires explicit user action before executing mutations

### 3.4 Response Renderer (`components/copilot/ResponseRenderer.tsx`)
Multi-modal conversational output component:
- Auto-formats SQL analytics queries into dark-themed scrollable data tables
- Renders KPI metrics and summary cards with chart containers

### 3.5 AppShell & Navigation (`components/shell/`)
- **`Sidebar.tsx`:** Role-aware collapsible sidebar with grouped navigation
- **`CommandPalette.tsx`:** Global Ctrl+K spotlight search across pages, runs, and approvals
- **`CopilotSheet.tsx`:** Universal slide-over conversational copilot available on every screen
- **`Breadcrumbs.tsx`:** Dynamic hierarchy location path

---

## 4. Chart & Data Visualization Theme (`lib/chart-theme.ts`)

Recharts visualizations match our dark mission-control palette:
- `stroke="#0284C7"` for primary time-series curves
- `stroke="#10B981"` for completion rate curves
- `stroke="#F59E0B"` for warning/error threshold lines
- Background grids use semi-transparent `rgba(255, 255, 255, 0.05)`
- Tooltips render with glassmorphism `bg-slate-950/80 backdrop-blur-md`

---

## 5. Accessibility (WCAG 2.2 AA)

All components adhere to accessibility standards:
- **Contrast Ratios:** Text-to-background contrast exceeds 4.5:1 (AA requirement)
- **Keyboard Navigation:** Tab order is linear; `Escape` key closes sheets, dialogs, and command palettes
- **Screen Reader Support:** Interactive elements feature `aria-label`, `role`, and `aria-expanded` attributes
- **Automated Verification:** Verified continuously via `@axe-core/react` in `frontend/tests/a11y.test.tsx`

---

## 6. Storybook Documentation

Browse and interact with components in isolation:
```bash
cd frontend
npm run storybook
```
Stories are maintained in `frontend/components/stories/` covering all design system primitives.
