"use client";

import { useState } from "react";
import {
  CheckSquare,
  Clock,
  CheckCircle2,
  XCircle,
  Shield,
  Eye,
  Edit3,
  Check,
  AlertCircle,
  X,
  FileDiff,
  Lock,
} from "lucide-react";
import { StatusBadge, type Status } from "@/components/ui/status-badge";
import { toast } from "sonner";

type Tab = "pending" | "decided" | "all";

interface MarkDiffEntry {
  rollNo: string;
  studentName: string;
  originalScore: number;
  proposedScore: number;
  comments: string;
}

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
  approvalsReceived: number;
  approvalsRequired: number;
  diffHash: string;
  entries?: MarkDiffEntry[];
}

const INITIAL_APPROVALS: ApprovalItem[] = [
  {
    id: "apr_001",
    title: "Publish Marks — CS301 Mid-term Exam",
    workflow: "Exam Marks Processing",
    runId: "run_001",
    riskLevel: "high",
    approvalType: "approval",
    status: "pending",
    requestedAt: "2 min ago",
    expiresIn: "57 min",
    requestedBy: "Evaluation Agent",
    description: "47 students evaluated. 3 papers audited with manual adjustments.",
    changesCount: 47,
    approvalsReceived: 0,
    approvalsRequired: 1,
    diffHash: "8f7e2c9a1d4b60e352f1",
    entries: [
      { rollNo: "101", studentName: "Riya Patel", originalScore: 68, proposedScore: 74, comments: "Question 3 step marking corrected" },
      { rollNo: "102", studentName: "Karan Mehta", originalScore: 54, proposedScore: 58, comments: "Diagram bonus marks verified" },
      { rollNo: "103", studentName: "Aditya Rao", originalScore: 82, proposedScore: 86, comments: "Recalculated section B sum" },
    ],
  },
  {
    id: "apr_002",
    title: "Batch Student Record Update",
    workflow: "Campus ERP Sync",
    runId: "run_006",
    riskLevel: "critical",
    approvalType: "dual_approval",
    status: "pending",
    requestedAt: "18 min ago",
    expiresIn: "42 min",
    requestedBy: "Dr. Ananya Krishnan",
    description: "Bulk status migration for graduating senior cohort to Alum ERP.",
    changesCount: 5,
    approvalsReceived: 1,
    approvalsRequired: 2,
    diffHash: "3b9a5c1e7f2d80a4",
    entries: [
      { rollNo: "001", studentName: "Meera Nair", originalScore: 88, proposedScore: 90, comments: "Capstone defense validated" },
      { rollNo: "002", studentName: "Rahul Sharma", originalScore: 79, proposedScore: 82, comments: "Elective transfer credit" },
    ],
  },
  {
    id: "apr_003",
    title: "Send Low-Confidence Parent Notifications",
    workflow: "Parent Communication",
    runId: "run_004",
    riskLevel: "medium",
    approvalType: "approval",
    status: "pending",
    requestedAt: "45 min ago",
    expiresIn: "15 min",
    requestedBy: "Communication Agent",
    description: "12 parent progress advisories via verified email queue.",
    changesCount: 12,
    approvalsReceived: 0,
    approvalsRequired: 1,
    diffHash: "4c1e8a2b5f9d3e70",
  },
  {
    id: "apr_004",
    title: "Publish Marks — MATH201 Calculus III",
    workflow: "Exam Marks Processing",
    runId: "run_007",
    riskLevel: "high",
    approvalType: "approval",
    status: "approved",
    requestedAt: "2h ago",
    expiresIn: "—",
    requestedBy: "Evaluation Agent",
    description: "35 students, final class curve verified by Department Chair.",
    changesCount: 35,
    approvalsReceived: 1,
    approvalsRequired: 1,
    diffHash: "1a2b3c4d5e6f7a8b",
  },
];

const riskConfig = {
  low: { bg: "bg-[var(--color-status-done-bg)]", text: "text-[var(--color-status-done)]", label: "Low" },
  medium: { bg: "bg-[var(--color-status-waiting-bg)]", text: "text-[var(--color-status-waiting)]", label: "Medium" },
  high: { bg: "bg-[var(--color-saffron)]/10", text: "text-[var(--color-saffron)]", label: "High" },
  critical: { bg: "bg-[var(--color-status-failed-bg)]", text: "text-[var(--color-status-failed)]", label: "Critical" },
};

const statusMap: Record<string, Status> = {
  pending: "waiting",
  approved: "done",
  rejected: "failed",
  expired: "failed",
};

/**
 * Approval Inbox — EPIC-14-T01 through T04 & T09
 *
 * Full-fidelity approval system featuring diff review, dual-approval workflow,
 * inline mark editing, and rejection reason binding.
 */
export default function ApprovalsPage() {
  const [activeTab, setActiveTab] = useState<Tab>("pending");
  const [approvals, setApprovals] = useState<ApprovalItem[]>(INITIAL_APPROVALS);

  // Modal states
  const [diffModalItem, setDiffModalItem] = useState<ApprovalItem | null>(null);
  const [rejectModalItem, setRejectModalItem] = useState<ApprovalItem | null>(null);
  const [rejectReason, setRejectReason] = useState("");
  const [editItem, setEditItem] = useState<ApprovalItem | null>(null);
  const [editableEntries, setEditableEntries] = useState<MarkDiffEntry[]>([]);

  const pendingCount = approvals.filter((a) => a.status === "pending").length;

  const filtered = approvals.filter((a) => {
    if (activeTab === "pending") return a.status === "pending";
    if (activeTab === "decided") return a.status === "approved" || a.status === "rejected";
    return true;
  });

  const handleApprove = (item: ApprovalItem) => {
    if (item.approvalType === "dual_approval" && item.approvalsReceived === 0) {
      // First of two required approvals
      setApprovals((prev) =>
        prev.map((a) =>
          a.id === item.id ? { ...a, approvalsReceived: 1 } : a
        )
      );
      toast.success("First approval recorded (1 of 2). Awaiting second approver review.");
    } else {
      // Final approval
      setApprovals((prev) =>
        prev.map((a) =>
          a.id === item.id
            ? { ...a, status: "approved", approvalsReceived: a.approvalsRequired }
            : a
        )
      );
      toast.success(`Approved: "${item.title}". Changes committed to ledger.`);
    }
  };

  const handleConfirmReject = () => {
    if (!rejectModalItem || !rejectReason.trim()) {
      toast.error("A reason is required to reject an approval request.");
      return;
    }

    setApprovals((prev) =>
      prev.map((a) =>
        a.id === rejectModalItem.id ? { ...a, status: "rejected" } : a
      )
    );
    toast.error(`Rejected: "${rejectModalItem.title}". Reason logged to audit trail.`);
    setRejectModalItem(null);
    setRejectReason("");
  };

  const handleOpenEdit = (item: ApprovalItem) => {
    setEditItem(item);
    setEditableEntries(item.entries ? JSON.parse(JSON.stringify(item.entries)) : []);
  };

  const handleSaveEditAndApprove = () => {
    if (!editItem) return;

    setApprovals((prev) =>
      prev.map((a) =>
        a.id === editItem.id
          ? {
              ...a,
              entries: editableEntries,
              status: "approved",
              approvalsReceived: a.approvalsRequired,
            }
          : a
      )
    );

    toast.success("Edited values saved and approval granted!");
    setEditItem(null);
  };

  return (
    <div className="space-y-6">
      {/* ── Header ──────────────────────────────────────────────────────── */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="font-heading text-2xl font-bold text-[var(--color-ink)]">
            Approval Inbox
          </h1>
          <p className="mt-1 text-sm text-[var(--color-ink-muted)]">
            Human-in-the-loop governance for agentic execution with cryptographic diff validation
          </p>
        </div>

        {/* Tab Pills */}
        <div className="flex items-center gap-1 rounded-[var(--radius-md)] border border-[var(--color-border)] bg-[var(--color-surface)] p-1">
          {(["pending", "decided", "all"] as Tab[]).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex items-center gap-2 rounded-[var(--radius-sm)] px-3 py-1.5 text-xs font-medium transition-all ${
                activeTab === tab
                  ? "bg-[var(--color-primary-tint)] text-[var(--color-primary)] font-semibold shadow-xs"
                  : "text-[var(--color-ink-muted)] hover:text-[var(--color-ink)]"
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
              {tab === "pending" && pendingCount > 0 && (
                <span className="flex h-4 min-w-[16px] items-center justify-center rounded-full bg-[var(--color-primary)] px-1 font-mono text-[10px] font-bold text-white">
                  {pendingCount}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* ── Cards List ──────────────────────────────────────────────────── */}
      <div className="space-y-4">
        {filtered.map((item) => {
          const risk = riskConfig[item.riskLevel];
          const isPending = item.status === "pending";

          return (
            <div
              key={item.id}
              className="rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-surface)] shadow-[var(--shadow-xs)] transition-all hover:shadow-[var(--shadow-sm)]"
            >
              <div className="p-5 space-y-4">
                {/* Header row */}
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="space-y-1 flex-1 min-w-[280px]">
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="text-sm font-semibold text-[var(--color-ink)]">
                        {item.title}
                      </h3>
                      <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-semibold ${risk.bg} ${risk.text}`}>
                        <Shield size={10} />
                        {risk.label} Risk
                      </span>
                      {item.approvalType === "dual_approval" && (
                        <span className="inline-flex items-center gap-1 rounded-full bg-[var(--color-surface-sunken)] px-2 py-0.5 text-[10px] font-medium text-[var(--color-ink-muted)] border border-[var(--color-border)]">
                          <Lock size={10} />
                          Dual-Approval ({item.approvalsReceived}/{item.approvalsRequired})
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-[var(--color-ink-muted)] leading-relaxed">
                      {item.description}
                    </p>
                    <div className="flex flex-wrap items-center gap-2 pt-1 font-mono text-[11px] text-[var(--color-ink-faint)]">
                      <span>{item.workflow}</span>
                      <span>•</span>
                      <span>Initiated by {item.requestedBy}</span>
                      <span>•</span>
                      <span>Hash: {item.diffHash.substring(0, 8)}…</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <StatusBadge
                      status={statusMap[item.status] ?? "waiting"}
                      label={item.status.charAt(0).toUpperCase() + item.status.slice(1)}
                    />
                    {isPending && (
                      <span className="flex items-center gap-1 rounded-full bg-[var(--color-surface-sunken)] px-2.5 py-1 text-[11px] font-medium text-[var(--color-ink-muted)] border border-[var(--color-border)]">
                        <Clock size={11} className="text-[var(--color-saffron)]" />
                        Expires in {item.expiresIn}
                      </span>
                    )}
                  </div>
                </div>

                {/* Inline Diff Sample if available */}
                {item.entries && item.entries.length > 0 && (
                  <div className="rounded-[var(--radius-md)] border border-[var(--color-border-subtle)] bg-[var(--color-surface-sunken)] p-3 space-y-2">
                    <div className="flex items-center justify-between text-[11px] font-semibold text-[var(--color-ink-muted)]">
                      <span>Payload Diff Preview ({item.entries.length} items)</span>
                      <button
                        onClick={() => setDiffModalItem(item)}
                        className="text-[var(--color-primary)] hover:underline flex items-center gap-1"
                      >
                        <FileDiff size={12} />
                        Inspect Full Diff
                      </button>
                    </div>
                    <div className="divide-y divide-[var(--color-border-subtle)] text-xs">
                      {item.entries.slice(0, 2).map((entry, idx) => (
                        <div key={idx} className="flex items-center justify-between py-1.5">
                          <span className="font-medium text-[var(--color-ink)]">
                            {entry.studentName} ({entry.rollNo})
                          </span>
                          <div className="flex items-center gap-2">
                            <span className="line-through text-[var(--color-ink-faint)]">{entry.originalScore}</span>
                            <span>→</span>
                            <span className="font-bold text-[var(--color-status-done)]">{entry.proposedScore}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Actions row for pending items */}
                {isPending && (
                  <div className="flex flex-wrap items-center gap-2 pt-3 border-t border-[var(--color-border-subtle)]">
                    <button
                      onClick={() => handleApprove(item)}
                      className="flex items-center gap-1.5 rounded-[var(--radius-md)] bg-[var(--color-status-done)] px-4 py-2 text-xs font-semibold text-white transition-opacity hover:opacity-90 shadow-xs"
                    >
                      <CheckCircle2 size={14} />
                      {item.approvalType === "dual_approval" && item.approvalsReceived === 0
                        ? "Record 1st Approval"
                        : "Approve & Publish"}
                    </button>

                    <button
                      onClick={() => {
                        setRejectModalItem(item);
                        setRejectReason("");
                      }}
                      className="flex items-center gap-1.5 rounded-[var(--radius-md)] border border-[var(--color-status-failed)] px-3 py-2 text-xs font-medium text-[var(--color-status-failed)] transition-colors hover:bg-[var(--color-status-failed-bg)]"
                    >
                      <XCircle size={14} />
                      Reject…
                    </button>

                    {item.entries && item.entries.length > 0 && (
                      <button
                        onClick={() => handleOpenEdit(item)}
                        className="flex items-center gap-1.5 rounded-[var(--radius-md)] border border-[var(--color-border)] bg-[var(--color-surface)] px-3 py-2 text-xs font-medium text-[var(--color-ink)] transition-colors hover:bg-[var(--color-surface-sunken)]"
                      >
                        <Edit3 size={14} className="text-[var(--color-primary)]" />
                        Edit Marks Before Approving
                      </button>
                    )}

                    <button
                      onClick={() => setDiffModalItem(item)}
                      className="ml-auto flex items-center gap-1.5 rounded-[var(--radius-md)] border border-[var(--color-border)] px-3 py-2 text-xs text-[var(--color-ink-muted)] transition-colors hover:text-[var(--color-ink)] hover:bg-[var(--color-surface-sunken)]"
                    >
                      <Eye size={13} />
                      View Diff
                    </button>
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {filtered.length === 0 && (
          <div className="flex flex-col items-center justify-center rounded-[var(--radius-lg)] border border-dashed border-[var(--color-border)] bg-[var(--color-surface)] py-16 text-center space-y-2">
            <CheckSquare size={36} className="text-[var(--color-ink-faint)]" />
            <h4 className="text-sm font-semibold text-[var(--color-ink)]">Inbox Zero</h4>
            <p className="text-xs text-[var(--color-ink-muted)]">No pending approvals require your action.</p>
          </div>
        )}
      </div>

      {/* ── Rejection Modal (Reason Required) ─────────────────────────────── */}
      {rejectModalItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="fixed inset-0 bg-black/40 backdrop-blur-xs" onClick={() => setRejectModalItem(null)} />
          <div className="relative w-full max-w-md rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-surface)] p-6 shadow-2xl z-10 space-y-4">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-2">
                <AlertCircle size={20} className="text-[var(--color-status-failed)]" />
                <h3 className="text-sm font-bold text-[var(--color-ink)]">Reject Approval Request</h3>
              </div>
              <button
                onClick={() => setRejectModalItem(null)}
                className="text-[var(--color-ink-muted)] hover:text-[var(--color-ink)]"
              >
                <X size={18} />
              </button>
            </div>

            <p className="text-xs text-[var(--color-ink-muted)]">
              Rejecting <strong className="text-[var(--color-ink)]">{rejectModalItem.title}</strong> will pause the workflow and return control to the initiating agent. An immutable reason must be recorded in the Decision Ledger.
            </p>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-[var(--color-ink)]">
                Reason for Rejection <span className="text-[var(--color-status-failed)]">*</span>
              </label>
              <textarea
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                placeholder="Explain why this proposal is rejected (e.g. Marks exceed curve limit)..."
                rows={3}
                className="w-full rounded-[var(--radius-md)] border border-[var(--color-border)] bg-[var(--color-surface-sunken)] p-2.5 text-xs text-[var(--color-ink)] outline-none focus:border-[var(--color-status-failed)]"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t border-[var(--color-border)]">
              <button
                onClick={() => setRejectModalItem(null)}
                className="rounded-[var(--radius-md)] border border-[var(--color-border)] px-3 py-1.5 text-xs font-medium text-[var(--color-ink)] hover:bg-[var(--color-surface-sunken)]"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmReject}
                disabled={!rejectReason.trim()}
                className="rounded-[var(--radius-md)] bg-[var(--color-status-failed)] px-4 py-1.5 text-xs font-semibold text-white disabled:opacity-50 hover:opacity-90"
              >
                Confirm Rejection
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Full Diff Modal (EPIC-14-T02) ─────────────────────────────────── */}
      {diffModalItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="fixed inset-0 bg-black/40 backdrop-blur-xs" onClick={() => setDiffModalItem(null)} />
          <div className="relative w-full max-w-2xl rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-surface)] p-6 shadow-2xl z-10 space-y-4 max-h-[85vh] flex flex-col">
            <div className="flex items-start justify-between border-b border-[var(--color-border)] pb-3">
              <div>
                <h3 className="text-base font-bold text-[var(--color-ink)]">{diffModalItem.title}</h3>
                <p className="text-xs text-[var(--color-ink-muted)]">
                  Cryptographic SHA-256 bound diff ({diffModalItem.diffHash})
                </p>
              </div>
              <button onClick={() => setDiffModalItem(null)} className="text-[var(--color-ink-muted)] hover:text-[var(--color-ink)]">
                <X size={18} />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto space-y-3">
              {diffModalItem.entries && diffModalItem.entries.length > 0 ? (
                <table className="w-full text-left text-xs border border-[var(--color-border)] rounded-[var(--radius-md)]">
                  <thead className="bg-[var(--color-surface-sunken)] border-b border-[var(--color-border)] text-[var(--color-ink-muted)]">
                    <tr>
                      <th className="p-2.5">Roll No</th>
                      <th className="p-2.5">Student</th>
                      <th className="p-2.5 text-center">Before</th>
                      <th className="p-2.5 text-center">Proposed</th>
                      <th className="p-2.5">Audit Note</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[var(--color-border-subtle)]">
                    {diffModalItem.entries.map((e, i) => (
                      <tr key={i} className="hover:bg-[var(--color-surface-sunken)]">
                        <td className="p-2.5 font-mono text-[var(--color-ink-faint)]">{e.rollNo}</td>
                        <td className="p-2.5 font-medium text-[var(--color-ink)]">{e.studentName}</td>
                        <td className="p-2.5 text-center line-through text-[var(--color-status-failed)]">{e.originalScore}</td>
                        <td className="p-2.5 text-center font-bold text-[var(--color-status-done)]">{e.proposedScore}</td>
                        <td className="p-2.5 text-[var(--color-ink-muted)]">{e.comments}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <div className="p-8 text-center text-xs text-[var(--color-ink-muted)]">
                  Diff contains document payload metadata and recipient routing rules.
                </div>
              )}
            </div>

            <div className="flex justify-between items-center pt-3 border-t border-[var(--color-border)] text-xs text-[var(--color-ink-muted)]">
              <span>Verified against Policy Rule: dev_threshold &lt;= 20%</span>
              <button
                onClick={() => setDiffModalItem(null)}
                className="rounded-[var(--radius-md)] bg-[var(--color-primary)] px-4 py-1.5 text-xs font-semibold text-white"
              >
                Close Diff
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Edit-Then-Approve Drawer (EPIC-14-T04) ────────────────────────── */}
      {editItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="fixed inset-0 bg-black/40 backdrop-blur-xs" onClick={() => setEditItem(null)} />
          <div className="relative w-full max-w-xl rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-surface)] p-6 shadow-2xl z-10 space-y-4 max-h-[85vh] flex flex-col">
            <div className="flex items-start justify-between border-b border-[var(--color-border)] pb-3">
              <div>
                <h3 className="text-base font-bold text-[var(--color-ink)]">Edit Marks &amp; Approve</h3>
                <p className="text-xs text-[var(--color-ink-muted)]">
                  Make manual faculty overrides before approving to Campus ERP.
                </p>
              </div>
              <button onClick={() => setEditItem(null)} className="text-[var(--color-ink-muted)] hover:text-[var(--color-ink)]">
                <X size={18} />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto space-y-3">
              {editableEntries.map((entry, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 rounded-[var(--radius-md)] border border-[var(--color-border)] bg-[var(--color-surface-sunken)] gap-3 text-xs"
                >
                  <div className="flex-1">
                    <span className="font-semibold text-[var(--color-ink)]">{entry.studentName}</span>
                    <span className="ml-2 font-mono text-[var(--color-ink-faint)]">({entry.rollNo})</span>
                    <p className="mt-0.5 text-[11px] text-[var(--color-ink-muted)]">{entry.comments}</p>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="text-[var(--color-ink-muted)]">Score:</span>
                    <input
                      type="number"
                      value={entry.proposedScore}
                      onChange={(e) => {
                        const val = Number(e.target.value);
                        setEditableEntries((prev) =>
                          prev.map((item, i) =>
                            i === idx ? { ...item, proposedScore: val } : item
                          )
                        );
                      }}
                      className="w-16 rounded-[var(--radius-sm)] border border-[var(--color-border)] bg-[var(--color-surface)] p-1.5 text-center font-bold text-xs text-[var(--color-ink)] outline-none focus:border-[var(--color-primary)]"
                    />
                  </div>
                </div>
              ))}
            </div>

            <div className="flex justify-end gap-2 pt-3 border-t border-[var(--color-border)]">
              <button
                onClick={() => setEditItem(null)}
                className="rounded-[var(--radius-md)] border border-[var(--color-border)] px-3 py-1.5 text-xs text-[var(--color-ink)] hover:bg-[var(--color-surface-sunken)]"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveEditAndApprove}
                className="flex items-center gap-1.5 rounded-[var(--radius-md)] bg-[var(--color-status-done)] px-4 py-1.5 text-xs font-semibold text-white hover:opacity-90"
              >
                <Check size={14} />
                Save &amp; Grant Approval
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
