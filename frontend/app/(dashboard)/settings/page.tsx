"use client";

import { Settings as SettingsIcon, User, Bell, Shield, Palette } from "lucide-react";

/**
 * Settings — EPIC-12 (Settings page)
 */
export default function SettingsPage() {
  const sections = [
    { icon: User, label: "Profile", desc: "Name, email, and role information" },
    { icon: Bell, label: "Notifications", desc: "Email, Telegram, and in-app preferences" },
    { icon: Shield, label: "Security", desc: "Password, MFA, and session management" },
    { icon: Palette, label: "Display", desc: "Theme, presenter mode, and layout preferences" },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-heading text-2xl font-bold text-[var(--color-ink)]">Settings</h1>
        <p className="mt-1 text-sm text-[var(--color-ink-muted)]">Account and platform configuration</p>
      </div>

      <div className="space-y-3">
        {sections.map((s) => (
          <button
            key={s.label}
            className="flex w-full items-center gap-4 rounded-[var(--radius-lg)] border bg-[var(--color-surface)] p-5 text-left transition-all hover:shadow-[var(--shadow-sm)] hover:border-[var(--color-border-strong)]"
            style={{ borderColor: "var(--color-border-subtle)" }}
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-[var(--radius-md)] bg-[var(--color-surface-sunken)]">
              <s.icon size={20} className="text-[var(--color-ink-muted)]" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-[var(--color-ink)]">{s.label}</h3>
              <p className="text-xs text-[var(--color-ink-muted)]">{s.desc}</p>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
