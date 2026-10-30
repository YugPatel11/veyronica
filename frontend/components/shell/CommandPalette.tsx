"use client";

import { useState, useMemo } from "react";
import Link from "next/link";
import { Search, Sparkles, CheckSquare, GitBranch } from "lucide-react";
import { NAV_SECTIONS } from "./Sidebar";

interface CommandPaletteProps {
  open: boolean;
  onClose: () => void;
  onOpenCopilot?: () => void;
}

export function CommandPalette({ open, onClose, onOpenCopilot }: CommandPaletteProps) {
  const [query, setQuery] = useState("");

  const searchItems = useMemo(() => {
    const navItems = NAV_SECTIONS.flatMap((s) => s.items).map((item) => ({
      type: "page",
      label: item.label,
      href: item.href,
      icon: item.icon,
    }));

    const quickActions = [
      {
        type: "action",
        label: "Open Nexus Copilot Assistant",
        action: () => {
          onClose();
          onOpenCopilot?.();
        },
        icon: <Sparkles size={18} className="text-primary" />,
      },
      {
        type: "run",
        label: "Active Run: #RUN-2026-EXAM-01",
        href: "/workflows",
        icon: <GitBranch size={18} className="text-secondary" />,
      },
      {
        type: "approval",
        label: "Pending Approval: Grade Moderation batch #4",
        href: "/approvals",
        icon: <CheckSquare size={18} className="text-amber-500" />,
      },
    ];

    return [...navItems, ...quickActions];
  }, [onClose, onOpenCopilot]);

  const filteredItems = useMemo(() => {
    if (!query.trim()) return searchItems.slice(0, 8);
    const q = query.toLowerCase();
    return searchItems.filter((i) => i.label.toLowerCase().includes(q));
  }, [searchItems, query]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label="Command palette"
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/40 backdrop-blur-xs transition-opacity" />

      {/* Dialog box */}
      <div
        className="relative w-full max-w-lg rounded-[var(--radius-lg)] bg-surface shadow-[var(--shadow-lg)] overflow-hidden border"
        style={{ borderColor: "var(--color-border)" }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-3 border-b px-4 py-3" style={{ borderColor: "var(--color-border)" }}>
          <Search size={18} className="text-ink-muted" strokeWidth={1.75} />
          <input
            autoFocus
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search pages, active runs, approvals, or actions…"
            className="flex-1 bg-transparent text-sm text-ink placeholder:text-ink-disabled outline-none"
            onKeyDown={(e) => {
              if (e.key === "Escape") onClose();
            }}
          />
          <kbd
            className="rounded-[var(--radius-sm)] border bg-surface-sunken px-1.5 py-0.5 font-mono text-[10px] text-ink-muted cursor-pointer hover:bg-surface"
            style={{ borderColor: "var(--color-border)" }}
            onClick={onClose}
          >
            ESC
          </kbd>
        </div>

        <div className="p-2 max-h-80 overflow-y-auto">
          {filteredItems.length === 0 ? (
            <div className="py-8 text-center text-xs text-ink-muted">
              No results found for &quot;{query}&quot;
            </div>
          ) : (
            <ul className="space-y-0.5">
              {filteredItems.map((item, idx) => (
                <li key={idx}>
                  {"href" in item && item.href ? (
                    <Link
                      href={item.href}
                      onClick={onClose}
                      className="flex items-center gap-3 rounded-[var(--radius-md)] px-3 py-2 text-sm text-ink-muted transition-colors hover:bg-surface-sunken hover:text-ink"
                    >
                      {item.icon}
                      <span className="flex-1 truncate">{item.label}</span>
                      <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded border border-border text-ink-faint">
                        {item.type}
                      </span>
                    </Link>
                  ) : (
                    <button
                      onClick={"action" in item ? item.action : undefined}
                      className="w-full flex items-center gap-3 rounded-[var(--radius-md)] px-3 py-2 text-sm text-ink-muted transition-colors hover:bg-surface-sunken hover:text-ink text-left"
                    >
                      {item.icon}
                      <span className="flex-1 truncate">{item.label}</span>
                      <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded border border-border text-ink-faint">
                        action
                      </span>
                    </button>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
