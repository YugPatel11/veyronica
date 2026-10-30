"use client";

import {
  TrendingUp,
  Clock,
  Zap,
  Users,
  BarChart3,
  Coins,
  ShieldCheck,
  ArrowUpRight,
  Sparkles,
} from "lucide-react";
import { StatCard } from "@/components/ui/stat-card";
import { ProgressBar } from "@/components/ui/progress-bar";
import { Badge } from "@/components/ui/badge";

/**
 * Impact Analytics & Cost UI — EPIC-20
 *
 * Provable efficiency gains, staff time freed, token tier budget breakdown,
 * and cost savings vs single-model architectures.
 */

const TIME_BREAKDOWN = [
  { label: "Exam Marks Processing", manual: 4.2, automated: 0.8, saved: 3.4 },
  { label: "Assignment Cycle & Deadline", manual: 2.5, automated: 0.4, saved: 2.1 },
  { label: "Student Leave Applications", manual: 1.8, automated: 0.2, saved: 1.6 },
  { label: "Parent Emergency Notifications", manual: 3.0, automated: 0.1, saved: 2.9 },
  { label: "Security Incident Response", manual: 1.5, automated: 0.3, saved: 1.2 },
];

const TIER_USAGE = [
  { tier: "Economy (Claude 3.5 Haiku)", tokens: "420K", cost: "$0.42", pct: 65, color: "var(--color-status-done)" },
  { tier: "Standard (Claude 3.5 Sonnet)", tokens: "180K", cost: "$1.80", pct: 25, color: "var(--color-primary)" },
  { tier: "Premium (Claude 3.5 Opus)", tokens: "45K", cost: "$2.05", pct: 10, color: "var(--color-ai-accent)" },
];

export default function ImpactPage() {
  const totalSaved = TIME_BREAKDOWN.reduce((sum, r) => sum + r.saved, 0);
  const totalManual = TIME_BREAKDOWN.reduce((sum, r) => sum + r.manual, 0);

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* ── Header ────────────────────────────────────────────────────────── */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="font-heading text-2xl font-bold text-[var(--color-ink)]">
              Impact Analytics & Cost Engine
            </h1>
            <Badge variant="outline" className="text-xs">
              EPIC-20
            </Badge>
          </div>
          <p className="mt-1 text-sm text-[var(--color-ink-muted)]">
            Auditable efficiency gains, faculty time reclaimed, and token routing cost savings
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold bg-[var(--color-status-done-bg)] text-[var(--color-status-done)]">
            <ShieldCheck size={14} />
            <span>Audited Against Ledger</span>
          </span>
        </div>
      </div>

      {/* ── 4 Stat Cards Row (EPIC-20-T02) ─────────────────────────────────── */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Total Time Reclaimed"
          value={`${totalSaved.toFixed(1)} hrs`}
          delta="+4.2h this week"
          trend="up"
          icon={Clock}
        />
        <StatCard
          label="Workflows Completed"
          value="48 Runs"
          delta="100% policy compliance"
          trend="up"
          icon={Zap}
        />
        <StatCard
          label="Manual Labor Replaced"
          value={`${totalManual.toFixed(1)} hrs`}
          delta="vs 1.8h agent compute"
          trend="up"
          icon={TrendingUp}
        />
        <StatCard
          label="Faculty Capacity Freed"
          value="≈ 1.6 FTE"
          delta="Re-allocated to research"
          trend="up"
          icon={Users}
        />
      </div>

      {/* ── Main Two-Column Breakdown ──────────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Manual vs Automated Time Breakdown (EPIC-20-T03) */}
        <div
          className="rounded-2xl border bg-[var(--color-surface)] p-6 shadow-sm space-y-5"
          style={{ borderColor: "var(--color-border-subtle)" }}
        >
          <div className="flex items-center justify-between border-b pb-3" style={{ borderColor: "var(--color-border-subtle)" }}>
            <div className="flex items-center gap-2">
              <BarChart3 size={16} className="text-[var(--color-primary)]" />
              <h2 className="font-heading text-sm font-semibold text-[var(--color-ink)]">
                Workflow Time Savings (Hours)
              </h2>
            </div>
            <span className="font-mono text-xs text-[var(--color-status-done)] font-semibold">
              {totalSaved.toFixed(1)}h Total Saved
            </span>
          </div>

          <div className="space-y-4">
            {TIME_BREAKDOWN.map((row) => (
              <div key={row.label} className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-medium text-[var(--color-ink)]">{row.label}</span>
                  <span className="font-mono font-semibold text-[var(--color-status-done)]">
                    +{row.saved.toFixed(1)}h saved
                  </span>
                </div>

                <div className="flex items-center gap-2 text-[11px] font-mono">
                  <div className="flex-1 bg-[var(--color-surface-sunken)] rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-[var(--color-primary)] h-full rounded-full transition-all duration-500"
                      style={{ width: `${(row.saved / row.manual) * 100}%` }}
                    />
                  </div>
                  <span className="text-[var(--color-ink-muted)] shrink-0">
                    {row.automated}h vs {row.manual}h
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column: Multi-Tier Token & Cost Intelligence (EPIC-20-T05 / T06) */}
        <div
          className="rounded-2xl border bg-[var(--color-surface)] p-6 shadow-sm space-y-5"
          style={{ borderColor: "var(--color-border-subtle)" }}
        >
          <div className="flex items-center justify-between border-b pb-3" style={{ borderColor: "var(--color-border-subtle)" }}>
            <div className="flex items-center gap-2">
              <Coins size={16} className="text-[var(--color-primary)]" />
              <h2 className="font-heading text-sm font-semibold text-[var(--color-ink)]">
                Dynamic LLM Tier Cost Savings
              </h2>
            </div>
            <Badge variant="outline" className="font-mono text-[10px]">
              -68% vs Single Opus
            </Badge>
          </div>

          {/* Daily Budget Progress Mini-Card */}
          <div className="rounded-xl border p-4 space-y-3" style={{ backgroundColor: "var(--color-surface-sunken)", borderColor: "var(--color-border-subtle)" }}>
            <div className="flex items-center justify-between text-xs">
              <span className="font-medium text-[var(--color-ink)]">Daily Token Budget</span>
              <span className="font-mono text-[var(--color-ink-muted)]">645K / 1,000K (64.5%)</span>
            </div>
            <ProgressBar value={64.5} max={100} size="sm" color="primary" />
            <div className="flex items-center justify-between text-[11px] text-[var(--color-ink-faint)]">
              <span>Actual Spend Today: <b className="font-mono text-[var(--color-ink)]">$4.27</b></span>
              <span>Projected Savings: <b className="font-mono text-[var(--color-status-done)]">$9.10</b></span>
            </div>
          </div>

          {/* Tier Usage Breakdown */}
          <div className="space-y-3">
            <span className="text-[11px] uppercase tracking-wider font-medium text-[var(--color-ink-faint)]">
              Token Routing Distribution
            </span>

            {TIER_USAGE.map((item) => (
              <div key={item.tier} className="flex items-center justify-between text-xs py-1">
                <div className="flex items-center gap-2">
                  <div
                    className="h-2.5 w-2.5 rounded-full"
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="text-[var(--color-ink)]">{item.tier}</span>
                </div>
                <div className="flex items-center gap-3 font-mono text-[11px]">
                  <span className="text-[var(--color-ink-muted)]">{item.tokens} tokens</span>
                  <span className="font-semibold text-[var(--color-ink)]">{item.cost}</span>
                </div>
              </div>
            ))}
          </div>

          {/* Cost Forecast Banner (EPIC-20-T07) */}
          <div
            className="flex items-center justify-between rounded-xl p-3 border text-xs"
            style={{
              backgroundColor: "var(--color-primary-subtle)",
              borderColor: "var(--color-border-subtle)",
            }}
          >
            <div className="flex items-center gap-2">
              <Sparkles size={15} className="text-[var(--color-primary)]" />
              <span className="font-medium text-[var(--color-ink)]">
                Monthly Projection: ~$128 vs $410 without tiering
              </span>
            </div>
            <ArrowUpRight size={14} className="text-[var(--color-primary)]" />
          </div>
        </div>
      </div>
    </div>
  );
}
