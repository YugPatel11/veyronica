import * as React from "react";
import { Info, AlertCircle, AlertTriangle, ShieldAlert } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * RiskBadge — EPIC-02-T06
 *
 * Outline badge with icon indicating risk level.
 */

type RiskLevel = "low" | "medium" | "high" | "critical";

interface RiskBadgeProps {
  level: RiskLevel;
  className?: string;
}

const riskConfig: Record<
  RiskLevel,
  { icon: React.ElementType; label: string; className: string }
> = {
  low: {
    icon: Info,
    label: "Low",
    className:
      "border-[var(--color-status-running)] text-[var(--color-status-running)] bg-[var(--color-status-running-bg)]",
  },
  medium: {
    icon: AlertCircle,
    label: "Medium",
    className:
      "border-[var(--color-status-waiting)] text-[var(--color-saffron-dark)] bg-[var(--color-status-waiting-bg)]",
  },
  high: {
    icon: AlertTriangle,
    label: "High",
    className:
      "border-[var(--color-status-failed)] text-[var(--color-status-failed)] bg-[var(--color-status-failed-bg)]",
  },
  critical: {
    icon: ShieldAlert,
    label: "Critical",
    className:
      "border-[var(--color-status-failed)] text-white bg-[var(--color-status-failed)]",
  },
};

export function RiskBadge({ level, className }: RiskBadgeProps) {
  const config = riskConfig[level];
  const Icon = config.icon;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-semibold uppercase tracking-wide",
        config.className,
        className
      )}
    >
      <Icon size={13} strokeWidth={2} />
      {config.label}
    </span>
  );
}

export type { RiskLevel, RiskBadgeProps };
