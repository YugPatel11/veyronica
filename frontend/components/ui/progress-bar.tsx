import * as React from "react";
import { cn } from "@/lib/utils";

/**
 * ProgressBar — EPIC-02-T05
 *
 * Accessible progress bar with aria-valuenow.
 */

interface ProgressBarProps {
  value: number;
  max?: number;
  label?: string;
  showValue?: boolean;
  size?: "sm" | "md" | "lg";
  color?: "primary" | "success" | "warning" | "danger";
  indeterminate?: boolean;
  className?: string;
}

const colorMap = {
  primary: "bg-[var(--color-primary)]",
  success: "bg-[var(--color-status-done)]",
  warning: "bg-[var(--color-status-waiting)]",
  danger: "bg-[var(--color-status-failed)]",
};

const sizeMap = {
  sm: "h-1.5",
  md: "h-2.5",
  lg: "h-4",
};

export function ProgressBar({
  value,
  max = 100,
  label,
  showValue = false,
  size = "md",
  color = "primary",
  indeterminate = false,
  className,
}: ProgressBarProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  return (
    <div className={cn("w-full", className)}>
      {(label || showValue) && (
        <div className="mb-1.5 flex items-center justify-between">
          {label && (
            <span className="text-xs font-medium text-[var(--color-ink-muted)]">
              {label}
            </span>
          )}
          {showValue && (
            <span className="font-mono text-xs text-[var(--color-ink-muted)]">
              {Math.round(percentage)}%
            </span>
          )}
        </div>
      )}
      <div
        className={cn(
          "w-full overflow-hidden rounded-full bg-[var(--color-surface-sunken)]",
          sizeMap[size]
        )}
        role="progressbar"
        aria-valuenow={indeterminate ? undefined : Math.round(percentage)}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={label}
      >
        <div
          className={cn(
            "h-full rounded-full transition-all duration-500 ease-out",
            colorMap[color],
            indeterminate && "animate-pulse w-full"
          )}
          style={indeterminate ? undefined : { width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
