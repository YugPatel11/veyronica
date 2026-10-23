"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { TrendingUp, TrendingDown, Minus, type LucideIcon } from "lucide-react";

/**
 * StatCard — EPIC-02-T05
 *
 * Large stat number with label, delta trend, and icon.
 * Design: "Numbers are large, readable, and honest"
 */

interface StatCardProps {
  label: string;
  value: string | number;
  delta?: string;
  trend?: "up" | "down" | "neutral";
  icon?: LucideIcon;
  loading?: boolean;
  className?: string;
}

export function StatCard({
  label,
  value,
  delta,
  trend = "neutral",
  icon: Icon,
  loading = false,
  className,
}: StatCardProps) {
  const trendConfig = {
    up: {
      icon: TrendingUp,
      color: "text-[var(--color-status-done)]",
      bg: "bg-[var(--color-status-done-bg)]",
    },
    down: {
      icon: TrendingDown,
      color: "text-[var(--color-status-failed)]",
      bg: "bg-[var(--color-status-failed-bg)]",
    },
    neutral: {
      icon: Minus,
      color: "text-[var(--color-ink-muted)]",
      bg: "bg-[var(--color-surface-sunken)]",
    },
  };

  const t = trendConfig[trend];
  const TrendIcon = t.icon;

  if (loading) {
    return (
      <div
        className={cn(
          "rounded-[var(--radius-lg)] border border-[var(--color-border-subtle)] bg-[var(--color-surface)] p-5",
          className
        )}
        aria-busy="true"
      >
        <div className="h-4 w-24 animate-pulse rounded bg-[var(--color-surface-sunken)]" />
        <div className="mt-3 h-8 w-20 animate-pulse rounded bg-[var(--color-surface-sunken)]" />
        <div className="mt-2 h-3 w-16 animate-pulse rounded bg-[var(--color-surface-sunken)]" />
      </div>
    );
  }

  return (
    <div
      className={cn(
        "rounded-[var(--radius-lg)] border border-[var(--color-border-subtle)] bg-[var(--color-surface)] p-5 transition-shadow hover:shadow-[var(--shadow-sm)]",
        className
      )}
    >
      <div className="flex items-center justify-between">
        <p className="text-xs font-medium uppercase tracking-wider text-[var(--color-ink-faint)]">
          {label}
        </p>
        {Icon && (
          <Icon
            size={20}
            strokeWidth={1.5}
            className="text-[var(--color-ink-disabled)]"
          />
        )}
      </div>
      <p className="mt-2 font-mono text-[1.75rem] font-bold leading-none text-[var(--color-ink)]">
        {value}
      </p>
      {delta && (
        <div className="mt-2 flex items-center gap-1.5">
          <span
            className={cn(
              "inline-flex items-center gap-0.5 rounded-full px-1.5 py-0.5 text-[11px] font-medium",
              t.color,
              t.bg
            )}
          >
            <TrendIcon size={12} />
            {delta}
          </span>
        </div>
      )}
    </div>
  );
}
