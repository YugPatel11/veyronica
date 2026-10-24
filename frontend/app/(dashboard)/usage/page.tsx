"use client";

import { Coins, TrendingDown, Cpu, BarChart3 } from "lucide-react";
import { StatCard } from "@/components/ui/stat-card";
import { ProgressBar } from "@/components/ui/progress-bar";

/**
 * Token & Cost — EPIC-20-T05/T06
 *
 * Budget bars, usage by tier/agent, and savings view.
 */

const budgets = [
  { scope: "Global Daily", used: 170000, limit: 500000 },
  { scope: "Global Monthly", used: 2400000, limit: 10000000 },
  { scope: "Exam Workflow", used: 85000, limit: 200000 },
  { scope: "Copilot", used: 42000, limit: 100000 },
];

const tierUsage = [
  { tier: "Economy (GPT-4o-mini)", calls: 142, tokens: 98000, cost: 0.82 },
  { tier: "Standard (GPT-4o)", calls: 38, tokens: 56000, cost: 2.14 },
  { tier: "Premium (GPT-4.1)", calls: 8, tokens: 16000, cost: 1.32 },
];

export default function UsagePage() {
  const totalCost = tierUsage.reduce((s, t) => s + t.cost, 0);
  const strongestOnlyCost = totalCost * 2.8;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-heading text-2xl font-bold text-[var(--color-ink)]">Token & Cost</h1>
        <p className="mt-1 text-sm text-[var(--color-ink-muted)]">LLM usage, budgets, and cost optimisation</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Cost Today" value={`$${totalCost.toFixed(2)}`} delta="-18% vs avg" trend="down" icon={Coins} />
        <StatCard label="Total Calls" value={tierUsage.reduce((s, t) => s + t.calls, 0)} delta="188 today" trend="neutral" icon={Cpu} />
        <StatCard label="Tokens Used" value="170K" delta="34% of daily budget" trend="neutral" icon={BarChart3} />
        <StatCard label="Savings vs Premium-Only" value={`$${(strongestOnlyCost - totalCost).toFixed(2)}`} delta="64% saved via tiering" trend="down" icon={TrendingDown} />
      </div>

      {/* Budget Bars */}
      <div className="rounded-[var(--radius-lg)] border bg-[var(--color-surface)] p-6" style={{ borderColor: "var(--color-border-subtle)" }}>
        <h2 className="font-heading text-base font-semibold text-[var(--color-ink)] mb-5">Budget Utilisation</h2>
        <div className="space-y-5">
          {budgets.map((b) => (
            <ProgressBar
              key={b.scope}
              value={b.used}
              max={b.limit}
              label={b.scope}
              showValue
              size="md"
              color={b.used / b.limit > 0.8 ? "danger" : b.used / b.limit > 0.5 ? "warning" : "primary"}
            />
          ))}
        </div>
      </div>

      {/* Tier Breakdown */}
      <div className="rounded-[var(--radius-lg)] border bg-[var(--color-surface)]" style={{ borderColor: "var(--color-border-subtle)" }}>
        <div className="border-b px-6 py-4" style={{ borderColor: "var(--color-border-subtle)" }}>
          <h2 className="font-heading text-base font-semibold text-[var(--color-ink)]">Usage by Model Tier</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left text-xs font-medium uppercase tracking-wider text-[var(--color-ink-faint)]" style={{ borderColor: "var(--color-border-subtle)" }}>
                <th className="px-6 py-3">Tier</th>
                <th className="px-4 py-3">Calls</th>
                <th className="px-4 py-3">Tokens</th>
                <th className="px-4 py-3 text-right">Cost</th>
              </tr>
            </thead>
            <tbody>
              {tierUsage.map((t) => (
                <tr key={t.tier} className="border-b last:border-b-0" style={{ borderColor: "var(--color-border-subtle)" }}>
                  <td className="px-6 py-3 font-medium text-[var(--color-ink)]">{t.tier}</td>
                  <td className="px-4 py-3 font-mono text-[var(--color-ink-muted)]">{t.calls}</td>
                  <td className="px-4 py-3 font-mono text-[var(--color-ink-muted)]">{(t.tokens / 1000).toFixed(0)}K</td>
                  <td className="px-4 py-3 font-mono text-right text-[var(--color-ink-muted)]">${t.cost.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
