import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

/**
 * Badge — EPIC-02-T04
 *
 * Variants: filled, outline, dot
 * Accessibility: role="status" for live badges
 */

const badgeVariants = cva(
  "inline-flex items-center gap-1.5 rounded-full text-xs font-medium transition-colors",
  {
    variants: {
      variant: {
        filled: "px-2.5 py-0.5",
        outline: "px-2.5 py-0.5 border bg-transparent",
        dot: "px-2.5 py-0.5",
      },
      color: {
        default:
          "bg-[var(--color-surface-sunken)] text-[var(--color-ink-muted)] border-[var(--color-border)]",
        primary:
          "bg-[var(--color-primary-tint)] text-[var(--color-primary)] border-[var(--color-primary)]",
        success:
          "bg-[var(--color-status-done-bg)] text-[var(--color-status-done)] border-[var(--color-status-done)]",
        warning:
          "bg-[var(--color-status-waiting-bg)] text-[var(--color-saffron-dark)] border-[var(--color-status-waiting)]",
        danger:
          "bg-[var(--color-status-failed-bg)] text-[var(--color-status-failed)] border-[var(--color-status-failed)]",
        info: "bg-[var(--color-status-running-bg)] text-[var(--color-status-running)] border-[var(--color-status-running)]",
        ai: "bg-[var(--color-ai-accent-bg)] text-[var(--color-ai-accent)] border-[var(--color-ai-accent)]",
      },
    },
    defaultVariants: {
      variant: "filled",
      color: "default",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {
  live?: boolean;
}

const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, variant, color, live, children, ...props }, ref) => {
    return (
      <span
        ref={ref}
        className={cn(badgeVariants({ variant, color, className }))}
        role={live ? "status" : undefined}
        aria-live={live ? "polite" : undefined}
        {...props}
      >
        {variant === "dot" && (
          <span
            className="h-1.5 w-1.5 rounded-full"
            style={{ backgroundColor: "currentColor" }}
          />
        )}
        {children}
      </span>
    );
  }
);
Badge.displayName = "Badge";

export { Badge, badgeVariants };
