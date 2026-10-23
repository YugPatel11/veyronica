import * as React from "react";
import { cn } from "@/lib/utils";

/**
 * Skeleton — EPIC-02-T08
 *
 * Component-shaped loading placeholder with shimmer animation.
 */

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "text" | "circle" | "card";
  width?: string | number;
  height?: string | number;
}

function Skeleton({
  className,
  variant = "text",
  width,
  height,
  ...props
}: SkeletonProps) {
  const variantStyles = {
    text: "h-4 w-full rounded",
    circle: "rounded-full",
    card: "rounded-[var(--radius-lg)]",
  };

  return (
    <div
      className={cn(
        "animate-pulse bg-[var(--color-surface-sunken)]",
        variantStyles[variant],
        className
      )}
      style={{ width, height }}
      aria-busy="true"
      aria-label="Loading..."
      {...props}
    />
  );
}

/**
 * Pre-built skeleton compositions
 */
function SkeletonCard({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "rounded-[var(--radius-lg)] border border-[var(--color-border-subtle)] bg-[var(--color-surface)] p-5 space-y-3",
        className
      )}
    >
      <Skeleton variant="text" className="h-4 w-2/5" />
      <Skeleton variant="text" className="h-8 w-1/3" />
      <Skeleton variant="text" className="h-3 w-1/4" />
    </div>
  );
}

function SkeletonTable({ rows = 5 }: { rows?: number }) {
  return (
    <div className="space-y-2">
      <div className="flex gap-4 px-4 py-2">
        <Skeleton className="h-4 w-1/4" />
        <Skeleton className="h-4 w-1/4" />
        <Skeleton className="h-4 w-1/4" />
        <Skeleton className="h-4 w-1/4" />
      </div>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-4 px-4 py-3 border-t border-[var(--color-border-subtle)]">
          <Skeleton className="h-4 w-1/4" />
          <Skeleton className="h-4 w-1/4" />
          <Skeleton className="h-4 w-1/4" />
          <Skeleton className="h-4 w-1/4" />
        </div>
      ))}
    </div>
  );
}

export { Skeleton, SkeletonCard, SkeletonTable };
