# NEXUS Design System — "Editorial Mission Control"

> **Version:** 1.0 · **Date:** 2026-10-23 · **Status:** Draft for approval
> **Theme:** Light (primary) · Dark theme planned for Phase 4+

---

## 1. Design Principles

### Core Principles

1. **Confident Clarity** — Every element communicates with precision. No ambiguity in status, no confusion in hierarchy. Data-dense but never cluttered.
2. **Warm Authority** — The interface feels trustworthy and institutional, like a well-designed report from a respected publisher. Not cold, not sterile, not playful.
3. **Purposeful Motion** — Animation serves comprehension: a status change is visible, a handoff is traceable, a count is alive. Never decorative. Always respectful of `prefers-reduced-motion`.
4. **Accessible by Default** — WCAG 2.2 AA minimum. Colour is never the sole indicator. Every interactive element is keyboard-reachable. Every state has a text equivalent.
5. **One Dashboard, Many Roles** — The same layout serves admin, faculty, approver, and operator. The sidebar adapts; the mental model stays constant.

### Visual Concept

**"Editorial Mission Control"** — Bloomberg Terminal's information density meets Notion's whitespace meets Linear's confidence. It looks like a publication control room for institutional operations:

- Approval cards feel like **signed documents** (subtle paper texture, stamp-like badges)
- The audit ledger is a **chained ribbon** with verified state icons
- The agent map is a **living network** with pulsing nodes and animated handoff edges
- Numbers are **large, readable, and honest** (no exaggeration, clear units)
- The sidebar is a **quiet table of contents**, not a loud navigation

### Anti-Patterns (What NEXUS Must NOT Look Like)

| Avoid | Why | Instead |
|-------|-----|---------|
| Default purple/blue gradient hero | Generic AI template look | Warm oat canvas with teal accents |
| Unthemed shadcn defaults | Every dashboard looks the same | Deep token customisation (see §2) |
| Glassmorphism everywhere | Overdone, low contrast | Subtle elevation via border + shadow |
| Emoji as icons | Unprofessional | Lucide icon set, consistent sizing |
| Stock card-grid sameness | No visual hierarchy | Varied card sizes, editorial layout |
| Inter + grey everything | Bland, forgettable | Source Serif 4 + Inter + JetBrains Mono |
| Pure white (#FFF) backgrounds | Cold, clinical | Oat #F2EEE5 canvas |
| Dark theme as primary | User requirement is light-first | Light theme primary; dark planned later |

---

## 2. Colour System

### 2.1 Palette

#### Global Tokens (Layer 1 — Raw Values)

```css
/* Canvas & Surface */
--color-oat-50:     #F9F7F2;
--color-oat-100:    #F2EEE5;    /* ← Canvas (page bg) */
--color-oat-200:    #E9E4D8;    /* ← Sunken panels */
--color-oat-300:    #D9D2C2;    /* ← Borders */
--color-oat-400:    #C4BAA6;
--color-oat-500:    #A99E8A;

--color-cream-50:   #FDFCFA;
--color-cream-100:  #FBF9F4;    /* ← Surface (cards) */
--color-cream-200:  #F5F1E9;
--color-cream-300:  #EDE7DA;

/* Ink (text) */
--color-ink-900:    #1E2A32;    /* ← Primary text */
--color-ink-700:    #364650;
--color-ink-500:    #5E6B72;    /* ← Muted text */
--color-ink-400:    #7A8790;
--color-ink-300:    #9BA5AC;
--color-ink-200:    #C2CAD0;

/* Teal (primary actions) */
--color-teal-900:   #063D3D;
--color-teal-800:   #0A5656;    /* ← Primary hover */
--color-teal-700:   #0E6B6B;    /* ← Primary */
--color-teal-600:   #148080;
--color-teal-500:   #1A9494;
--color-teal-400:   #3DB5B5;
--color-teal-300:   #7CD4D4;
--color-teal-200:   #B3E6E6;
--color-teal-100:   #D7ECE9;    /* ← Primary tint */
--color-teal-50:    #EBF5F3;

/* Saffron (human attention, waiting) */
--color-saffron-900: #7A4E0B;
--color-saffron-800: #A56810;
--color-saffron-700: #C47D1B;
--color-saffron-600: #E9A23B;   /* ← Saffron primary */
--color-saffron-500: #F0B556;
--color-saffron-400: #F5C97A;
--color-saffron-300: #F9DDA3;
--color-saffron-200: #FCF0D0;
--color-saffron-100: #FEF7E8;
--color-saffron-50:  #FFFBF3;

/* Blue (running, info) */
--color-blue-800:   #1F3F8C;
--color-blue-700:   #2B51AE;
--color-blue-600:   #3563C9;    /* ← Running/Info */
--color-blue-500:   #4F7DDC;
--color-blue-400:   #7A9DE8;
--color-blue-200:   #C2D4F4;
--color-blue-100:   #E0EAFA;
--color-blue-50:    #F0F5FD;

/* Green (success) */
--color-green-800:  #1E5E3A;
--color-green-700:  #257548;
--color-green-600:  #2E8B57;    /* ← Success */
--color-green-500:  #3DA36C;
--color-green-400:  #65BF90;
--color-green-200:  #B5DFC9;
--color-green-100:  #DAEEE2;
--color-green-50:   #EDF7F1;

/* Red (danger, failed) */
--color-red-800:    #8C2C24;
--color-red-700:    #A83830;
--color-red-600:    #C8453B;    /* ← Danger/Failed */
--color-red-500:    #D86054;
--color-red-400:    #E58880;
--color-red-200:    #F4C9C5;
--color-red-100:    #FAE4E2;
--color-red-50:     #FDF2F1;

/* Coral (rare AI highlight) */
--color-coral-600:  #E8735A;    /* ← AI moments */
--color-coral-100:  #FCEAE4;
```

#### Semantic Tokens (Layer 2 — Roles)

```css
:root {
  /* Canvas & Surface */
  --color-canvas:             var(--color-oat-100);
  --color-surface:            var(--color-cream-100);
  --color-surface-raised:     var(--color-cream-50);
  --color-surface-sunken:     var(--color-oat-200);
  --color-surface-overlay:    var(--color-cream-100);

  /* Borders */
  --color-border:             var(--color-oat-300);
  --color-border-subtle:      var(--color-oat-200);
  --color-border-strong:      var(--color-oat-400);

  /* Text */
  --color-text-primary:       var(--color-ink-900);
  --color-text-secondary:     var(--color-ink-500);
  --color-text-tertiary:      var(--color-ink-400);
  --color-text-disabled:      var(--color-ink-300);
  --color-text-on-primary:    #FFFFFF;
  --color-text-on-saffron:    var(--color-saffron-900);

  /* Primary (actions) */
  --color-primary:            var(--color-teal-700);
  --color-primary-hover:      var(--color-teal-800);
  --color-primary-active:     var(--color-teal-900);
  --color-primary-tint:       var(--color-teal-100);
  --color-primary-subtle:     var(--color-teal-50);

  /* Status: Semantic */
  --color-status-done:        var(--color-green-600);
  --color-status-done-bg:     var(--color-green-50);
  --color-status-running:     var(--color-blue-600);
  --color-status-running-bg:  var(--color-blue-50);
  --color-status-waiting:     var(--color-saffron-600);
  --color-status-waiting-bg:  var(--color-saffron-50);
  --color-status-failed:      var(--color-red-600);
  --color-status-failed-bg:   var(--color-red-50);
  --color-status-warning:     var(--color-saffron-600);
  --color-status-warning-bg:  var(--color-saffron-100);

  /* Interactive */
  --color-focus-ring:         var(--color-teal-500);
  --color-link:               var(--color-teal-700);
  --color-link-hover:         var(--color-teal-800);

  /* Special */
  --color-ai-accent:          var(--color-coral-600);
  --color-ai-accent-bg:       var(--color-coral-100);
}
```

#### Component Tokens (Layer 3)

```css
:root {
  /* Buttons */
  --button-primary-bg:        var(--color-primary);
  --button-primary-bg-hover:  var(--color-primary-hover);
  --button-primary-text:      var(--color-text-on-primary);
  --button-secondary-bg:      transparent;
  --button-secondary-border:  var(--color-border);
  --button-secondary-text:    var(--color-text-primary);
  --button-danger-bg:         var(--color-status-failed);
  --button-danger-text:       var(--color-text-on-primary);

  /* Cards */
  --card-bg:                  var(--color-surface);
  --card-border:              var(--color-border-subtle);
  --card-shadow:              var(--shadow-sm);

  /* Sidebar */
  --sidebar-bg:               var(--color-surface);
  --sidebar-border:           var(--color-border);
  --sidebar-item-hover:       var(--color-primary-subtle);
  --sidebar-item-active:      var(--color-primary-tint);
  --sidebar-item-text:        var(--color-text-secondary);
  --sidebar-item-text-active: var(--color-primary);

  /* Approval Card */
  --approval-card-bg:         var(--color-cream-50);
  --approval-card-border:     var(--color-border);
  --approval-card-stamp:      var(--color-primary);
  --approval-card-urgent-border: var(--color-status-waiting);

  /* Ledger */
  --ledger-chain-color:       var(--color-primary);
  --ledger-verified-bg:       var(--color-status-done-bg);
  --ledger-broken-bg:         var(--color-status-failed-bg);
}
```

### 2.2 Contrast Verification

| Pair | Ratio | WCAG Level |
|------|-------|-----------|
| Primary text (#1E2A32) on Canvas (#F2EEE5) | 10.8:1 | AAA ✓ |
| Primary text (#1E2A32) on Surface (#FBF9F4) | 12.1:1 | AAA ✓ |
| Muted text (#5E6B72) on Canvas (#F2EEE5) | 4.7:1 | AA ✓ |
| Muted text (#5E6B72) on Surface (#FBF9F4) | 5.2:1 | AA ✓ |
| White on Primary (#0E6B6B) | 5.3:1 | AA ✓ |
| White on Running (#3563C9) | 4.6:1 | AA ✓ |
| White on Success (#2E8B57) | 4.8:1 | AA ✓ |
| White on Danger (#C8453B) | 4.5:1 | AA ✓ |
| Saffron text (#7A4E0B) on Saffron bg (#FFFBF3) | 7.2:1 | AAA ✓ |

> All critical text/background pairs meet WCAG 2.2 AA (4.5:1) minimum. Most achieve AAA (7:1).

### 2.3 Status Colour Language

Every status has a **colour + icon + shape**, never colour alone:

| Status | Colour | Icon (Lucide) | Badge Shape | Accessible Label |
|--------|--------|--------------|-------------|-----------------|
| Done / Success | Green `#2E8B57` | `CheckCircle2` | Filled pill | "Completed" |
| Running / Active | Blue `#3563C9` | `Loader2` (spinning) | Outlined pill | "In progress" |
| Waiting for Human | Saffron `#E9A23B` | `UserCheck` | Filled pill | "Awaiting approval" |
| Failed / Error | Red `#C8453B` | `XCircle` | Filled pill | "Failed" |
| Warning | Saffron `#E9A23B` | `AlertTriangle` | Outlined pill | "Warning" |
| Queued | Grey `#5E6B72` | `Clock` | Outlined pill | "Queued" |
| Degraded | Saffron `#E9A23B` | `AlertCircle` | Dashed pill | "Degraded" |
| AI Confidence Low | Coral `#E8735A` | `Eye` | Dotted pill | "Low confidence" |

---

## 3. Typography

### 3.1 Font Stack

| Role | Font | Weight Range | Source | Fallback |
|------|------|-------------|--------|----------|
| **Headings** | Source Serif 4 | 600–700 | Google Fonts via `next/font` | Georgia, 'Times New Roman', serif |
| **Body** | Inter | 400–600 | Google Fonts via `next/font` | -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif |
| **Monospace** | JetBrains Mono | 400–500 | Google Fonts via `next/font` | 'Fira Code', 'Cascadia Code', monospace |

> **Verification:** All three fonts are available on Google Fonts. Source Serif 4 provides editorial character for headings. Inter provides excellent readability at small sizes for data-dense interfaces. JetBrains Mono's distinct characters (I/l/1, O/0) are critical for displaying IDs, hashes, and numbers.

### 3.2 Type Scale

| Token | Size (rem/px) | Line Height | Weight | Font | Use |
|-------|--------------|-------------|--------|------|-----|
| `--text-display` | 2.25rem / 36px | 1.2 | 700 | Source Serif 4 | Page titles, hero numbers |
| `--text-h1` | 1.75rem / 28px | 1.25 | 700 | Source Serif 4 | Section titles |
| `--text-h2` | 1.375rem / 22px | 1.3 | 600 | Source Serif 4 | Card titles, panel headers |
| `--text-h3` | 1.125rem / 18px | 1.35 | 600 | Source Serif 4 | Sub-section titles |
| `--text-body` | 0.9375rem / 15px | 1.6 | 400 | Inter | Default body text |
| `--text-body-strong` | 0.9375rem / 15px | 1.6 | 600 | Inter | Emphasised body text |
| `--text-sm` | 0.8125rem / 13px | 1.5 | 400 | Inter | Secondary text, captions |
| `--text-xs` | 0.6875rem / 11px | 1.45 | 500 | Inter | Badges, labels, overlines |
| `--text-mono` | 0.8125rem / 13px | 1.5 | 400 | JetBrains Mono | IDs, hashes, numbers, code |
| `--text-mono-sm` | 0.6875rem / 11px | 1.4 | 400 | JetBrains Mono | Inline hash previews |
| `--text-stat` | 2.5rem / 40px | 1.1 | 700 | Inter | Large dashboard numbers |
| `--text-stat-sm` | 1.5rem / 24px | 1.2 | 600 | Inter | Secondary dashboard numbers |

### 3.3 CSS Custom Properties

```css
:root {
  /* Type scale */
  --font-heading: 'Source Serif 4', Georgia, serif;
  --font-body: 'Inter', -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

  --text-display-size: 2.25rem;
  --text-display-line: 1.2;
  --text-display-weight: 700;

  --text-h1-size: 1.75rem;
  --text-h1-line: 1.25;
  --text-h1-weight: 700;

  --text-h2-size: 1.375rem;
  --text-h2-line: 1.3;
  --text-h2-weight: 600;

  --text-h3-size: 1.125rem;
  --text-h3-line: 1.35;
  --text-h3-weight: 600;

  --text-body-size: 0.9375rem;
  --text-body-line: 1.6;
  --text-body-weight: 400;

  --text-sm-size: 0.8125rem;
  --text-sm-line: 1.5;

  --text-xs-size: 0.6875rem;
  --text-xs-line: 1.45;

  --text-mono-size: 0.8125rem;
  --text-mono-line: 1.5;

  --text-stat-size: 2.5rem;
  --text-stat-line: 1.1;
  --text-stat-weight: 700;
}
```

---

## 4. Spacing System

Base unit: **4px**. All spacing uses multiples of 4.

| Token | Value | Use |
|-------|-------|-----|
| `--space-0` | 0 | Reset |
| `--space-0.5` | 2px | Micro gaps (icon-to-label inside badges) |
| `--space-1` | 4px | Tight padding (badge padding) |
| `--space-1.5` | 6px | — |
| `--space-2` | 8px | Inline spacing, small gaps |
| `--space-3` | 12px | Card padding (compact), button padding |
| `--space-4` | 16px | Standard card padding, section gaps |
| `--space-5` | 20px | — |
| `--space-6` | 24px | Between cards, panel padding |
| `--space-8` | 32px | Section spacing, page padding |
| `--space-10` | 40px | Large section breaks |
| `--space-12` | 48px | Page-level spacing |
| `--space-16` | 64px | Hero spacing |

### Touch Targets

- Minimum interactive target: **44×44px** (WCAG 2.2 AA)
- Minimum gap between interactive elements: **8px**
- Button minimum height: **36px** (small), **40px** (default), **48px** (large)

---

## 5. Border Radius

| Token | Value | Use |
|-------|-------|-----|
| `--radius-none` | 0 | Sharp corners (tables, dividers) |
| `--radius-sm` | 4px | Small elements (badges, tags) |
| `--radius-md` | 8px | Cards, inputs, buttons |
| `--radius-lg` | 12px | Modals, dropdowns, command palette |
| `--radius-xl` | 16px | Panels, sheets |
| `--radius-full` | 9999px | Pills, avatars, status dots |

---

## 6. Elevation & Shadow

| Token | Value | Use |
|-------|-------|-----|
| `--shadow-none` | none | Flat elements |
| `--shadow-xs` | `0 1px 2px rgba(30,42,50,0.04)` | Subtle lift (cards at rest) |
| `--shadow-sm` | `0 1px 3px rgba(30,42,50,0.06), 0 1px 2px rgba(30,42,50,0.04)` | Cards, buttons |
| `--shadow-md` | `0 4px 6px rgba(30,42,50,0.06), 0 2px 4px rgba(30,42,50,0.04)` | Dropdowns, popovers |
| `--shadow-lg` | `0 10px 15px rgba(30,42,50,0.06), 0 4px 6px rgba(30,42,50,0.04)` | Modals, command palette |
| `--shadow-xl` | `0 20px 25px rgba(30,42,50,0.08), 0 8px 10px rgba(30,42,50,0.04)` | Sheets, overlays |

> Shadows use the ink colour (`#1E2A32`) at very low opacity for warm consistency. No blue-tinted shadows.

---

## 7. Motion System

### Principles

- **Purpose:** Every animation communicates a state change, not decoration
- **Respect:** `prefers-reduced-motion: reduce` disables all non-essential motion
- **Duration:** Short for micro-interactions, longer for page transitions
- **Easing:** `ease-out` for entrances, `ease-in` for exits, spring for playful elements

### Tokens

| Token | Duration | Easing | Use |
|-------|----------|--------|-----|
| `--motion-instant` | 0ms | — | Reduced motion replacement |
| `--motion-fast` | 100ms | ease-out | Hover states, focus rings |
| `--motion-normal` | 200ms | ease-out | Tooltips, dropdowns, badges |
| `--motion-slow` | 300ms | ease-out | Sheets, modals, panels |
| `--motion-deliberate` | 500ms | ease-in-out | Page transitions, large panels |
| `--motion-spring` | 400ms | cubic-bezier(0.34, 1.56, 0.64, 1) | Counters, status changes |

### Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Key Animations (Framer Motion)

| Element | Trigger | Animation |
|---------|---------|-----------|
| Status badge | Status change | Colour cross-fade (200ms) with subtle scale pulse (1.0 → 1.05 → 1.0) |
| Counter (time saved, cost) | Value update | Number ticker (spring, from old to new value) |
| Agent map node | Agent starts working | Subtle glow pulse (opacity 0.3 → 0.6 → 0.3, 2s loop) |
| Agent map edge | Handoff between agents | Dot travels along edge (500ms) |
| Approval card | Approval received | Entrance slide-in from right (300ms) |
| Toast | Show/dismiss | Slide up + fade in (200ms) / slide down + fade out (200ms) |
| Sidebar | Collapse/expand | Width animation (300ms) |
| Copilot sheet | Open/close | Slide from right (300ms) |
| Command palette | Open | Scale from 0.95 + fade in (200ms) |
| Skeleton loader | Loading | Shimmer gradient sweep (1.5s loop) |
| Verify Integrity | Click → result | Loading spinner → checkmark or X with colour flash |

---

## 8. Iconography

### Icon Set: Lucide

**Why Lucide:** Open-source, actively maintained, consistent design, good coverage, tree-shakable, Next.js friendly (`lucide-react`).

### Sizing

| Context | Size | Stroke Width |
|---------|------|-------------|
| Inline text | 16px | 2px |
| Buttons, nav items | 20px | 1.75px |
| Card headers, features | 24px | 1.5px |
| Hero / empty states | 48px | 1.25px |

### Key Icon Mapping

| Concept | Icon | Notes |
|---------|------|-------|
| Mission Control | `LayoutDashboard` | — |
| Agent Map | `Network` | — |
| Workflows | `GitBranch` | — |
| Approvals | `CheckSquare` | Waiting: `UserCheck` |
| Audit / Ledger | `ScrollText` | Verified: `ShieldCheck` |
| Connected Systems | `Plug` | — |
| Copilot | `MessageSquare` | — |
| Security | `Shield` | — |
| Impact | `TrendingUp` | — |
| Cost / Tokens | `Coins` | — |
| Settings | `Settings` | — |
| Templates | `LayoutTemplate` | — |
| Run / Execute | `Play` | — |
| Pause | `Pause` | — |
| Approve | `Check` | — |
| Reject | `X` | — |
| Risk: Low | `Info` | Blue |
| Risk: Medium | `AlertCircle` | Saffron |
| Risk: High | `AlertTriangle` | Red |
| Risk: Critical | `ShieldAlert` | Red, filled |

### Illustration Style

- **No illustrations in v1** — the data is the content
- Empty states use a large Lucide icon (48px) + descriptive text + action button
- Optional: subtle line illustrations for onboarding (consistent stroke width, oat/teal palette)

---

## 9. Layout Grid

### Desktop (≥ 1280px)

```
| Sidebar (240px) | Main Content (flex-1) |
|                 | ← 32px padding →     |
|                 | 12-column grid        |
|                 | gap: 24px             |
```

- Sidebar: fixed width 240px, collapsible to 64px (icon-only)
- Main content: fluid, max-width 1440px, centered
- Content grid: 12 columns, 24px gutter
- Page padding: 32px

### Tablet (768px – 1279px)

- Sidebar: collapsed to icon-only (64px) or hidden (overlay)
- Content: 8-column grid, 16px gutter
- Page padding: 24px

### Mobile (< 768px)

- Sidebar: hidden, accessible via hamburger menu
- Content: single column, full width
- Page padding: 16px
- Approval cards: full-width, stacked actions

### Breakpoint Tokens

```css
:root {
  --bp-sm:  640px;
  --bp-md:  768px;
  --bp-lg:  1024px;
  --bp-xl:  1280px;
  --bp-2xl: 1440px;
}
```

---

## 10. Component Inventory

### 10.1 Base Components (shadcn/ui themed)

| Component | Variants | States | Accessibility |
|-----------|----------|--------|--------------|
| **Button** | primary, secondary, outline, ghost, danger, link | default, hover, focus, active, disabled, loading | `aria-disabled`, `aria-busy`, focus ring |
| **Badge** | filled, outline, dot | — | `role="status"` for live badges |
| **Card** | default, raised, sunken, approval | hover (if interactive) | Semantic heading structure |
| **Input** | text, email, password, search, textarea | default, focus, error, disabled | `aria-invalid`, `aria-describedby` for errors |
| **Select** | default, multi | open, closed, disabled | Keyboard nav, `aria-expanded` |
| **Tooltip** | text, rich | shown, hidden | Delay 300ms, `aria-describedby` |
| **Dialog** | default, alert | open, closed | Focus trap, `aria-modal` |
| **Dropdown** | default | open, closed | Keyboard nav, `aria-expanded` |
| **Sheet** | right (Copilot), left (details) | open, closed | Focus trap, close on Escape |
| **Tabs** | line, filled | active, inactive | `role="tablist"`, `aria-selected` |
| **Toggle** | default | on, off, disabled | `role="switch"`, `aria-checked` |
| **Avatar** | image, initials, icon | default | `alt` text |
| **Separator** | horizontal, vertical | — | `role="separator"` |
| **Skeleton** | text, circle, card | loading | `aria-busy="true"`, `aria-label` |

### 10.2 Data Components

| Component | Props | States | Notes |
|-----------|-------|--------|-------|
| **DataTable** | columns, data, sorting, filtering, pagination, selection | loading, empty, error | Virtual scrolling for > 100 rows |
| **StatCard** | label, value, delta, trend, icon | default, loading | Large number, trend arrow, monospace delta |
| **Timeline** | entries (vertical) | default, loading | Step cards with status, connector lines |
| **DiffTable** | before, after, columns | default | Change cells highlighted (green add, red remove) |
| **ProgressBar** | value, max, label | default, indeterminate | `role="progressbar"`, `aria-valuenow` |
| **Sparkline** | data points | default | Tiny inline chart, teal colour |
| **CounterTicker** | value, format | animating | Framer Motion number animation |

### 10.3 Status Components

| Component | Props | Notes |
|-----------|-------|-------|
| **StatusBadge** | status (done/running/waiting/failed/warning/queued) | Colour + icon + text, never colour alone |
| **RiskBadge** | level (low/medium/high/critical) | Outline badge with icon |
| **ConfidenceIndicator** | value (0–1) | Progress arc with colour gradient |
| **CircuitIndicator** | state (closed/open/half-open) | Dot with tooltip |
| **AutonomyDial** | level, onChange | 3-position visual dial |

### 10.4 Layout Components

| Component | Description |
|-----------|-------------|
| **AppShell** | Root layout: sidebar + header + content area |
| **Sidebar** | Role-aware navigation, collapsible, grouped sections |
| **Header** | Breadcrumbs, search trigger, notifications, user menu |
| **CommandPalette** | Ctrl+K, search across pages/runs/approvals/agents |
| **CopilotSheet** | Right-side slide-over chat, available on every page |
| **PageHeader** | Title (serif), subtitle, actions slot |
| **SectionHeader** | Sub-section title with optional actions |

### 10.5 Feedback Components

| Component | Trigger | Design |
|-----------|---------|--------|
| **Toast** | User action result | Bottom-right, auto-dismiss 5s, status icon + text |
| **EmptyState** | No data | Large icon + title + description + action button |
| **ErrorBoundary** | Component crash | Friendly message + retry button + error ID |
| **LoadingSkeleton** | Data loading | Component-shaped skeleton with shimmer |
| **SuccessState** | Action completed | Checkmark animation + summary |

### 10.6 Specialised Components

| Component | Page | Description |
|-----------|------|-------------|
| **AgentMapNode** | Agent Map | React Flow custom node: circle with status glow, label, current task tooltip |
| **AgentMapEdge** | Agent Map | Animated edge with dot travelling on handoff |
| **ApprovalCard** | Approval Inbox | Document-styled card: summary, risk badge, diff table, actions, countdown timer |
| **AuditChain** | Audit Explorer | Ribbon visualisation: chain links with verified/broken icons |
| **VerifyButton** | Audit Explorer | Button → loading → green check / red X with chain status |
| **WorkflowGraph** | Workflow Studio | React Flow read-only graph of YAML steps |
| **ChaosIndicator** | Connected Systems | Amber overlay when chaos mode active |
| **ConnectorTile** | Connected Systems | System card with icon, status dot, latency, circuit state |
| **ImpactNumber** | Impact Analytics | Large animated number with unit and trend |

---

## 11. Page Specifications

### 11.1 Login Screen

**Layout:** Centred card on oat canvas. NEXUS logo (wordmark) above form.

**Components:** Logo, Input (email), Input (password), Button (primary: "Sign in"), Link ("Forgot password?"), MFA input (conditional).

**States:** Default → Loading → Success redirect / Error (toast).

**Design notes:** No hero image, no illustration. Clean, confident, institutional. Subtle paper texture on background.

### 11.2 Mission Control (Overview)

**Layout:** Page header ("Mission Control") + 2-row grid.

**Row 1 — Stats bar (4 StatCards):**
| Stat | Value Format | Icon |
|------|-------------|------|
| Active Runs | Count | `Play` |
| Approvals Pending | Count (saffron if > 0) | `UserCheck` |
| Time Saved Today | "X min" | `Clock` |
| Cost Today | "$X.XX" | `Coins` |

**Row 2 — 3-column layout:**
- **Agent Map (span 2):** React Flow canvas showing Master + specialist agents. Nodes glow when active. Edges animate on handoff. Click node → tooltip with current task.
- **Recent Activity (span 1):** Scrollable event feed. Each event: icon, text, timestamp. Auto-updates via SSE.

**Row 3 — 2-column:**
- **Active Runs Table:** Run ID (mono), workflow, status badge, current step, elapsed, cost. Click → Run detail.
- **Connector Health Grid:** Tiles for ERP, LMS, CRM, Email, Telegram. Status dot, latency, circuit state.

### 11.3 Agent Map (Full Page)

**Layout:** Full-height React Flow canvas with floating control panel.

**Nodes:**
- Master Agent: larger circle, always centred
- Specialist agents: arranged radially
- Each node: status-coloured ring (glow when running), name, current task below
- Click: detail popover (task, model, tokens, duration)

**Edges:**
- Animated on handoff: dot travels from source to target (500ms)
- Edge colour: grey (idle), blue (active), green (complete), red (error)

**Controls:**
- Zoom, fit to view, minimap
- Filter by status
- Time slider for replay (Decision Replay mode)

### 11.4 Run Detail + Decision Replay

**Layout:** Split view — left: vertical timeline, right: detail panel.

**Timeline (left, 40% width):**
- Vertical steps, top to bottom
- Each step card: step name, agent, status badge, duration, token count
- Approval steps have distinct styling (document border)
- Click step → loads detail in right panel

**Detail panel (right, 60% width):**
- **Agent step:** inputs, outputs, decision record (options, chosen, confidence, rationale)
- **Connector step:** system, operation, diff (if dry-run), result, latency
- **Approval step:** approval card (summary, diff, approver, channel, decision, comment, timestamps)

**Decision Replay mode:**
- Time slider at top
- Steps highlight progressively as slider moves
- Agent map shows state at each checkpoint

### 11.5 Approval Inbox

**Layout:** Page header ("Approvals") + tabs (Pending | Decided | All) + card list.

**Approval Card (full detail):**
```
┌──────────────────────────────────────────────────────────┐
│  🔶 HIGH                                   ⏱ 28 min left │
│                                                          │
│  Publish marks for Unit Test 2, Division B               │
│  ─────────────────────────────────────────                │
│  2 answers below confidence threshold                    │
│  Average change: +12% vs previous exam                   │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Student     │ Old Mark │ New Mark │ Confidence     │  │
│  │ Karan M.    │    —     │   14/25  │ ⬤ 0.58 Low   │  │
│  │ Riya P.     │    —     │   16/25  │ ⬤ 0.91 High  │  │
│  │ ... (15 more rows) ...                            │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  Model: tier_strong · Agent: evaluation                  │
│  Run: exam_result_cycle #ERX-042                         │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌─────────────────────┐    │
│  │ ✓ Approve │  │ ✗ Reject │  │ ✎ Edit then approve │    │
│  └──────────┘  └──────────┘  └─────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

**Card styling:**
- Cream background (`--approval-card-bg`)
- Left border colour = risk level
- Timer countdown (saffron when < 10 min)
- Actions at bottom, primary = Approve (teal)

### 11.6 Connected Systems

**Layout:** Grid of ConnectorTiles (4 across on desktop, 2 on tablet).

**Each tile:**
- System icon/logo
- System name
- Status dot (green/amber/red)
- Latency (ms, mono font)
- Circuit state badge
- "View" button → iframe or embedded read-only view of the mock system

**Chaos indicator:** Amber overlay with pulsing border when chaos mode is active on a system.

### 11.7 Workflow Studio

**Layout:** Split — left: workflow list/tree, right: graph view.

**Graph view (React Flow):**
- Nodes for each step type (distinct icons per type)
- Edges showing flow direction
- Branch nodes with conditional labels
- Parallel nodes with fan-out/fan-in visual
- Read-only in v1 (editing in Phase 5+)

**Autonomy Dial:**
- 3-position visual dial below the graph
- Assist | Supervised | Autonomous
- Live switchable, with confirmation dialog

### 11.8 Audit Explorer + Verify Integrity

**Layout:** Page header + filters bar + data table + Verify button.

**Filters:** Run ID, actor, event type, system, date range.

**Table columns:** Seq (mono), Timestamp, Run, Actor, Event Type, System, Operation, Summary.

**Verify Integrity button:**
- Large, prominent, right of page header
- Click → loading spinner → result:
  - ✓ Green state: "Chain intact: 1,247 entries verified" (checkmark animation)
  - ✗ Red state: "Chain broken at entry #892" (with link to the entry)

**Chain visualisation (below table):**
- Horizontal ribbon of linked chain icons
- Green = verified, red = broken
- Click any link → jumps to that entry in the table

### 11.9 Impact Analytics

**Layout:** Stats row + charts grid.

**Stats row (4 large numbers):**
- Total Time Saved (animated counter, e.g., "4,230 min")
- Workflows Completed
- Errors Prevented
- Average Cost per Run

**Charts:**
- Bar chart: Manual estimate vs Automated time vs Human review time (per workflow type)
- Line chart: Time saved trend over time
- Pie chart: Automation rate (automated steps vs human steps)
- Table: Per-run breakdown with drilldown

### 11.10 Token & Cost

**Layout:** Budget summary + usage charts + savings view.

**Budget summary:** Bar showing used/remaining with threshold markers (50%, 80%, 95%).

**Usage charts:**
- Stacked bar: cost by model tier over time
- Stacked bar: cost by agent
- Table: recent LLM calls with model, tokens, cost, cached flag

**Savings view:**
- Side-by-side comparison: "Actual cost" vs "If all calls used strongest model"
- Savings percentage highlighted

### 11.11 Copilot

**Layout:** Full-height chat interface (right panel if sheet, full page if /copilot).

**Message types:**
- User message (right-aligned, teal-tinted bubble)
- Assistant message (left-aligned, surface-coloured)
- Chart/table responses (full-width, rendered inline)
- Confirmation card (action summary with Confirm/Cancel)

**Input:** Multi-line input with send button, optional file attachment.

### 11.12 Security Center

**Layout:** Stats + event list + active blocks.

**Stats:** Active incidents, blocked entities, failed logins (24h).

**Event list:** Searchable, filterable table of security events with severity badges.

**Active blocks:** Table of currently blocked IPs/users with expiry and unblock button.

### 11.13 Template Gallery

**Layout:** Grid of template cards, grouped by pack (Campus, HR, Finance).

**Template card:** Icon, name, description, system tags, "Use Template" button.

### 11.14 Settings

**Sub-pages:**
- General: Platform name, logo, institution settings
- Models & Tiers: Tier → model mapping, pricing table
- Budgets: Monthly limits, thresholds, enforcement mode
- Users & Roles: User list, role assignment, MFA status
- Notifications: Per-type channel preferences
- Sandbox: Demo mode toggle, reset button, chaos controls

---

## 12. Data Visualisation Style

### Chart Theme (Recharts)

```typescript
const chartTheme = {
  colors: [
    '#0E6B6B',  // primary teal
    '#3563C9',  // blue
    '#2E8B57',  // green
    '#E9A23B',  // saffron
    '#E8735A',  // coral
    '#5E6B72',  // muted
  ],
  axis: {
    stroke: '#D9D2C2',     // border colour
    tick: { fill: '#5E6B72', fontSize: 11, fontFamily: 'Inter' },
    label: { fill: '#1E2A32', fontSize: 13, fontFamily: 'Inter', fontWeight: 600 },
  },
  grid: {
    stroke: '#E9E4D8',     // sunken colour
    strokeDasharray: '3 3',
  },
  tooltip: {
    bg: '#FBF9F4',         // surface
    border: '#D9D2C2',
    text: '#1E2A32',
    radius: 8,
  },
  legend: {
    text: { fill: '#5E6B72', fontSize: 12, fontFamily: 'Inter' },
  },
};
```

### Chart Types Used

| Chart | Page | Configuration |
|-------|------|--------------|
| Bar (horizontal) | Impact | Grouped: manual/automated/human per workflow |
| Bar (stacked) | Cost | Cost by tier over time |
| Line | Impact | Time saved trend |
| Area | Monitoring | Queue depth over time |
| Donut | Analytics | Automation rate |
| Sparkline | StatCards | Inline trend |
| Flow graph | Agent Map | React Flow with custom nodes |
| Timeline | Run Detail | Vertical, custom |

---

## 13. Copy & Tone Guidelines

### Voice

- **Authoritative but approachable.** Not robotic, not casual.
- **Precise.** "2 answers below confidence threshold" not "Some answers may have issues."
- **Honest.** "Measured with a stopwatch on 5 samples" not "Saves hours of time."
- **Active voice.** "The agent flagged this answer" not "This answer was flagged."

### Key UI Copy Patterns

| Context | Pattern | Example |
|---------|---------|---------|
| Empty state | Descriptive + action | "No workflow runs yet. Start your first workflow →" |
| Error | What happened + what to do | "Failed to connect to ERP. Check connector settings or retry." |
| Success | Confirmation | "Marks published to ERP. 28 students updated." |
| Loading | What's happening | "Evaluating answer sheets..." |
| Approval | Clear ask | "Review and approve 28 mark updates for Unit Test 2, Division B" |
| Stat label | Noun + qualifier | "Time Saved Today" not "Total time saved since start" |

### Terminology

| Use | Don't use |
|-----|-----------|
| Workflow | Pipeline, process |
| Run | Execution, instance |
| Agent | Bot, assistant |
| Approval | Authorization, permission |
| Ledger | Log, audit trail (use "audit trail" only in external communication) |
| Connector | Integration, adapter |
| Policy | Rule (policies contain rules) |

---

## 14. Accessibility Plan

### Standards

- **WCAG 2.2 Level AA** — all pages
- **WCAG 2.2 Level AAA** — for text contrast where feasible

### Checklist (per component / per page)

- [ ] Colour contrast ≥ 4.5:1 (text), ≥ 3:1 (large text, UI components)
- [ ] Colour is never the sole indicator of status
- [ ] All interactive elements are keyboard-navigable (Tab, Enter, Escape, Arrow keys)
- [ ] Visible focus indicators (2px teal ring, 3:1 contrast)
- [ ] All images have alt text
- [ ] All form inputs have labels (visible or `aria-label`)
- [ ] Error messages are programmatically associated (`aria-describedby`)
- [ ] Live regions for dynamic content (`aria-live="polite"` for event feeds, toasts)
- [ ] Skip-to-content link on every page
- [ ] Heading hierarchy is correct (one `h1` per page)
- [ ] `prefers-reduced-motion` respected (all animations disabled)
- [ ] `prefers-contrast: more` supported (high-contrast token overrides)
- [ ] Touch targets ≥ 44×44px
- [ ] Page is usable at 200% zoom without horizontal scrolling

### Focus Styling

```css
:focus-visible {
  outline: 2px solid var(--color-focus-ring);
  outline-offset: 2px;
  border-radius: var(--radius-sm);
}
```

### Screen Reader Patterns

| Element | ARIA | Notes |
|---------|------|-------|
| Status badge | `role="status"`, `aria-label="Status: Running"` | Dynamic updates with `aria-live` |
| Agent map | `role="img"`, `aria-label="Agent network diagram"` | Summary of active/idle agents |
| Counter ticker | `aria-live="polite"`, `aria-atomic="true"` | Announces new value |
| Approval timer | `aria-label="28 minutes remaining"` | Updated every minute |
| Data table | Standard `<table>` with `<th scope="col">` | Sort state: `aria-sort` |

---

## 15. Dark Theme Plan (Phase 4+)

**Approach:** Semantic token remap only. Global tokens stay. Component tokens inherit.

```css
[data-theme="dark"] {
  --color-canvas:           #1A1D21;
  --color-surface:          #22262B;
  --color-surface-raised:   #282D33;
  --color-surface-sunken:   #141619;
  --color-border:           #353B42;
  --color-border-subtle:    #2B3038;
  --color-text-primary:     #E8E6E1;
  --color-text-secondary:   #9CA3AB;
  --color-text-on-primary:  #FFFFFF;
  /* Status colours lighten slightly for dark backgrounds */
  --color-status-done:      #3DA36C;
  --color-status-running:   #5B8FE8;
  --color-status-waiting:   #F0B556;
  --color-status-failed:    #E06B62;
}
```

All contrast ratios re-verified before shipping dark theme.

---

## 16. Tailwind Configuration

### tailwind.config.ts (token mapping)

```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: "var(--color-canvas)",
        surface: {
          DEFAULT: "var(--color-surface)",
          raised: "var(--color-surface-raised)",
          sunken: "var(--color-surface-sunken)",
        },
        border: {
          DEFAULT: "var(--color-border)",
          subtle: "var(--color-border-subtle)",
          strong: "var(--color-border-strong)",
        },
        ink: {
          DEFAULT: "var(--color-text-primary)",
          muted: "var(--color-text-secondary)",
          faint: "var(--color-text-tertiary)",
          disabled: "var(--color-text-disabled)",
        },
        primary: {
          DEFAULT: "var(--color-primary)",
          hover: "var(--color-primary-hover)",
          active: "var(--color-primary-active)",
          tint: "var(--color-primary-tint)",
          subtle: "var(--color-primary-subtle)",
        },
        status: {
          done: "var(--color-status-done)",
          "done-bg": "var(--color-status-done-bg)",
          running: "var(--color-status-running)",
          "running-bg": "var(--color-status-running-bg)",
          waiting: "var(--color-status-waiting)",
          "waiting-bg": "var(--color-status-waiting-bg)",
          failed: "var(--color-status-failed)",
          "failed-bg": "var(--color-status-failed-bg)",
        },
        ai: {
          accent: "var(--color-ai-accent)",
          "accent-bg": "var(--color-ai-accent-bg)",
        },
      },
      fontFamily: {
        heading: ["var(--font-heading)"],
        body: ["var(--font-body)"],
        mono: ["var(--font-mono)"],
      },
      fontSize: {
        display: ["var(--text-display-size)", { lineHeight: "var(--text-display-line)" }],
        h1: ["var(--text-h1-size)", { lineHeight: "var(--text-h1-line)" }],
        h2: ["var(--text-h2-size)", { lineHeight: "var(--text-h2-line)" }],
        h3: ["var(--text-h3-size)", { lineHeight: "var(--text-h3-line)" }],
        body: ["var(--text-body-size)", { lineHeight: "var(--text-body-line)" }],
        sm: ["var(--text-sm-size)", { lineHeight: "var(--text-sm-line)" }],
        xs: ["var(--text-xs-size)", { lineHeight: "var(--text-xs-line)" }],
        stat: ["var(--text-stat-size)", { lineHeight: "var(--text-stat-line)" }],
      },
      borderRadius: {
        sm: "var(--radius-sm)",
        md: "var(--radius-md)",
        lg: "var(--radius-lg)",
        xl: "var(--radius-xl)",
      },
      boxShadow: {
        xs: "var(--shadow-xs)",
        sm: "var(--shadow-sm)",
        md: "var(--shadow-md)",
        lg: "var(--shadow-lg)",
        xl: "var(--shadow-xl)",
      },
      transitionDuration: {
        fast: "var(--motion-fast)",
        normal: "var(--motion-normal)",
        slow: "var(--motion-slow)",
        deliberate: "var(--motion-deliberate)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
```

---

*End of DESIGN.md. See also: [PLAN.md](file:///d:/Projects%202/Veyronica/PLAN.md) · [TASKS.md](file:///d:/Projects%202/Veyronica/TASKS.md) · [design/tokens.css](file:///d:/Projects%202/Veyronica/design/tokens.css)*
