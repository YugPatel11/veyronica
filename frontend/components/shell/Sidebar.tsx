"use client";

import { type ReactNode } from "react";
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
  PanelLeftClose,
  PanelLeft,
} from "lucide-react";
import { cn } from "@/lib/utils";

export interface NavItem {
  label: string;
  href: string;
  icon: ReactNode;
  roles?: string[];
}

export interface NavSection {
  label: string;
  items: NavItem[];
}

export const NAV_SECTIONS: NavSection[] = [
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
      { label: "Security", href: "/security", icon: <Shield size={20} strokeWidth={1.75} />, roles: ["admin", "superadmin"] },
      { label: "Templates", href: "/templates", icon: <LayoutTemplate size={20} strokeWidth={1.75} />, roles: ["admin", "superadmin", "coordinator"] },
      { label: "Settings", href: "/settings", icon: <Settings size={20} strokeWidth={1.75} /> },
    ],
  },
];

interface SidebarProps {
  collapsed: boolean;
  onToggleCollapse: () => void;
  userRole?: string;
}

export function Sidebar({ collapsed, onToggleCollapse, userRole = "admin" }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        "fixed left-0 top-0 z-30 flex h-screen flex-col border-r bg-surface transition-all duration-200",
        collapsed ? "w-[var(--sidebar-width-collapsed)]" : "w-[var(--sidebar-width)]"
      )}
      style={{ borderColor: "var(--color-border)" }}
      aria-label="Sidebar navigation"
    >
      {/* Brand logo */}
      <div className="flex h-14 items-center gap-3 border-b px-4" style={{ borderColor: "var(--color-border)" }}>
        <div
          className="flex h-8 w-8 items-center justify-center rounded-[var(--radius-md)] text-sm font-bold text-white shadow-sm"
          style={{ backgroundColor: "var(--color-primary)" }}
        >
          N
        </div>
        {!collapsed && (
          <span className="font-heading text-lg font-bold tracking-tight" style={{ color: "var(--color-primary)" }}>
            NEXUS
          </span>
        )}
      </div>

      {/* Role-filtered navigation links */}
      <nav className="flex-1 overflow-y-auto px-2 py-3" aria-label="Main navigation">
        {NAV_SECTIONS.map((section) => {
          const visibleItems = section.items.filter(
            (item) => !item.roles || item.roles.includes(userRole)
          );
          if (!visibleItems.length) return null;

          return (
            <div key={section.label} className="mb-4">
              {!collapsed && (
                <p className="mb-1 px-3 text-[11px] font-medium uppercase tracking-wider text-ink-faint">
                  {section.label}
                </p>
              )}
              <ul className="space-y-0.5">
                {visibleItems.map((item) => {
                  const isActive = pathname === item.href;
                  return (
                    <li key={item.href}>
                      <Link
                        href={item.href}
                        className={cn(
                          "flex items-center gap-3 rounded-[var(--radius-md)] px-3 py-2 text-sm transition-colors duration-100",
                          collapsed && "justify-center px-0",
                          isActive ? "font-medium" : "text-ink-muted hover:text-ink hover:bg-surface-sunken"
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
          );
        })}
      </nav>

      {/* Collapse toggle */}
      <div className="border-t p-2" style={{ borderColor: "var(--color-border)" }}>
        <button
          onClick={onToggleCollapse}
          className="flex w-full items-center justify-center rounded-[var(--radius-md)] p-2 text-ink-muted hover:bg-surface-sunken hover:text-ink transition-colors"
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? <PanelLeft size={20} /> : <PanelLeftClose size={20} />}
        </button>
      </div>
    </aside>
  );
}
