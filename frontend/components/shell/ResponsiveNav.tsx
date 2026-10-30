"use client";

import { useEffect, useState, type ReactNode } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Menu, X } from "lucide-react";
import { NAV_SECTIONS } from "./Sidebar";

interface ResponsiveNavProps {
  children?: ReactNode;
}

export function ResponsiveNav({ children }: ResponsiveNavProps) {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  // Close mobile drawer whenever route changes
  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  return (
    <>
      {/* Mobile Drawer Trigger */}
      <button
        onClick={() => setMobileOpen(true)}
        className="rounded-[var(--radius-md)] p-1.5 text-ink-muted hover:bg-surface-sunken hover:text-ink md:hidden"
        aria-label="Open mobile navigation menu"
      >
        <Menu size={20} strokeWidth={1.75} />
      </button>

      {/* Mobile Drawer Modal */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 md:hidden" role="dialog" aria-modal="true">
          <div
            className="fixed inset-0 bg-black/40 backdrop-blur-xs transition-opacity"
            onClick={() => setMobileOpen(false)}
          />
          <aside
            className="fixed inset-y-0 left-0 w-72 flex flex-col bg-surface border-r shadow-2xl z-50 p-4"
            style={{ borderColor: "var(--color-border)" }}
          >
            <div className="flex h-12 items-center justify-between border-b pb-3" style={{ borderColor: "var(--color-border)" }}>
              <div className="flex items-center gap-2">
                <div
                  className="flex h-7 w-7 items-center justify-center rounded-[var(--radius-md)] text-xs font-bold text-white"
                  style={{ backgroundColor: "var(--color-primary)" }}
                >
                  N
                </div>
                <span className="font-heading text-base font-bold" style={{ color: "var(--color-primary)" }}>
                  NEXUS
                </span>
              </div>
              <button
                onClick={() => setMobileOpen(false)}
                className="rounded p-1 text-ink-muted hover:bg-surface-sunken hover:text-ink"
                aria-label="Close navigation menu"
              >
                <X size={18} />
              </button>
            </div>

            <nav className="mt-4 flex-1 overflow-y-auto space-y-4">
              {NAV_SECTIONS.map((section) => (
                <div key={section.label}>
                  <p className="px-3 text-[10px] font-semibold uppercase tracking-wider text-ink-faint">
                    {section.label}
                  </p>
                  <ul className="mt-1 space-y-0.5">
                    {section.items.map((item) => {
                      const isActive = pathname === item.href;
                      return (
                        <li key={item.href}>
                          <Link
                            href={item.href}
                            onClick={() => setMobileOpen(false)}
                            className="flex items-center gap-3 rounded-[var(--radius-md)] px-3 py-2 text-sm text-ink-muted transition-colors hover:bg-surface-sunken hover:text-ink"
                            style={{
                              backgroundColor: isActive ? "var(--color-primary-tint)" : undefined,
                              color: isActive ? "var(--color-primary)" : undefined,
                            }}
                          >
                            {item.icon}
                            {item.label}
                          </Link>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              ))}
            </nav>
            {children}
          </aside>
        </div>
      )}
    </>
  );
}
