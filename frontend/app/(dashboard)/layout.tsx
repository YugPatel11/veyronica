"use client";

import { useState, useEffect, type ReactNode } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Network,
  GitBranch,
  CheckSquare,
  Plug,
  MessageSquare,
  ScrollText,
  TrendingUp,
  Coins,
  Shield,
  Settings,
  LayoutTemplate,
  Search,
  Bell,
  PanelLeftClose,
  PanelLeft,
  LogOut,
} from "lucide-react";
import { cn } from "@/lib/utils";

/** Navigation item configuration */
interface NavItem {
  label: string;
  href: string;
  icon: ReactNode;
  permission?: string;
}

const NAV_SECTIONS: { label: string; items: NavItem[] }[] = [
  {
    label: "Platform",
    items: [
      { label: "Mission Control", href: "/overview", icon: <LayoutDashboard size={20} strokeWidth={1.75} /> },
      { label: "Agent Map", href: "/agents", icon: <Network size={20} strokeWidth={1.75} /> },
      { label: "Workflows", href: "/workflows", icon: <GitBranch size={20} strokeWidth={1.75} /> },
      { label: "Approvals", href: "/approvals", icon: <CheckSquare size={20} strokeWidth={1.75} /> },
      { label: "Connected Systems", href: "/systems", icon: <Plug size={20} strokeWidth={1.75} /> },
    ],
  },
  {
    label: "Intelligence",
    items: [
      { label: "Copilot", href: "/copilot", icon: <MessageSquare size={20} strokeWidth={1.75} /> },
      { label: "Audit Explorer", href: "/audit", icon: <ScrollText size={20} strokeWidth={1.75} /> },
      { label: "Impact Analytics", href: "/impact", icon: <TrendingUp size={20} strokeWidth={1.75} /> },
      { label: "Token & Cost", href: "/usage", icon: <Coins size={20} strokeWidth={1.75} /> },
    ],
  },
  {
    label: "Admin",
    items: [
      { label: "Security", href: "/security", icon: <Shield size={20} strokeWidth={1.75} /> },
      { label: "Templates", href: "/templates", icon: <LayoutTemplate size={20} strokeWidth={1.75} /> },
      { label: "Settings", href: "/settings", icon: <Settings size={20} strokeWidth={1.75} /> },
    ],
  },
];

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);

  // Ctrl+K to open command palette
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setCommandPaletteOpen((prev) => !prev);
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <div className="flex min-h-screen">
      {/* ── Sidebar ──────────────────────────────────────────────────── */}
      <aside
        className={cn(
          "fixed left-0 top-0 z-30 flex h-screen flex-col border-r bg-surface transition-all duration-200",
          collapsed ? "w-[var(--sidebar-width-collapsed)]" : "w-[var(--sidebar-width)]"
        )}
        style={{ borderColor: "var(--color-border)" }}
      >
        {/* Logo area */}
        <div className="flex h-14 items-center gap-3 border-b px-4" style={{ borderColor: "var(--color-border)" }}>
          <div
            className="flex h-8 w-8 items-center justify-center rounded-[var(--radius-md)] text-sm font-bold text-white"
            style={{ backgroundColor: "var(--color-primary)" }}
          >
            N
          </div>
          {!collapsed && (
            <span className="font-heading text-lg font-bold" style={{ color: "var(--color-primary)" }}>
              NEXUS
            </span>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto px-2 py-3" aria-label="Main navigation">
          {NAV_SECTIONS.map((section) => (
            <div key={section.label} className="mb-4">
              {!collapsed && (
                <p className="mb-1 px-3 text-[11px] font-medium uppercase tracking-wider text-ink-faint">
                  {section.label}
                </p>
              )}
              <ul className="space-y-0.5">
                {section.items.map((item) => {
                  const isActive = pathname === item.href;
                  return (
                    <li key={item.href}>
                      <Link
                        href={item.href}
                        className={cn(
                          "flex items-center gap-3 rounded-[var(--radius-md)] px-3 py-2 text-sm transition-colors duration-100",
                          collapsed && "justify-center px-0",
                          isActive
                            ? "font-medium"
                            : "text-ink-muted hover:text-ink"
                        )}
                        style={{
                          backgroundColor: isActive ? "var(--color-primary-tint)" : undefined,
                          color: isActive ? "var(--color-primary)" : undefined,
                        }}
                        title={collapsed ? item.label : undefined}
                        aria-current={isActive ? "page" : undefined}
                      >
                        {item.icon}
                        {!collapsed && <span>{item.label}</span>}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </nav>

        {/* Collapse toggle */}
        <div className="border-t p-2" style={{ borderColor: "var(--color-border)" }}>
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="flex w-full items-center justify-center rounded-[var(--radius-md)] p-2 text-ink-muted hover:bg-surface-sunken hover:text-ink transition-colors"
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {collapsed ? <PanelLeft size={20} /> : <PanelLeftClose size={20} />}
          </button>
        </div>
      </aside>

      {/* ── Main Content ─────────────────────────────────────────────── */}
      <div
        className={cn(
          "flex flex-1 flex-col transition-all duration-200",
          collapsed ? "ml-[var(--sidebar-width-collapsed)]" : "ml-[var(--sidebar-width)]"
        )}
      >
        {/* Header */}
        <header
          className="sticky top-0 z-20 flex h-14 items-center justify-between border-b bg-surface px-6"
          style={{ borderColor: "var(--color-border)" }}
        >
          {/* Left: breadcrumb placeholder */}
          <div className="text-sm text-ink-muted">
            {/* Breadcrumbs populated per-page in Phase 3 */}
          </div>

          {/* Right: search, notifications, user */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setCommandPaletteOpen(true)}
              className="flex items-center gap-2 rounded-[var(--radius-md)] border px-3 py-1.5 text-sm text-ink-muted transition-colors hover:border-[var(--color-border-strong)] hover:text-ink"
              style={{ borderColor: "var(--color-border)" }}
            >
              <Search size={16} strokeWidth={1.75} />
              <span className="hidden sm:inline">Search</span>
              <kbd className="hidden rounded-[var(--radius-sm)] border bg-surface-sunken px-1.5 py-0.5 font-mono text-[10px] sm:inline" style={{ borderColor: "var(--color-border)" }}>
                ⌘K
              </kbd>
            </button>

            <button
              className="relative rounded-[var(--radius-md)] p-2 text-ink-muted hover:bg-surface-sunken hover:text-ink transition-colors"
              aria-label="Notifications"
            >
              <Bell size={20} strokeWidth={1.75} />
            </button>

            <button
              className="rounded-[var(--radius-md)] p-2 text-ink-muted hover:bg-surface-sunken hover:text-ink transition-colors"
              aria-label="Sign out"
              onClick={() => {
                if (typeof window !== "undefined") {
                  sessionStorage.clear();
                  window.location.href = "/";
                }
              }}
            >
              <LogOut size={20} strokeWidth={1.75} />
            </button>
          </div>
        </header>

        {/* Page content */}
        <main id="main-content" className="flex-1 p-6 lg:p-8">
          {children}
        </main>
      </div>

      {/* ── Command Palette (Ctrl+K) ─────────────────────────────────── */}
      {commandPaletteOpen && (
        <div
          className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]"
          onClick={() => setCommandPaletteOpen(false)}
        >
          {/* Backdrop */}
          <div className="absolute inset-0 bg-black/20" />

          {/* Palette */}
          <div
            className="relative w-full max-w-lg rounded-[var(--radius-lg)] bg-surface shadow-[var(--shadow-lg)]"
            style={{ border: "1px solid var(--color-border)" }}
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-label="Command palette"
          >
            <div className="flex items-center gap-3 border-b px-4 py-3" style={{ borderColor: "var(--color-border)" }}>
              <Search size={18} className="text-ink-muted" strokeWidth={1.75} />
              <input
                autoFocus
                type="text"
                placeholder="Search pages, runs, approvals…"
                className="flex-1 bg-transparent text-sm text-ink placeholder:text-ink-disabled outline-none"
                onKeyDown={(e) => {
                  if (e.key === "Escape") setCommandPaletteOpen(false);
                }}
              />
              <kbd className="rounded-[var(--radius-sm)] border bg-surface-sunken px-1.5 py-0.5 font-mono text-[10px] text-ink-muted" style={{ borderColor: "var(--color-border)" }}>
                ESC
              </kbd>
            </div>
            <div className="px-2 py-3">
              <p className="px-2 text-xs font-medium uppercase tracking-wider text-ink-faint">
                Quick Navigation
              </p>
              <ul className="mt-1 space-y-0.5">
                {NAV_SECTIONS.flatMap((s) => s.items)
                  .slice(0, 6)
                  .map((item) => (
                    <li key={item.href}>
                      <Link
                        href={item.href}
                        onClick={() => setCommandPaletteOpen(false)}
                        className="flex items-center gap-3 rounded-[var(--radius-md)] px-3 py-2 text-sm text-ink-muted transition-colors hover:bg-surface-sunken hover:text-ink"
                      >
                        {item.icon}
                        {item.label}
                      </Link>
                    </li>
                  ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
