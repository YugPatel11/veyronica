"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Activity,
  CheckSquare,
  Clock,
  Coins,
  GitBranch,
  Plug,
  Zap,
  AlertTriangle,
  ArrowRight,
  RefreshCw,
  Play,
  CircleDot,
} from "lucide-react";
import { StatCard } from "@/components/ui/stat-card";
import { StatusBadge, type Status } from "@/components/ui/status-badge";
import { ProgressBar } from "@/components/ui/progress-bar";
import { Timeline, type TimelineEntry } from "@/components/ui/timeline";

/**
 * Mission Control — EPIC-13-T01
 *
 * Overview page: 4 StatCards, recent workflow runs table,
 * connector health grid, and live event feed.
 */

// ── Mock Data (replaced by API calls when backend is connected) ─────────────

const STATS = {
  activeRuns: { value: 3, delta: "+2 today", trend: "up" as const },
  pendingApprovals: { value: 7, delta: "3 urgent", trend: "up" as const },
  timeSaved: { value: "12.4h", delta: "+1.8h this week", trend: "up" as const },
  costToday: { value: "$4.28", delta: "-18% vs avg", trend: "down" as const },
};

interface WorkflowRun {
  id: string;
  name: string;
  status: Status;
  autonomy: string;
  steps: string;
  started: string;
  duration: string;
  cost: string;
}

const RECENT_RUNS: WorkflowRun[] = [
  {
    id: "run_001",
    name: "Exam Marks Processing",
    status: "running",
    autonomy: "Supervised",
    steps: "3/6",
    started: "2 min ago",
    duration: "2m 14s",
    cost: "$0.42",
  },
  {
    id: "run_002",
    name: "Assignment Cycle — CS201",
    status: "waiting",
    autonomy: "Supervised",
    steps: "4/5",
    started: "18 min ago",
    duration: "17m 48s",
    cost: "$1.12",
  },
  {
    id: "run_003",
    name: "Leave Application — Arjun K.",
    status: "done",
    autonomy: "Autonomous",
    steps: "5/5",
    started: "1h ago",
    duration: "4m 32s",
    cost: "$0.18",
  },
  {
    id: "run_004",
    name: "Exam Marks Processing — PHY101",
    status: "done",
    autonomy: "Supervised",
    steps: "6/6",
    started: "3h ago",
    duration: "12m 05s",
    cost: "$2.56",
  },
  {
    id: "run_005",
    name: "Security Incident — Brute Force",
    status: "failed",
    autonomy: "Supervised",
    steps: "2/4",
    started: "5h ago",
    duration: "1m 22s",
    cost: "$0.08",
  },
];

interface ConnectorHealth {
  id: string;
  name: string;
  status: "healthy" | "degraded" | "down";
  latency: string;
  circuit: "closed" | "open" | "half_open";
}

const CONNECTORS: ConnectorHealth[] = [
  { id: "erp", name: "Campus ERP", status: "healthy", latency: "42ms", circuit: "closed" },
  { id: "lms", name: "LMS", status: "healthy", latency: "38ms", circuit: "closed" },
  { id: "crm", name: "Student CRM", status: "degraded", latency: "210ms", circuit: "half_open" },
  { id: "email", name: "Email (SMTP)", status: "healthy", latency: "120ms", circuit: "closed" },
  { id: "storage", name: "Object Storage", status: "healthy", latency: "18ms", circuit: "closed" },
  { id: "telegram", name: "Telegram", status: "down", latency: "—", circuit: "open" },
];

const LIVE_EVENTS: TimelineEntry[] = [
  {
    id: "evt_1",
    title: "Evaluation Agent completed marking",
    description: "CS301 — 47 answer sheets processed, avg confidence 0.87",
    timestamp: "Just now",
    status: "completed",
  },
  {
    id: "evt_2",
    title: "Approval required: Publish Marks",
    description: "PHY101 — waiting for Dr. Riya Patel",
    timestamp: "2m ago",
    status: "running",
  },
  {
    id: "evt_3",
    title: "Leave Application auto-approved",
    description: "Arjun K. — low risk, autonomous mode",
    timestamp: "8m ago",
    status: "completed",
  },
  {
    id: "evt_4",
    title: "CRM connector degraded",
    description: "Circuit breaker → half_open, latency spike to 210ms",
    timestamp: "12m ago",
    status: "failed",
  },
  {
    id: "evt_5",
    title: "Exam Marks workflow started",
    description: "CS301 Mid-term — initiated by Dr. Ananya Krishnan",
    timestamp: "14m ago",
    status: "completed",
  },
];

// ── Connector health colour helpers ─────────────────────────────────────────

const connectorStatusStyle = {
  healthy: {
    dot: "bg-[var(--color-status-done)]",
    bg: "bg-[var(--color-status-done-bg)]",
    text: "text-[var(--color-status-done)]",
    label: "Healthy",
  },
  degraded: {
    dot: "bg-[var(--color-status-waiting)]",
    bg: "bg-[var(--color-status-waiting-bg)]",
    text: "text-[var(--color-saffron-dark)]",
    label: "Degraded",
  },
  down: {
    dot: "bg-[var(--color-status-failed)]",
    bg: "bg-[var(--color-status-failed-bg)]",
    text: "text-[var(--color-status-failed)]",
    label: "Down",
  },
};

const circuitLabel: Record<string, string> = {
  closed: "Closed",
  open: "Open",
  half_open: "Half-Open",
};

// ── Page Component ──────────────────────────────────────────────────────────

export default function OverviewPage() {
  const [refreshing, setRefreshing] = useState(false);

  function handleRefresh() {
    setRefreshing(true);
    setTimeout(() => setRefreshing(false), 1200);
  }

  return (
    <div className="space-y-8">
      {/* ── Header ──────────────────────────────────────────────────────── */}
      <div className="flex items-end justify-between">
        <div>
          <h1 className="font-heading text-2xl font-bold text-[var(--color-ink)]">
            Mission Control
          </h1>
          <p className="mt-1 text-sm text-[var(--color-ink-muted)]">
            Real-time overview of agents, workflows, and connected systems
          </p>
        </div>
        <button
          onClick={handleRefresh}
          className="flex items-center gap-2 rounded-[var(--radius-md)] border px-3 py-1.5 text-sm font-medium text-[var(--color-ink-muted)] transition-all hover:border-[var(--color-border-strong)] hover:text-[var(--color-ink)]"
          style={{ borderColor: "var(--color-border)" }}
        >
          <RefreshCw
            size={14}
            className={refreshing ? "animate-spin" : ""}
          />
          Refresh
        </button>
      </div>

      {/* ── Stat Cards Row ──────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Active Runs"
          value={STATS.activeRuns.value}
          delta={STATS.activeRuns.delta}
          trend={STATS.activeRuns.trend}
          icon={Activity}
        />
        <StatCard
          label="Pending Approvals"
          value={STATS.pendingApprovals.value}
          delta={STATS.pendingApprovals.delta}
          trend={STATS.pendingApprovals.trend}
          icon={CheckSquare}
        />
        <StatCard
          label="Time Saved"
          value={STATS.timeSaved.value}
          delta={STATS.timeSaved.delta}
          trend={STATS.timeSaved.trend}
          icon={Clock}
        />
        <StatCard
          label="Cost Today"
          value={STATS.costToday.value}
          delta={STATS.costToday.delta}
          trend={STATS.costToday.trend}
          icon={Coins}
        />
      </div>

      {/* ── Main Grid: Runs Table + Connector Health ────────────────────── */}
      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        {/* Workflow Runs Table — spans 2 cols */}
        <div
          className="col-span-1 rounded-[var(--radius-lg)] border bg-[var(--color-surface)] xl:col-span-2"
          style={{ borderColor: "var(--color-border-subtle)" }}
        >
          <div className="flex items-center justify-between border-b px-5 py-4" style={{ borderColor: "var(--color-border-subtle)" }}>
            <div className="flex items-center gap-2">
              <GitBranch size={18} strokeWidth={1.75} className="text-[var(--color-primary)]" />
              <h2 className="font-heading text-base font-semibold text-[var(--color-ink)]">
                Recent Workflow Runs
              </h2>
            </div>
            <Link
              href="/workflows"
              className="flex items-center gap-1 text-xs font-medium transition-colors"
              style={{ color: "var(--color-primary)" }}
            >
              View all <ArrowRight size={12} />
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-xs font-medium uppercase tracking-wider text-[var(--color-ink-faint)]" style={{ borderColor: "var(--color-border-subtle)" }}>
                  <th className="px-5 py-3">Workflow</th>
                  <th className="px-3 py-3">Status</th>
                  <th className="hidden px-3 py-3 md:table-cell">Autonomy</th>
                  <th className="px-3 py-3">Progress</th>
                  <th className="hidden px-3 py-3 lg:table-cell">Started</th>
                  <th className="px-3 py-3 text-right">Cost</th>
                </tr>
              </thead>
              <tbody>
                {RECENT_RUNS.map((run) => {
                  const [doneStr, totalStr] = run.steps.split("/");
                  const done = Number(doneStr ?? 0);
                  const total = Number(totalStr ?? 1);
                  return (
                    <tr
                      key={run.id}
                      className="border-b last:border-b-0 transition-colors hover:bg-[var(--color-surface-sunken)]"
                      style={{ borderColor: "var(--color-border-subtle)" }}
                    >
                      <td className="px-5 py-3">
                        <div>
                          <p className="font-medium text-[var(--color-ink)]">{run.name}</p>
                          <p className="mt-0.5 font-mono text-[11px] text-[var(--color-ink-faint)]">{run.id}</p>
                        </div>
                      </td>
                      <td className="px-3 py-3">
                        <StatusBadge status={run.status} />
                      </td>
                      <td className="hidden px-3 py-3 md:table-cell">
                        <span className="text-xs text-[var(--color-ink-muted)]">{run.autonomy}</span>
                      </td>
                      <td className="px-3 py-3">
                        <div className="flex items-center gap-2">
                          <ProgressBar value={done} max={total} size="sm" className="w-16" />
                          <span className="font-mono text-xs text-[var(--color-ink-muted)]">{run.steps}</span>
                        </div>
                      </td>
                      <td className="hidden px-3 py-3 lg:table-cell">
                        <span className="text-xs text-[var(--color-ink-muted)]">{run.started}</span>
                      </td>
                      <td className="px-3 py-3 text-right">
                        <span className="font-mono text-xs text-[var(--color-ink-muted)]">{run.cost}</span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Connector Health Grid */}
        <div
          className="rounded-[var(--radius-lg)] border bg-[var(--color-surface)]"
          style={{ borderColor: "var(--color-border-subtle)" }}
        >
          <div className="flex items-center justify-between border-b px-5 py-4" style={{ borderColor: "var(--color-border-subtle)" }}>
            <div className="flex items-center gap-2">
              <Plug size={18} strokeWidth={1.75} className="text-[var(--color-primary)]" />
              <h2 className="font-heading text-base font-semibold text-[var(--color-ink)]">
                Connected Systems
              </h2>
            </div>
            <Link
              href="/systems"
              className="flex items-center gap-1 text-xs font-medium transition-colors"
              style={{ color: "var(--color-primary)" }}
            >
              Details <ArrowRight size={12} />
            </Link>
          </div>

          <div className="space-y-1 p-3">
            {CONNECTORS.map((c) => {
              const s = connectorStatusStyle[c.status];
              return (
                <div
                  key={c.id}
                  className="flex items-center justify-between rounded-[var(--radius-md)] px-3 py-2.5 transition-colors hover:bg-[var(--color-surface-sunken)]"
                >
                  <div className="flex items-center gap-3">
                    <div className={`h-2 w-2 rounded-full ${s.dot}`} />
                    <div>
                      <p className="text-sm font-medium text-[var(--color-ink)]">{c.name}</p>
                      <p className="text-[11px] text-[var(--color-ink-faint)]">
                        {c.latency} · Circuit: {circuitLabel[c.circuit]}
                      </p>
                    </div>
                  </div>
                  <span
                    className={`rounded-full px-2 py-0.5 text-[11px] font-medium ${s.bg} ${s.text}`}
                  >
                    {s.label}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* ── Bottom Grid: Live Feed + Quick Actions ──────────────────────── */}
      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        {/* Live Event Feed */}
        <div
          className="col-span-1 rounded-[var(--radius-lg)] border bg-[var(--color-surface)] xl:col-span-2"
          style={{ borderColor: "var(--color-border-subtle)" }}
        >
          <div className="flex items-center justify-between border-b px-5 py-4" style={{ borderColor: "var(--color-border-subtle)" }}>
            <div className="flex items-center gap-2">
              <Zap size={18} strokeWidth={1.75} className="text-[var(--color-ai-accent)]" />
              <h2 className="font-heading text-base font-semibold text-[var(--color-ink)]">
                Live Event Feed
              </h2>
            </div>
            <div className="flex items-center gap-1.5">
              <CircleDot size={8} className="animate-pulse text-[var(--color-status-done)]" />
              <span className="text-[11px] font-medium text-[var(--color-status-done)]">Live</span>
            </div>
          </div>
          <div className="p-5">
            <Timeline entries={LIVE_EVENTS} />
          </div>
        </div>

        {/* Quick Actions Panel */}
        <div
          className="rounded-[var(--radius-lg)] border bg-[var(--color-surface)]"
          style={{ borderColor: "var(--color-border-subtle)" }}
        >
          <div className="border-b px-5 py-4" style={{ borderColor: "var(--color-border-subtle)" }}>
            <h2 className="font-heading text-base font-semibold text-[var(--color-ink)]">
              Quick Actions
            </h2>
          </div>
          <div className="space-y-2 p-4">
            {[
              { label: "Start Exam Workflow", icon: Play, href: "/workflows" },
              { label: "Review Approvals", icon: CheckSquare, href: "/approvals" },
              { label: "Open Copilot", icon: Zap, href: "/copilot" },
              { label: "View Audit Trail", icon: GitBranch, href: "/audit" },
            ].map((action) => (
              <Link
                key={action.label}
                href={action.href}
                className="flex items-center gap-3 rounded-[var(--radius-md)] border px-4 py-3 text-sm font-medium text-[var(--color-ink)] transition-all hover:border-[var(--color-primary-tint)] hover:bg-[var(--color-primary-subtle)] hover:text-[var(--color-primary)]"
                style={{ borderColor: "var(--color-border-subtle)" }}
              >
                <action.icon size={18} strokeWidth={1.75} />
                {action.label}
                <ArrowRight size={14} className="ml-auto opacity-0 transition-opacity group-hover:opacity-100" />
              </Link>
            ))}

            {/* Budget usage mini-widget */}
            <div className="mt-4 rounded-[var(--radius-md)] bg-[var(--color-surface-sunken)] p-4">
              <p className="text-xs font-medium uppercase tracking-wider text-[var(--color-ink-faint)]">
                Daily Token Budget
              </p>
              <ProgressBar
                value={34}
                max={100}
                showValue
                size="sm"
                color="primary"
                className="mt-3"
              />
              <p className="mt-2 font-mono text-xs text-[var(--color-ink-muted)]">
                170K / 500K tokens used
              </p>
            </div>

            {/* Alerts mini */}
            <div className="mt-2 flex items-center gap-2 rounded-[var(--radius-md)] bg-[var(--color-status-waiting-bg)] px-3 py-2.5">
              <AlertTriangle size={14} className="text-[var(--color-saffron-dark)]" />
              <span className="text-xs font-medium text-[var(--color-saffron-dark)]">
                CRM connector degraded — latency spike
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
