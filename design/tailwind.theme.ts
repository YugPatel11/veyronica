/**
 * NEXUS — Tailwind Theme Extension
 * "Editorial Mission Control" · Light Mode
 *
 * Import this in tailwind.config.ts:
 *   import { nexusTheme } from "./design/tailwind.theme";
 *   theme: { extend: nexusTheme }
 */

export const nexusTheme = {
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
      warning: "var(--color-status-warning)",
      "warning-bg": "var(--color-status-warning-bg)",
    },
    ai: {
      accent: "var(--color-ai-accent)",
      "accent-bg": "var(--color-ai-accent-bg)",
    },
    saffron: {
      DEFAULT: "var(--color-saffron-600)",
      50: "var(--color-saffron-50)",
      100: "var(--color-saffron-100)",
      600: "var(--color-saffron-600)",
      900: "var(--color-saffron-900)",
    },
  },

  fontFamily: {
    heading: ["var(--font-heading)"],
    body: ["var(--font-body)"],
    mono: ["var(--font-mono)"],
  },

  fontSize: {
    display: [
      "var(--text-display-size)",
      { lineHeight: "var(--text-display-line)", fontWeight: "var(--text-display-weight)" },
    ],
    h1: [
      "var(--text-h1-size)",
      { lineHeight: "var(--text-h1-line)", fontWeight: "var(--text-h1-weight)" },
    ],
    h2: [
      "var(--text-h2-size)",
      { lineHeight: "var(--text-h2-line)", fontWeight: "var(--text-h2-weight)" },
    ],
    h3: [
      "var(--text-h3-size)",
      { lineHeight: "var(--text-h3-line)", fontWeight: "var(--text-h3-weight)" },
    ],
    body: [
      "var(--text-body-size)",
      { lineHeight: "var(--text-body-line)" },
    ],
    sm: [
      "var(--text-sm-size)",
      { lineHeight: "var(--text-sm-line)" },
    ],
    xs: [
      "var(--text-xs-size)",
      { lineHeight: "var(--text-xs-line)" },
    ],
    mono: [
      "var(--text-mono-size)",
      { lineHeight: "var(--text-mono-line)" },
    ],
    stat: [
      "var(--text-stat-size)",
      { lineHeight: "var(--text-stat-line)", fontWeight: "var(--text-stat-weight)" },
    ],
    "stat-sm": [
      "var(--text-stat-sm-size)",
      { lineHeight: "var(--text-stat-sm-line)", fontWeight: "var(--text-stat-sm-weight)" },
    ],
  },

  borderRadius: {
    none: "var(--radius-none)",
    sm: "var(--radius-sm)",
    md: "var(--radius-md)",
    lg: "var(--radius-lg)",
    xl: "var(--radius-xl)",
    full: "var(--radius-full)",
  },

  boxShadow: {
    none: "var(--shadow-none)",
    xs: "var(--shadow-xs)",
    sm: "var(--shadow-sm)",
    md: "var(--shadow-md)",
    lg: "var(--shadow-lg)",
    xl: "var(--shadow-xl)",
  },

  transitionDuration: {
    instant: "var(--motion-instant)",
    fast: "var(--motion-fast)",
    normal: "var(--motion-normal)",
    slow: "var(--motion-slow)",
    deliberate: "var(--motion-deliberate)",
  },

  transitionTimingFunction: {
    "ease-out": "var(--ease-out)",
    "ease-in": "var(--ease-in)",
    "ease-in-out": "var(--ease-in-out)",
    spring: "var(--ease-spring)",
  },

  spacing: {
    "0.5": "var(--space-0-5)",
    "1": "var(--space-1)",
    "1.5": "var(--space-1-5)",
    "2": "var(--space-2)",
    "3": "var(--space-3)",
    "4": "var(--space-4)",
    "5": "var(--space-5)",
    "6": "var(--space-6)",
    "8": "var(--space-8)",
    "10": "var(--space-10)",
    "12": "var(--space-12)",
    "16": "var(--space-16)",
    sidebar: "var(--sidebar-width)",
    "sidebar-collapsed": "var(--sidebar-width-collapsed)",
  },

  maxWidth: {
    content: "var(--content-max-width)",
  },
} as const;
