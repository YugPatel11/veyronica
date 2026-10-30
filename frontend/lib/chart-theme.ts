/**
 * Chart Theme & Design System Integration (EPIC-02-T13)
 * Provides cohesive color palettes, axis styles, tooltip styles, and helpers
 * matching the Veyronica/Nexus dark & light modern glassmorphic theme.
 */

export const chartColors = {
  primary: "#6366f1",    // Indigo
  secondary: "#06b6d4",  // Cyan
  success: "#10b981",    // Emerald
  warning: "#f59e0b",    // Amber
  danger: "#ef4444",     // Rose/Red
  purple: "#8b5cf6",     // Violet
  pink: "#ec4899",       // Pink
  muted: "#64748b",      // Slate
  background: "#0f172a", // Dark background
  card: "#1e293b",       // Dark surface
  border: "#334155",     // Slate border
  text: "#f8fafc",       // Text primary
  textMuted: "#94a3b8",  // Text muted
};

export const chartGradients = {
  primary: ["rgba(99, 102, 241, 0.4)", "rgba(99, 102, 241, 0.0)"],
  secondary: ["rgba(6, 182, 212, 0.4)", "rgba(6, 182, 212, 0.0)"],
  success: ["rgba(16, 185, 129, 0.4)", "rgba(16, 185, 129, 0.0)"],
  danger: ["rgba(239, 68, 68, 0.4)", "rgba(239, 68, 68, 0.0)"],
};

export const defaultAxisProps = {
  stroke: chartColors.border,
  tick: { fill: chartColors.textMuted, fontSize: 12 },
  tickLine: { stroke: chartColors.border },
  axisLine: { stroke: chartColors.border },
};

export const defaultGridProps = {
  stroke: "#1e293b",
  strokeDasharray: "3 3",
  vertical: false,
};

export const defaultTooltipStyle = {
  backgroundColor: "rgba(15, 23, 42, 0.95)",
  border: "1px solid #334155",
  borderRadius: "8px",
  boxShadow: "0 10px 25px -5px rgba(0, 0, 0, 0.5)",
  color: "#f8fafc",
  fontSize: "12px",
  padding: "8px 12px",
};
