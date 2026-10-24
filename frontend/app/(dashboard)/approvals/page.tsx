"use client";

import { useState } from "react";
import {
  CheckSquare,
  Clock,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  ArrowRight,
  Shield,
  Eye,
  Filter,
} from "lucide-react";
import { StatusBadge } from "@/components/ui/status-badge";

/**
 * Approval Inbox — EPIC-14-T01
 *
 * Tabs: Pending / Decided / All.
 * Each card shows diff, risk badge, countdown, and actions.
 */

type Tab = "pending" | "decided" | "all";

interface ApprovalItem {
  id: string;
  title: string;
  workflow: string;
  runId: string;
  riskLevel: "low" | "medium" | "high" | "critical";
  approvalType: "approval" | "dual_approval" | "notify";
  status: "pending" | "approved" | "rejected" | "expired";
  requestedAt: string;
  expiresIn: string;
  requestedBy: string;
  description: string;
  changesCount: number;
}

const MOCK_APPROVALS: ApprovalItem[] = [
  {
    id: "apr_001",
    title: "Publish Marks — CS301 Mid-term",
    workflow: "Exam Marks Processing",
    runId: "run_001",
    riskLevel: "high",
    approvalType: "approval",
    status: "pending",
    requestedAt: "2 min ago",
    expiresIn: "57 min",
    requestedBy: "Evaluation Agent",
    description: "47 students, avg marks 62.4/100, 3 flagged for low confidence",
    changesCount: 47,
  },
  {
    id: "apr_002",
    title: "Delete Student Records — Batch",
    workflow: "Admin Operation",
    runId: "run_006",
    riskLevel: "critical",
    approvalType: "dual_approval",
    status: "pending",
    requestedAt: "18 min ago",
    expiresIn: "42 min",
    requestedBy: "Dr. Ananya Krishnan",
    description: "Remove 5 duplicate student records from ERP",
    changesCount: 5,
  },
  {
    id: "apr_003",
    title: "Send Parent Notifications — PHY101",
    workflow: "Exam Marks Processing",
    runId: "run_004",
    riskLevel: "medium",
    approvalType: "approval",
    status: "pending",
    requestedAt: "45 min ago",
    expiresIn: "15 min",
    requestedBy: "Communication Agent",
    description: "12 below-threshold notifications to parents via email",
    changesCount: 12,
  },
  {
    id: "apr_004",
    title: "Publish Marks — MATH201",
    workflow: "Exam Marks Processing",
    runId: "run_007",
    riskLevel: "high",
    approvalType: "approval",
    status: "approved",
    requestedAt: "2h ago",
    expiresIn: "—",
    requestedBy: "Evaluation Agent",
    description: "35 students, avg marks 71.2/100",
    changesCount: 35,
  },
  {
    id: "apr_005",
    title: "Update Student Grade — Arjun K.",
    workflow: "Assignment Cycle",
    runId: "run_008",
    riskLevel: "medium",
    approvalType: "approval",
    status: "rejected",
    requestedAt: "3h ago",
    expiresIn: "—",
    requestedBy: "Assignment Agent",
    description: "Grade change B+ → A- requires faculty confirmation",
    changesCount: 1,
  },
];

const riskConfig = {
  low: { label: "Low", bg: "bg-[var(--color-status-done-bg)]", text: "text-[var(--color-status-done)]" },
  medium: { label: "Medium", bg: "bg-[var(--color-status-waiting-bg)]", text: "text-[var(--color-saffron-dark)]" },
  high: { label: "High", bg: "bg-[var(--color-status-failed-bg)]", text: "text-[var(--color-status-failed)]" },
  critical: { label: "Critical", bg: "bg-[var(--color-status-failed-bg)]", text: "text-[var(--color-status-failed)]" },
};

const statusMap: Record<string, "waiting" | "done" | "failed" | "queued"> = {
  pending: "waiting",
  approved: "done",
  rejected: "failed",
  expired: "queued",
};

export default function ApprovalsPage() {
  const [activeTab, setActiveTab] = useState<Tab>("pending");

  const filtered = MOCK_APPROVALS.filter((a) => {
    if (activeTab === "pending") return a.status === "pending";
    if (activeTab === "decided") return a.status !== "pending";
    return true;
  });

  const pendingCount = MOCK_APPROVALS.filter((a) => a.status === "pending").length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="font-heading text-2xl font-bold text-[var(--color-ink)]">
          Approval Inbox
        </h1>
        <p className="mt-1 text-sm text-[var(--color-ink-muted)]">
          Review and decide on pending agent actions
        </p>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-1 rounded-[var(--radius-md)] bg-[var(--color-surface-sunken)] p-1">
        {(["pending", "decided", "all"] as Tab[]).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`flex items-center gap-2 rounded-[var(--radius-sm)] px-4 py-2 text-sm font-medium transition-all ${
              activeTab === tab
                ? "bg-[var(--color-surface)] text-[var(--color-ink)] shadow-[var(--shadow-xs)]"
                : "text-[var(--color-ink-muted)] hover:text-[var(--color-ink)]"
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
            {tab === "pending" && pendingCount > 0 && (
              <span className="flex h-5 w-5 items-center justify-center rounded-full bg-[var(--color-primary)] text-[11px] font-bold text-white">
                {pendingCount}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Approval Cards */}
      <div className="space-y-3">
        {filtered.map((approval) => {
          const risk = riskConfig[approval.riskLevel];
          return (
            <div
              key={approval.id}
              className="rounded-[var(--radius-lg)] border bg-[var(--color-surface)] transition-shadow hover:shadow-[var(--shadow-sm)]"
              style={{ borderColor: "var(--color-border-subtle)" }}
            >
              <div className="p-5">
                {/* Top row */}
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="text-sm font-semibold text-[var(--color-ink)]">
                        {approval.title}
                      </h3>
                      <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium ${risk.bg} ${risk.text}`}>
                        <Shield size={10} />
                        {risk.label} Risk
                      </span>
                      {approval.approvalType === "dual_approval" && (
                        <span className="rounded-full bg-[var(--color-surface-sunken)] px-2 py-0.5 text-[11px] font-medium text-[var(--color-ink-muted)]">
                          Dual Approval
                        </span>
                      )}
                    </div>
                    <p className="mt-1 text-xs text-[var(--color-ink-muted)]">
                      {approval.description}
                    </p>
                    <div className="mt-2 flex flex-wrap items-center gap-3 text-[11px] text-[var(--color-ink-faint)]">
                      <span>{approval.workflow}</span>
                      <span>·</span>
                      <span>by {approval.requestedBy}</span>
                      <span>·</span>
                      <span>{approval.requestedAt}</span>
                      <span>·</span>
                      <span>{approval.changesCount} changes</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <StatusBadge status={statusMap[approval.status] ?? "waiting"} label={approval.status.charAt(0).toUpperCase() + approval.status.slice(1)} />
                    {approval.status === "pending" && (
                      <span className="flex items-center gap-1 rounded-full bg-[var(--color-surface-sunken)] px-2 py-0.5 text-[11px] font-medium text-[var(--color-ink-muted)]">
                        <Clock size={10} />
                        {approval.expiresIn}
                      </span>
                    )}
                  </div>
                </div>

                {/* Actions for pending */}
                {approval.status === "pending" && (
                  <div className="mt-4 flex items-center gap-2 border-t pt-4" style={{ borderColor: "var(--color-border-subtle)" }}>
                    <button className="flex items-center gap-1.5 rounded-[var(--radius-md)] bg-[var(--color-status-done)] px-4 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90">
                      <CheckCircle2 size={14} />
                      Approve
                    </button>
                    <button className="flex items-center gap-1.5 rounded-[var(--radius-md)] border border-[var(--color-status-failed)] px-4 py-2 text-sm font-medium text-[var(--color-status-failed)] transition-colors hover:bg-[var(--color-status-failed-bg)]">
                      <XCircle size={14} />
                      Reject
                    </button>
                    <button className="ml-auto flex items-center gap-1.5 rounded-[var(--radius-md)] border px-3 py-2 text-sm text-[var(--color-ink-muted)] transition-colors hover:bg-[var(--color-surface-sunken)]" style={{ borderColor: "var(--color-border)" }}>
                      <Eye size={14} />
                      View Diff
                    </button>
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {filtered.length === 0 && (
          <div className="flex flex-col items-center justify-center rounded-[var(--radius-lg)] border border-dashed bg-[var(--color-surface)] py-12" style={{ borderColor: "var(--color-border)" }}>
            <CheckSquare size={40} className="text-[var(--color-ink-disabled)]" />
            <p className="mt-3 text-sm font-medium text-[var(--color-ink-muted)]">No approvals in this tab</p>
          </div>
        )}
      </div>
    </div>
  );
}
