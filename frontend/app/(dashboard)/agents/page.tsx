"use client";

import { Network, CircleDot } from "lucide-react";

/**
 * Agent Map — EPIC-13-T02 placeholder
 *
 * Will use React Flow for interactive agent canvas.
 */
export default function AgentsPage() {
  const agents = [
    { id: "master", name: "Master Agent", status: "active", role: "Orchestrator" },
    { id: "ingestion", name: "Ingestion Agent", status: "active", role: "OCR & extraction" },
    { id: "evaluation", name: "Evaluation Agent", status: "busy", role: "Marking & grading" },
    { id: "verifier", name: "Verifier Agent", status: "idle", role: "Cross-checking" },
    { id: "analysis", name: "Analysis Agent", status: "idle", role: "Trends & risk" },
    { id: "communication", name: "Communication Agent", status: "idle", role: "Notifications" },
    { id: "copilot", name: "Copilot Agent", status: "active", role: "Ad-hoc queries" },
    { id: "security", name: "Security Agent", status: "monitoring", role: "Incident response" },
  ];

  const statusStyle: Record<string, string> = {
    active: "bg-[var(--color-status-done)]",
    busy: "bg-[var(--color-status-running)]",
    idle: "bg-[var(--color-border-strong)]",
    monitoring: "bg-[var(--color-status-waiting)]",
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-heading text-2xl font-bold text-[var(--color-ink)]">Agent Map</h1>
        <p className="mt-1 text-sm text-[var(--color-ink-muted)]">Specialist agents and their current state</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {agents.map((a) => (
          <div
            key={a.id}
            className="rounded-[var(--radius-lg)] border bg-[var(--color-surface)] p-5 transition-shadow hover:shadow-[var(--shadow-sm)]"
            style={{ borderColor: "var(--color-border-subtle)" }}
          >
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[var(--color-primary-tint)]">
                <Network size={18} className="text-[var(--color-primary)]" />
              </div>
              <div className="flex-1">
                <h3 className="text-sm font-semibold text-[var(--color-ink)]">{a.name}</h3>
                <p className="text-[11px] text-[var(--color-ink-faint)]">{a.role}</p>
              </div>
              <div className={`h-2.5 w-2.5 rounded-full ${statusStyle[a.status] ?? statusStyle.idle}`} title={a.status} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
