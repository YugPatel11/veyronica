"use client";

import { Toaster as Sonner, toast } from "sonner";

/**
 * Toast — EPIC-02-T08
 *
 * Uses Sonner with NEXUS theme. Bottom-right, auto-dismiss 5s.
 */

function Toaster() {
  return (
    <Sonner
      position="bottom-right"
      duration={5000}
      closeButton
      toastOptions={{
        style: {
          background: "var(--color-surface)",
          border: "1px solid var(--color-border)",
          color: "var(--color-ink)",
          fontFamily: "var(--font-body)",
          fontSize: "14px",
          borderRadius: "var(--radius-md)",
          boxShadow: "var(--shadow-lg)",
        },
        classNames: {
          title: "font-medium",
          description: "text-[var(--color-ink-muted)]",
        },
      }}
    />
  );
}

export { Toaster, toast };
