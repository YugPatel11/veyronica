import * as React from "react";
import { cn } from "@/lib/utils";

/**
 * Avatar — EPIC-02-T04
 *
 * Variants: image, initials, icon. With alt text for a11y.
 */

interface AvatarProps {
  src?: string | null;
  alt?: string;
  name?: string;
  size?: "sm" | "md" | "lg";
  className?: string;
}

const sizeMap = {
  sm: "h-7 w-7 text-[10px]",
  md: "h-9 w-9 text-xs",
  lg: "h-11 w-11 text-sm",
};

function getInitials(name: string): string {
  return name
    .split(" ")
    .map((w) => w[0])
    .filter(Boolean)
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

// Deterministic color from name
function getAvatarColor(name: string): string {
  const colors = [
    "var(--color-primary)",
    "var(--color-status-done)",
    "var(--color-status-running)",
    "var(--color-saffron)",
    "#8B5CF6",
    "#EC4899",
    "#14B8A6",
  ];
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return colors[Math.abs(hash) % colors.length];
}

export function Avatar({ src, alt, name, size = "md", className }: AvatarProps) {
  const initials = name ? getInitials(name) : "?";
  const bgColor = name ? getAvatarColor(name) : "var(--color-ink-muted)";

  if (src) {
    return (
      <img
        src={src}
        alt={alt || name || "Avatar"}
        className={cn(
          "rounded-full object-cover ring-2 ring-[var(--color-surface)] ring-offset-0",
          sizeMap[size],
          className
        )}
      />
    );
  }

  return (
    <span
      className={cn(
        "inline-flex items-center justify-center rounded-full font-semibold text-white ring-2 ring-[var(--color-surface)] ring-offset-0",
        sizeMap[size],
        className
      )}
      style={{ backgroundColor: bgColor }}
      role="img"
      aria-label={alt || name || "Avatar"}
    >
      {initials}
    </span>
  );
}
