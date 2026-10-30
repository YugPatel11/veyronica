"use client";

import { useState, type ReactNode } from "react";
import { Search, Sparkles, LogOut } from "lucide-react";
import { Sidebar } from "./Sidebar";
import { CommandPalette } from "./CommandPalette";
import { CopilotSheet } from "./CopilotSheet";
import { Breadcrumbs } from "./Breadcrumbs";
import { ResponsiveNav } from "./ResponsiveNav";
import { KeyboardNav } from "./KeyboardNav";
import { NotificationPopover } from "@/components/dashboard/notification-popover";
import { cn } from "@/lib/utils";

interface AppShellProps {
  children: ReactNode;
  userRole?: string;
}

export function AppShell({ children, userRole = "admin" }: AppShellProps) {
  const [collapsed, setCollapsed] = useState(false);
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [copilotOpen, setCopilotOpen] = useState(false);

  const handleCloseAll = () => {
    setCommandPaletteOpen(false);
    setCopilotOpen(false);
  };

  return (
    <div className="flex min-h-screen">
      {/* Keyboard Shortcuts Listener */}
      <KeyboardNav
        onToggleCommandPalette={() => setCommandPaletteOpen((prev) => !prev)}
        onToggleCopilot={() => setCopilotOpen((prev) => !prev)}
        onCloseAllModals={handleCloseAll}
      />

      {/* Role-aware Collapsible Sidebar */}
      <Sidebar
        collapsed={collapsed}
        onToggleCollapse={() => setCollapsed(!collapsed)}
        userRole={userRole}
      />

      {/* Main Container */}
      <div
        className={cn(
          "flex flex-1 flex-col transition-all duration-200",
          collapsed ? "ml-[var(--sidebar-width-collapsed)]" : "ml-[var(--sidebar-width)]"
        )}
      >
        {/* Header Bar */}
        <header
          className="sticky top-0 z-20 flex h-14 items-center justify-between border-b bg-surface px-4 sm:px-6"
          style={{ borderColor: "var(--color-border)" }}
        >
          {/* Left: Mobile hamburger & breadcrumbs */}
          <div className="flex items-center gap-2 sm:gap-3 min-w-0">
            <ResponsiveNav />
            <Breadcrumbs />
          </div>

          {/* Right: Search trigger, Copilot, Notifications, Sign out */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setCommandPaletteOpen(true)}
              className="flex items-center gap-2 rounded-[var(--radius-md)] border px-3 py-1.5 text-sm text-ink-muted transition-colors hover:border-[var(--color-border-strong)] hover:text-ink"
              style={{ borderColor: "var(--color-border)" }}
              aria-label="Open search palette (⌘K)"
            >
              <Search size={16} strokeWidth={1.75} />
              <span className="hidden sm:inline">Search</span>
              <kbd className="hidden rounded-[var(--radius-sm)] border bg-surface-sunken px-1.5 py-0.5 font-mono text-[10px] sm:inline" style={{ borderColor: "var(--color-border)" }}>
                ⌘K
              </kbd>
            </button>

            <button
              onClick={() => setCopilotOpen(true)}
              className="flex items-center gap-1.5 rounded-[var(--radius-md)] border px-2.5 py-1.5 text-xs font-medium text-ink-muted transition-colors hover:border-[var(--color-primary)] hover:text-[var(--color-primary)]"
              style={{ borderColor: "var(--color-border)" }}
              aria-label="Open Nexus Copilot (⌘J)"
            >
              <Sparkles size={14} className="text-[var(--color-primary)]" />
              <span className="hidden sm:inline">Copilot</span>
              <kbd className="hidden font-mono text-[10px] text-ink-faint md:inline">⌘J</kbd>
            </button>

            <NotificationPopover />

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

        {/* Page Content */}
        <main id="main-content" className="flex-1 p-6 lg:p-8">
          {children}
        </main>
      </div>

      {/* Global Command Palette */}
      <CommandPalette
        open={commandPaletteOpen}
        onClose={() => setCommandPaletteOpen(false)}
        onOpenCopilot={() => setCopilotOpen(true)}
      />

      {/* Global Copilot Slide-over Sheet */}
      <CopilotSheet open={copilotOpen} onClose={() => setCopilotOpen(false)} />
    </div>
  );
}
