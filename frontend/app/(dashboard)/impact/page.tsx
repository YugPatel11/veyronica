"use client";

import { TrendingUp, Clock, Zap, Users, BarChart3 } from "lucide-react";
import { StatCard } from "@/components/ui/stat-card";
import { ProgressBar } from "@/components/ui/progress-bar";

/**
 * Impact Analytics — EPIC-20-T01/T02
 *
 * Impact stats, time saved breakdown, manual vs automated bar chart.
 */

const timeBreakdown = [
  { label: "Exam Processing", manual: 4.2, automated: 0.8, saved: 3.4 },
  { label: "Assignment Cycle", manual: 2.5, automated: 0.4, saved: 2.1 },
  { label: "Leave Applications", manual: 1.8, automated: 0.2, saved: 1.6 },
  { label: "Parent Notifications", manual: 3.0, automated: 0.1, saved: 2.9 },
  { label: "Security Incidents", manual: 1.5, automated: 0.3, saved: 1.2 },
];

export default function ImpactPage() {
  const totalSaved = timeBreakdown.reduce((sum, r) => sum + r.saved, 0);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-heading text-2xl font-bold text-[var(--color-ink)]">Impact Analytics</h1>
        <p className="mt-1 text-sm text-[var(--color-ink-muted)]">Measured efficiency gains — not claims</p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Total Time Saved" value={`${totalSaved.toFixed(1)}h`} delta="+4.2h this week" trend="up" icon={Clock} />
        <StatCard label="Workflows Completed" value="28" delta="+8 this week" trend="up" icon={Zap} />
        <StatCard label="Manual Hours Replaced" value="13.0h" delta="vs 2.0h agent time" trend="up" icon={TrendingUp} />
        <StatCard label="Staff Hours Freed" value="11.0h" delta="≈ 1.4 FTE days" trend="up" icon={Users} />
      </div>

      {/* Time Saved Breakdown */}
      <div
        className="rounded-[var(--radius-lg)] border bg-[var(--color-surface)] p-6"
        style={{ borderColor: "var(--color-border-subtle)" }}
      >
        <div className="flex items-center gap-2 mb-5">
          <BarChart3 size={18} className="text-[var(--color-primary)]" />
          <h2 className="font-heading text-base font-semibold text-[var(--color-ink)]">
            Manual vs Automated Time
          </h2>
        </div>

        <div className="space-y-5">
          {timeBreakdown.map((row) => (
            <div key={row.label}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-[var(--color-ink)]">{row.label}</span>
                <span className="font-mono text-xs text-[var(--color-status-done)]">
                  {row.saved.toFixed(1)}h saved
                </span>
              </div>
              <div className="flex gap-2">
                <div className="flex-1">
                  <div className="mb-1 text-[11px] text-[var(--color-ink-faint)]">Manual: {row.manual}h</div>
                  <div className="h-2.5 rounded-full bg-[var(--color-surface-sunken)] overflow-hidden">
                    <div
                      className="h-full rounded-full bg-[var(--color-ink-disabled)] transition-all duration-500"
                      style={{ width: `${(row.manual / 5) * 100}%` }}
                    />
                  </div>
                </div>
                <div className="flex-1">
                  <div className="mb-1 text-[11px] text-[var(--color-ink-faint)]">Automated: {row.automated}h</div>
                  <div className="h-2.5 rounded-full bg-[var(--color-surface-sunken)] overflow-hidden">
                    <div
                      className="h-full rounded-full bg-[var(--color-primary)] transition-all duration-500"
                      style={{ width: `${(row.automated / 5) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
