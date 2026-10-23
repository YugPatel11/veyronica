import * as React from "react";
import { cn } from "@/lib/utils";

/**
 * Textarea — EPIC-02-T04
 */

export interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: boolean;
  errorMessage?: string;
}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, error, errorMessage, id, ...props }, ref) => {
    const errorId = errorMessage && id ? `${id}-error` : undefined;
    return (
      <div className="w-full">
        <textarea
          id={id}
          className={cn(
            "flex min-h-[80px] w-full rounded-[var(--radius-md)] bg-[var(--color-surface-raised)] px-3 py-2 text-sm text-[var(--color-ink)] transition-colors duration-100",
            "border placeholder:text-[var(--color-ink-disabled)] resize-y",
            "focus:outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary-subtle)]",
            "disabled:cursor-not-allowed disabled:opacity-50",
            error
              ? "border-[var(--color-status-failed)]"
              : "border-[var(--color-border)]",
            className
          )}
          ref={ref}
          aria-invalid={error || undefined}
          aria-describedby={errorId}
          {...props}
        />
        {errorMessage && (
          <p id={errorId} className="mt-1.5 text-xs text-[var(--color-status-failed)]" role="alert">
            {errorMessage}
          </p>
        )}
      </div>
    );
  }
);
Textarea.displayName = "Textarea";

export { Textarea };
