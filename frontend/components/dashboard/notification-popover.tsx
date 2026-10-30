"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { Bell, CheckCircle2, Shield, AlertTriangle, FileText, Check } from "lucide-react";

interface NotificationItem {
  id: string;
  category: "approval" | "workflow" | "security" | "system";
  title: string;
  body: string;
  time: string;
  read: boolean;
  link?: string;
}

const INITIAL_NOTIFICATIONS: NotificationItem[] = [
  {
    id: "notif_1",
    category: "approval",
    title: "Dual-Approval Required",
    body: "Publish CS301 marks to Campus ERP requires your review.",
    time: "2m ago",
    read: false,
    link: "/approvals",
  },
  {
    id: "notif_2",
    category: "workflow",
    title: "Exam Marks Cycle Finished",
    body: "Ingested 47 student sheets with 98.4% verification rate.",
    time: "15m ago",
    read: false,
    link: "/workflows",
  },
  {
    id: "notif_3",
    category: "security",
    title: "Brute Force Throttled",
    body: "5 failed logins blocked for faculty account from unexpected subnet.",
    time: "1h ago",
    read: true,
    link: "/security",
  },
];

const categoryIcons = {
  approval: { icon: Shield, color: "text-[var(--color-status-waiting)] bg-[var(--color-status-waiting-bg)]" },
  workflow: { icon: CheckCircle2, color: "text-[var(--color-status-done)] bg-[var(--color-status-done-bg)]" },
  security: { icon: AlertTriangle, color: "text-[var(--color-status-failed)] bg-[var(--color-status-failed-bg)]" },
  system: { icon: FileText, color: "text-[var(--color-primary)] bg-[var(--color-primary-tint)]" },
};

/**
 * NotificationPopover — EPIC-12-T08 / EPIC-21
 *
 * Header notification bell with unread count indicator and actionable popover.
 */
export function NotificationPopover() {
  const [open, setOpen] = useState(false);
  const [items, setItems] = useState<NotificationItem[]>(INITIAL_NOTIFICATIONS);
  const popoverRef = useRef<HTMLDivElement>(null);

  const unreadCount = items.filter((i) => !i.read).length;

  const markAllRead = () => {
    setItems((prev) => prev.map((item) => ({ ...item, read: true })));
  };

  const markItemRead = (id: string) => {
    setItems((prev) => prev.map((item) => (item.id === id ? { ...item, read: true } : item)));
  };

  // Close when clicking outside
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (popoverRef.current && !popoverRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    if (open) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [open]);

  return (
    <div className="relative" ref={popoverRef}>
      <button
        onClick={() => setOpen((prev) => !prev)}
        className="relative rounded-[var(--radius-md)] p-2 text-[var(--color-ink-muted)] hover:bg-[var(--color-surface-sunken)] hover:text-[var(--color-ink)] transition-colors"
        aria-label={`Notifications (${unreadCount} unread)`}
        aria-expanded={open}
      >
        <Bell size={20} strokeWidth={1.75} />
        {unreadCount > 0 && (
          <span className="absolute right-1.5 top-1.5 flex h-4 min-w-[16px] items-center justify-center rounded-full bg-[var(--color-status-failed)] px-1 font-mono text-[10px] font-bold text-white ring-2 ring-[var(--color-surface)]">
            {unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div
          className="absolute right-0 top-full mt-2 w-80 sm:w-96 rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-surface)] shadow-[var(--shadow-lg)] z-50 overflow-hidden"
          role="region"
          aria-label="Notification center"
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b border-[var(--color-border)] px-4 py-3 bg-[var(--color-surface-sunken)]">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-[var(--color-ink)]">Notifications</span>
              {unreadCount > 0 && (
                <span className="rounded-full bg-[var(--color-primary-tint)] px-2 py-0.5 text-[10px] font-medium text-[var(--color-primary)]">
                  {unreadCount} new
                </span>
              )}
            </div>
            {unreadCount > 0 && (
              <button
                onClick={markAllRead}
                className="flex items-center gap-1 text-[11px] text-[var(--color-primary)] hover:underline"
              >
                <Check size={12} />
                <span>Mark all read</span>
              </button>
            )}
          </div>

          {/* List */}
          <div className="max-h-80 overflow-y-auto divide-y divide-[var(--color-border-subtle)]">
            {items.length === 0 ? (
              <div className="p-6 text-center text-xs text-[var(--color-ink-muted)]">
                No notifications right now.
              </div>
            ) : (
              items.map((item) => {
                const conf = categoryIcons[item.category];
                const Icon = conf.icon;
                return (
                  <div
                    key={item.id}
                    onClick={() => markItemRead(item.id)}
                    className={`flex items-start gap-3 p-3 text-left transition-colors hover:bg-[var(--color-surface-sunken)] ${
                      !item.read ? "bg-[var(--color-primary-tint)]/20" : ""
                    }`}
                  >
                    <div className={`mt-0.5 flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full text-xs ${conf.color}`}>
                      <Icon size={14} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-1">
                        <p className={`text-xs ${!item.read ? "font-semibold text-[var(--color-ink)]" : "font-medium text-[var(--color-ink)]"}`}>
                          {item.title}
                        </p>
                        <span className="text-[10px] text-[var(--color-ink-faint)] whitespace-nowrap">
                          {item.time}
                        </span>
                      </div>
                      <p className="mt-0.5 text-[11px] text-[var(--color-ink-muted)] line-clamp-2">
                        {item.body}
                      </p>
                      {item.link && (
                        <Link
                          href={item.link}
                          onClick={() => setOpen(false)}
                          className="mt-1 inline-block text-[10px] font-medium text-[var(--color-primary)] hover:underline"
                        >
                          View details →
                        </Link>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* Footer */}
          <div className="border-t border-[var(--color-border)] px-4 py-2 text-center bg-[var(--color-surface-sunken)]">
            <Link
              href="/settings"
              onClick={() => setOpen(false)}
              className="text-[11px] text-[var(--color-ink-muted)] hover:text-[var(--color-ink)] transition-colors"
            >
              Notification preferences
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
