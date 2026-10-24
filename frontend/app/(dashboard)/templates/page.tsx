"use client";

import { LayoutTemplate, GitBranch, ArrowRight, Plus } from "lucide-react";

/**
 * Templates — EPIC-22 (Template Gallery)
 */

const templates = [
  { slug: "exam-marks-processing", name: "Exam Marks Processing", desc: "Ingest → Evaluate → Verify → Approve → Publish → Notify", steps: 6, category: "Campus" },
  { slug: "leave-application", name: "Leave Application", desc: "Validate → Assess → Approve → Update → Confirm", steps: 5, category: "Campus" },
  { slug: "assignment-cycle", name: "Assignment Cycle", desc: "Classify → Mark → Sync → Detect Overdue → Notify", steps: 5, category: "Campus" },
  { slug: "security-incident", name: "Security Incident", desc: "Detect → Assess → Respond → Notify", steps: 4, category: "Platform" },
  { slug: "hr-leave-approval", name: "HR Leave Approval", desc: "Validate → Check Balance → Approve → Apply", steps: 4, category: "HR (Extensibility)" },
];

export default function TemplatesPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="font-heading text-2xl font-bold text-[var(--color-ink)]">Templates</h1>
          <p className="mt-1 text-sm text-[var(--color-ink-muted)]">Workflow-as-config templates</p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
        {templates.map((t) => (
          <div
            key={t.slug}
            className="group rounded-[var(--radius-lg)] border bg-[var(--color-surface)] p-5 transition-all hover:shadow-[var(--shadow-sm)] hover:border-[var(--color-border-strong)]"
            style={{ borderColor: "var(--color-border-subtle)" }}
          >
            <div className="flex items-center gap-3 mb-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-[var(--radius-md)] bg-[var(--color-primary-tint)]">
                <GitBranch size={16} className="text-[var(--color-primary)]" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-[var(--color-ink)]">{t.name}</h3>
                <p className="text-[11px] text-[var(--color-ink-faint)]">{t.category} · {t.steps} steps</p>
              </div>
            </div>
            <p className="text-xs text-[var(--color-ink-muted)] leading-relaxed">{t.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
