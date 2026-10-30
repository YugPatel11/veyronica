"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronRight, Home } from "lucide-react";

const ROUTE_MAP: Record<string, { section: string; label: string }> = {
  "/overview": { section: "Platform", label: "Mission Control" },
  "/agents": { section: "Platform", label: "Agent Map" },
  "/workflows": { section: "Platform", label: "Workflows" },
  "/approvals": { section: "Platform", label: "Approvals" },
  "/systems": { section: "Platform", label: "Connected Systems" },
  "/copilot": { section: "Intelligence", label: "Copilot" },
  "/audit": { section: "Intelligence", label: "Audit Explorer" },
  "/impact": { section: "Intelligence", label: "Impact Analytics" },
  "/usage": { section: "Intelligence", label: "Token & Cost" },
  "/security": { section: "Admin", label: "Security Center" },
  "/templates": { section: "Admin", label: "Templates" },
  "/settings": { section: "Admin", label: "Settings" },
};

/**
 * Breadcrumbs — EPIC-12-T05
 *
 * Clean, accessible breadcrumb navigation trail matching dashboard hierarchy.
 */
export function Breadcrumbs() {
  const pathname = usePathname();
  const route = ROUTE_MAP[pathname];

  if (!route) {
    return (
      <div className="flex items-center gap-1.5 text-xs text-[var(--color-ink-muted)]">
        <Link href="/overview" className="flex items-center gap-1 hover:text-[var(--color-ink)] transition-colors">
          <Home size={13} />
          <span>NEXUS</span>
        </Link>
      </div>
    );
  }

  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-1.5 text-xs text-[var(--color-ink-muted)]">
      <Link
        href="/overview"
        className="flex items-center gap-1 hover:text-[var(--color-ink)] transition-colors"
        aria-label="Dashboard Home"
      >
        <Home size={13} />
        <span>NEXUS</span>
      </Link>
      <ChevronRight size={12} className="text-[var(--color-ink-faint)]" />
      <span className="font-medium text-[var(--color-ink-faint)]">{route.section}</span>
      <ChevronRight size={12} className="text-[var(--color-ink-faint)]" />
      <span className="font-semibold text-[var(--color-ink)]" aria-current="page">
        {route.label}
      </span>
    </nav>
  );
}
