import * as React from "react";
import { cn } from "@/lib/utils";

/**
 * Timeline — EPIC-02-T05
 *
 * Vertical timeline with step cards and connector lines.
 */

interface TimelineEntry {
  id: string;
  title: string;
  description?: string;
  timestamp?: string;
  status?: "completed" | "running" | "pending" | "failed" | "skipped";
  icon?: React.ReactNode;
}

interface TimelineProps {
  entries: TimelineEntry[];
  className?: string;
}

const statusStyles: Record<string, { dot: string; line: string }> = {
  completed: {
    dot: "bg-[var(--color-status-done)] border-[var(--color-status-done-bg)]",
    line: "bg-[var(--color-status-done)]",
  },
  running: {
    dot: "bg-[var(--color-status-running)] border-[var(--color-status-running-bg)] animate-pulse",
    line: "bg-[var(--color-border)]",
  },
  pending: {
    dot: "bg-[var(--color-surface-sunken)] border-[var(--color-border)]",
    line: "bg-[var(--color-border-subtle)]",
  },
  failed: {
    dot: "bg-[var(--color-status-failed)] border-[var(--color-status-failed-bg)]",
    line: "bg-[var(--color-status-failed)]",
  },
  skipped: {
    dot: "bg-[var(--color-ink-disabled)] border-[var(--color-surface-sunken)]",
    line: "bg-[var(--color-border-subtle)]",
  },
};

const defaultStatusStyle: { dot: string; line: string } = {
  dot: "bg-[var(--color-surface-sunken)] border-[var(--color-border)]",
  line: "bg-[var(--color-border-subtle)]",
};

export function Timeline({ entries, className }: TimelineProps) {
  return (
    <div className={cn("relative space-y-0", className)}>
      {entries.map((entry, index) => {
        const status = entry.status || "pending";
        const styles = statusStyles[status] ?? defaultStatusStyle;
        const isLast = index === entries.length - 1;

        return (
          <div key={entry.id} className="relative flex gap-4 pb-6 last:pb-0">
            {/* Connector line */}
            {!isLast && (
              <div
                className={cn(
                  "absolute left-[11px] top-6 h-full w-0.5",
                  styles.line
                )}
              />
            )}

            {/* Dot */}
            <div className="relative z-10 flex-shrink-0">
              <div
                className={cn(
                  "h-6 w-6 rounded-full border-2 flex items-center justify-center",
                  styles.dot
                )}
              >
                {entry.icon && (
                  <span className="text-white">{entry.icon}</span>
                )}
              </div>
            </div>

            {/* Content */}
            <div className="min-w-0 flex-1 pt-0.5">
              <div className="flex items-center justify-between gap-2">
                <p className="text-sm font-medium text-[var(--color-ink)]">
                  {entry.title}
                </p>
                {entry.timestamp && (
                  <time className="flex-shrink-0 font-mono text-[11px] text-[var(--color-ink-faint)]">
                    {entry.timestamp}
                  </time>
                )}
              </div>
              {entry.description && (
                <p className="mt-0.5 text-xs text-[var(--color-ink-muted)]">
                  {entry.description}
                </p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export type { TimelineEntry, TimelineProps };
