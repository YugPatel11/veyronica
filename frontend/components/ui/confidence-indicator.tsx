"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

/**
 * ConfidenceIndicator — EPIC-02-T06
 *
 * Circular progress arc showing AI confidence (0–1).
 * Colour gradient: red → saffron → green.
 */

interface ConfidenceIndicatorProps {
  value: number; // 0 to 1
  size?: number;
  strokeWidth?: number;
  showLabel?: boolean;
  className?: string;
}

function getConfidenceColor(value: number): string {
  if (value >= 0.8) return "var(--color-status-done)";
  if (value >= 0.5) return "var(--color-status-waiting)";
  return "var(--color-status-failed)";
}

function getConfidenceLabel(value: number): string {
  if (value >= 0.8) return "High";
  if (value >= 0.5) return "Medium";
  return "Low";
}

export function ConfidenceIndicator({
  value,
  size = 36,
  strokeWidth = 3,
  showLabel = true,
  className,
}: ConfidenceIndicatorProps) {
  const clamped = Math.min(Math.max(value, 0), 1);
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - clamped);
  const color = getConfidenceColor(clamped);
  const label = getConfidenceLabel(clamped);

  return (
    <div className={cn("inline-flex items-center gap-2", className)}>
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        className="-rotate-90"
        role="meter"
        aria-valuenow={Math.round(clamped * 100)}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`Confidence: ${Math.round(clamped * 100)}%`}
      >
        {/* Background ring */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="var(--color-surface-sunken)"
          strokeWidth={strokeWidth}
        />
        {/* Foreground arc */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-500 ease-out"
        />
      </svg>
      {showLabel && (
        <span className="text-xs font-medium" style={{ color }}>
          {(clamped * 100).toFixed(0)}% {label}
        </span>
      )}
    </div>
  );
}

export type { ConfidenceIndicatorProps };
