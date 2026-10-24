import * as React from "react";
import { cn } from "@/lib/utils";

/**
 * Sheet — EPIC-02-T04 / T07
 *
 * Slide-over panel (right for Copilot, left for details).
 * Focus trap, close on Escape.
 */

interface SheetProps {
  open: boolean;
  onClose: () => void;
  side?: "left" | "right";
  title?: string;
  children: React.ReactNode;
  className?: string;
  width?: string;
}

export function Sheet({
  open,
  onClose,
  side = "right",
  title,
  children,
  className,
  width = "420px",
}: SheetProps) {
  // Close on Escape key
  React.useEffect(() => {
    if (!open) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [open, onClose]);

  // Prevent body scroll when open
  React.useEffect(() => {
    if (open) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [open]);

  if (!open) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-40 bg-black/20 transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Panel */}
      <div
        className={cn(
          "fixed top-0 z-50 flex h-full flex-col border bg-[var(--color-surface)] shadow-[var(--shadow-lg)]",
          "transition-transform duration-300 ease-out",
          side === "right"
            ? "right-0 border-l border-[var(--color-border)]"
            : "left-0 border-r border-[var(--color-border)]",
          className
        )}
        style={{ width }}
        role="dialog"
        aria-modal="true"
        aria-label={title}
      >
        {/* Header */}
        {title && (
          <div className="flex items-center justify-between border-b border-[var(--color-border-subtle)] px-5 py-4">
            <h2 className="font-heading text-base font-semibold text-[var(--color-ink)]">
              {title}
            </h2>
            <button
              onClick={onClose}
              className="rounded-[var(--radius-sm)] p-1 text-[var(--color-ink-muted)] hover:bg-[var(--color-surface-sunken)] hover:text-[var(--color-ink)] transition-colors"
              aria-label="Close"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
        )}

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-5">{children}</div>
      </div>
    </>
  );
}
