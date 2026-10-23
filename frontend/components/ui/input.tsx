import * as React from "react";
import { cn } from "@/lib/utils";

/**
 * Input — EPIC-02-T04
 *
 * Themed input matching NEXUS design tokens.
 * States: default, focus, error, disabled
 * Accessibility: aria-invalid, aria-describedby for errors
 */

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: boolean;
  errorMessage?: string;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, error, errorMessage, id, ...props }, ref) => {
    const errorId = errorMessage && id ? `${id}-error` : undefined;
    return (
      <div className="w-full">
        <input
          type={type}
          id={id}
          className={cn(
            "flex h-10 w-full rounded-[var(--radius-md)] bg-[var(--color-surface-raised)] px-3 py-2 text-sm text-[var(--color-ink)] transition-colors duration-100",
            "border placeholder:text-[var(--color-ink-disabled)]",
            "focus:outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary-subtle)]",
            "disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-[var(--color-surface-sunken)]",
            error
              ? "border-[var(--color-status-failed)] focus:border-[var(--color-status-failed)] focus:ring-[var(--color-status-failed-bg)]"
              : "border-[var(--color-border)]",
            className
          )}
          ref={ref}
          aria-invalid={error || undefined}
          aria-describedby={errorId}
          {...props}
        />
        {errorMessage && (
          <p
            id={errorId}
            className="mt-1.5 text-xs text-[var(--color-status-failed)]"
            role="alert"
          >
            {errorMessage}
          </p>
        )}
      </div>
    );
  }
);
Input.displayName = "Input";

export { Input };
