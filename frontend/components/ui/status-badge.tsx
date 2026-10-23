import * as React from "react";
import {
  CheckCircle2,
  Loader2,
  Clock,
  XCircle,
  AlertTriangle,
  Pause,
} from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * StatusBadge — EPIC-02-T06
 *
 * Status indicator with colour + icon + text.
 * Never colour alone (accessibility).
 */

type Status = "done" | "running" | "waiting" | "failed" | "warning" | "queued" | "skipped";

interface StatusBadgeProps {
  status: Status;
  label?: string;
  className?: string;
}

const statusConfig: Record<
  Status,
  { icon: React.ElementType; label: string; className: string }
> = {
  done: {
    icon: CheckCircle2,
    label: "Completed",
    className:
      "bg-[var(--color-status-done-bg)] text-[var(--color-status-done)]",
  },
  running: {
    icon: Loader2,
    label: "Running",
    className:
      "bg-[var(--color-status-running-bg)] text-[var(--color-status-running)]",
  },
  waiting: {
    icon: Clock,
    label: "Waiting",
    className:
      "bg-[var(--color-status-waiting-bg)] text-[var(--color-saffron-dark)]",
  },
  failed: {
    icon: XCircle,
    label: "Failed",
    className:
      "bg-[var(--color-status-failed-bg)] text-[var(--color-status-failed)]",
  },
  warning: {
    icon: AlertTriangle,
    label: "Warning",
    className:
      "bg-[var(--color-status-waiting-bg)] text-[var(--color-saffron-dark)]",
  },
  queued: {
    icon: Pause,
    label: "Queued",
    className:
      "bg-[var(--color-surface-sunken)] text-[var(--color-ink-muted)]",
  },
  skipped: {
    icon: Pause,
    label: "Skipped",
    className:
      "bg-[var(--color-surface-sunken)] text-[var(--color-ink-disabled)]",
  },
};

export function StatusBadge({ status, label, className }: StatusBadgeProps) {
  const config = statusConfig[status];
  const Icon = config.icon;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium",
        config.className,
        className
      )}
      role="status"
    >
      <Icon
        size={14}
        strokeWidth={2}
        className={status === "running" ? "animate-spin" : ""}
      />
      {label || config.label}
    </span>
  );
}

export type { Status, StatusBadgeProps };
