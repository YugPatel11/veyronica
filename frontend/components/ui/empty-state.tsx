import * as React from "react";
import { cn } from "@/lib/utils";
import { type LucideIcon, FileQuestion } from "lucide-react";
import { Button } from "./button";

/**
 * EmptyState — EPIC-02-T08
 *
 * Large icon + title + description + optional action button.
 */

interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
  className?: string;
}

export function EmptyState({
  icon: Icon = FileQuestion,
  title,
  description,
  actionLabel,
  onAction,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center py-16 px-4 text-center",
        className
      )}
    >
      <div className="rounded-full bg-[var(--color-surface-sunken)] p-4">
        <Icon
          size={48}
          strokeWidth={1.25}
          className="text-[var(--color-ink-disabled)]"
        />
      </div>
      <h3 className="mt-4 font-heading text-lg font-semibold text-[var(--color-ink)]">
        {title}
      </h3>
      {description && (
        <p className="mt-1.5 max-w-sm text-sm text-[var(--color-ink-muted)]">
          {description}
        </p>
      )}
      {actionLabel && onAction && (
        <Button variant="primary" size="md" onClick={onAction} className="mt-5">
          {actionLabel}
        </Button>
      )}
    </div>
  );
}
