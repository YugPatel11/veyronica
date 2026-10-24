"use client";

import {
  GitBranch,
  ArrowRight,
  Play,
  Clock,
  Layers,
  Zap,
} from "lucide-react";
import { StatusBadge } from "@/components/ui/status-badge";

/**
 * Workflows page — EPIC-14-T05 (Workflow Studio read-only)
 *
 * Lists workflow definitions and recent runs.
 */

interface WorkflowDef {
  slug: string;
  name: string;
  description: string;
  trigger: string;
  stepsCount: number;
  autonomyDefault: string;
  runsToday: number;
  status: "active" | "draft";
}

const WORKFLOW_DEFS: WorkflowDef[] = [
  {
    slug: "exam-marks-processing",
    name: "Exam Marks Processing",
    description: "End-to-end exam marks ingestion, evaluation, verification, and publication",
    trigger: "manual",
    stepsCount: 6,
    autonomyDefault: "supervised",
    runsToday: 3,
    status: "active",
  },
  {
    slug: "leave-application",
    name: "Leave Application Processing",
    description: "Student leave application review and processing",
    trigger: "webhook",
    stepsCount: 5,
    autonomyDefault: "supervised",
    runsToday: 1,
    status: "active",
  },
  {
    slug: "assignment-cycle",
    name: "Assignment Cycle",
    description: "Assignment submission classification, marking, and notification",
    trigger: "webhook",
    stepsCount: 5,
    autonomyDefault: "supervised",
    runsToday: 0,
    status: "draft",
  },
  {
    slug: "security-incident",
    name: "Security Incident Response",
    description: "Detect, assess, and respond to security events automatically",
    trigger: "webhook",
    stepsCount: 4,
    autonomyDefault: "supervised",
    runsToday: 0,
    status: "draft",
  },
];

const triggerConfig: Record<string, { icon: typeof Play; label: string }> = {
  manual: { icon: Play, label: "Manual" },
  webhook: { icon: Zap, label: "Webhook" },
  scheduled: { icon: Clock, label: "Scheduled" },
  copilot: { icon: Layers, label: "Copilot" },
};

export default function WorkflowsPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-end justify-between">
        <div>
          <h1 className="font-heading text-2xl font-bold text-[var(--color-ink)]">
            Workflows
          </h1>
          <p className="mt-1 text-sm text-[var(--color-ink-muted)]">
            Workflow definitions and execution templates
          </p>
        </div>
      </div>

      {/* Workflow Cards Grid */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {WORKFLOW_DEFS.map((wf) => {
          const trigger = triggerConfig[wf.trigger] ?? triggerConfig.manual;
          const TriggerIcon = trigger.icon;
          return (
            <div
              key={wf.slug}
              className="group rounded-[var(--radius-lg)] border bg-[var(--color-surface)] p-5 transition-all hover:shadow-[var(--shadow-sm)] hover:border-[var(--color-border-strong)]"
              style={{ borderColor: "var(--color-border-subtle)" }}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div
                    className="flex h-10 w-10 items-center justify-center rounded-[var(--radius-md)]"
                    style={{ backgroundColor: "var(--color-primary-tint)" }}
                  >
                    <GitBranch size={20} className="text-[var(--color-primary)]" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-[var(--color-ink)]">{wf.name}</h3>
                    <div className="mt-0.5 flex items-center gap-2 text-[11px] text-[var(--color-ink-faint)]">
                      <span className="flex items-center gap-1">
                        <TriggerIcon size={10} />
                        {trigger.label}
                      </span>
                      <span>·</span>
                      <span>{wf.stepsCount} steps</span>
                      <span>·</span>
                      <span>{wf.autonomyDefault}</span>
                    </div>
                  </div>
                </div>

                <span
                  className={`rounded-full px-2 py-0.5 text-[11px] font-medium ${
                    wf.status === "active"
                      ? "bg-[var(--color-status-done-bg)] text-[var(--color-status-done)]"
                      : "bg-[var(--color-surface-sunken)] text-[var(--color-ink-disabled)]"
                  }`}
                >
                  {wf.status === "active" ? "Active" : "Draft"}
                </span>
              </div>

              <p className="mt-3 text-xs text-[var(--color-ink-muted)] leading-relaxed">
                {wf.description}
              </p>

              <div className="mt-4 flex items-center justify-between border-t pt-3" style={{ borderColor: "var(--color-border-subtle)" }}>
                <span className="font-mono text-xs text-[var(--color-ink-faint)]">
                  {wf.runsToday > 0 ? `${wf.runsToday} runs today` : "No runs today"}
                </span>
                <button
                  className="flex items-center gap-1 text-xs font-medium opacity-0 transition-all group-hover:opacity-100"
                  style={{ color: "var(--color-primary)" }}
                >
                  View Details <ArrowRight size={12} />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
