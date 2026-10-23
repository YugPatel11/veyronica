import * as React from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * Select — EPIC-02-T04
 *
 * Native select with NEXUS theme for simplicity and accessibility.
 */

export interface SelectProps
  extends React.SelectHTMLAttributes<HTMLSelectElement> {
  error?: boolean;
  placeholder?: string;
}

const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, error, children, placeholder, ...props }, ref) => {
    return (
      <div className="relative w-full">
        <select
          className={cn(
            "flex h-10 w-full appearance-none rounded-[var(--radius-md)] bg-[var(--color-surface-raised)] px-3 py-2 pr-8 text-sm text-[var(--color-ink)] transition-colors duration-100",
            "border",
            "focus:outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary-subtle)]",
            "disabled:cursor-not-allowed disabled:opacity-50",
            error
              ? "border-[var(--color-status-failed)]"
              : "border-[var(--color-border)]",
            className
          )}
          ref={ref}
          aria-invalid={error || undefined}
          {...props}
        >
          {placeholder && (
            <option value="" disabled>
              {placeholder}
            </option>
          )}
          {children}
        </select>
        <ChevronDown
          size={16}
          className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-[var(--color-ink-muted)]"
        />
      </div>
    );
  }
);
Select.displayName = "Select";

export { Select };
