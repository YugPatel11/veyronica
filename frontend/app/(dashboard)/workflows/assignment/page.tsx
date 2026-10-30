"use client";

import { useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  CheckCircle2,
  Clock,
  AlertCircle,
  Send,
  RefreshCw,
  Search,
  ShieldCheck,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";

/**
 * Assignment Dashboard — EPIC-16-T06 (WF2)
 *
 * Submission classification, overdue detection, plagiarism screening, and LMS grade book sync.
 */

interface SubmissionItem {
  id: string;
  studentRoll: string;
  studentName: string;
  assignmentTitle: string;
  course: string;
  submittedAt: string;
  classification: "on_time" | "late" | "overdue";
  marks: string;
  plagiarismScore: number; // percentage
  lmsSyncStatus: "synced" | "pending" | "failed";
}

const INITIAL_SUBMISSIONS: SubmissionItem[] = [
  {
    id: "sub_01",
    studentRoll: "2024-CS-012",
    studentName: "Kabir Mehta",
    assignmentTitle: "B-Tree Indexing Implementation",
    course: "CS301",
    submittedAt: "Oct 29, 23:45",
    classification: "on_time",
    marks: "24/25",
    plagiarismScore: 3.1,
    lmsSyncStatus: "synced",
  },
  {
    id: "sub_02",
    studentRoll: "2024-CS-018",
    studentName: "Meera Sen",
    assignmentTitle: "B-Tree Indexing Implementation",
    course: "CS301",
    submittedAt: "Oct 30, 00:15",
    classification: "late",
    marks: "21/25 (-2 late)",
    plagiarismScore: 5.4,
    lmsSyncStatus: "synced",
  },
  {
    id: "sub_03",
    studentRoll: "2024-CS-022",
    studentName: "Tarun Kapoor",
    assignmentTitle: "B-Tree Indexing Implementation",
    course: "CS301",
    submittedAt: "Unsubmitted",
    classification: "overdue",
    marks: "—",
    plagiarismScore: 0,
    lmsSyncStatus: "pending",
  },
  {
    id: "sub_04",
    studentRoll: "2024-CS-029",
    studentName: "Isha Deshmukh",
    assignmentTitle: "B-Tree Indexing Implementation",
    course: "CS301",
    submittedAt: "Oct 29, 21:10",
    classification: "on_time",
    marks: "25/25",
    plagiarismScore: 1.8,
    lmsSyncStatus: "synced",
  },
  {
    id: "sub_05",
    studentRoll: "2024-CS-035",
    studentName: "Aditya Joshi",
    assignmentTitle: "B-Tree Indexing Implementation",
    course: "CS301",
    submittedAt: "Oct 30, 01:40",
    classification: "late",
    marks: "19/25 (-4 late)",
    plagiarismScore: 8.2,
    lmsSyncStatus: "pending",
  },
];

export default function AssignmentDashboardPage() {
  const [submissions, setSubmissions] = useState<SubmissionItem[]>(INITIAL_SUBMISSIONS);
  const [filter, setFilter] = useState<"all" | "on_time" | "late" | "overdue">("all");
  const [search, setSearch] = useState("");
  const [syncing, setSyncing] = useState(false);
  const [notificationSent, setNotificationSent] = useState(false);

  const filtered = submissions.filter((s) => {
    const matchesSearch =
      search === "" ||
      s.studentName.toLowerCase().includes(search.toLowerCase()) ||
      s.studentRoll.toLowerCase().includes(search.toLowerCase());

    if (!matchesSearch) return false;
    if (filter !== "all") return s.classification === filter;
    return true;
  });

  const handleSyncLMS = () => {
    setSyncing(true);
    setTimeout(() => {
      setSyncing(false);
      setSubmissions((prev) =>
        prev.map((s) => (s.lmsSyncStatus === "pending" ? { ...s, lmsSyncStatus: "synced" } : s))
      );
    }, 1000);
  };

  const handleSendReminders = () => {
    setNotificationSent(true);
    setTimeout(() => setNotificationSent(false), 4000);
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* ── Header ────────────────────────────────────────────────────────── */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <Link
            href="/workflows"
            className="flex h-9 w-9 items-center justify-center rounded-lg border transition-colors hover:bg-[var(--color-surface-sunken)]"
            style={{
              borderColor: "var(--color-border)",
              color: "var(--color-ink)",
            }}
          >
            <ArrowLeft size={16} />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-heading text-xl font-bold text-[var(--color-ink)]">
                Assignment Cycle & Deadline Engine
              </h1>
              <Badge variant="outline" className="text-xs">
                WF2 Active
              </Badge>
            </div>
            <p className="mt-0.5 text-xs text-[var(--color-ink-muted)]">
              Automated submission classification, Celery Beat overdue detection, and LMS grade synchronization
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleSendReminders}
            className="flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-semibold text-[var(--color-ink)] hover:bg-[var(--color-surface-sunken)] transition-colors cursor-pointer"
            style={{ borderColor: "var(--color-border)" }}
          >
            <Send size={13} />
            <span>Notify Overdue</span>
          </button>
          <button
            onClick={handleSyncLMS}
            disabled={syncing}
            className="flex items-center gap-1.5 rounded-lg px-3.5 py-1.5 text-xs font-semibold text-white shadow-xs transition-opacity hover:opacity-90 disabled:opacity-50 cursor-pointer"
            style={{ backgroundColor: "var(--color-primary)" }}
          >
            <RefreshCw size={13} className={syncing ? "animate-spin" : ""} />
            <span>{syncing ? "Syncing LMS…" : "Sync to LMS"}</span>
          </button>
        </div>
      </div>

      {/* ── Notification Banner ────────────────────────────────────────────── */}
      {notificationSent && (
        <div
          className="flex items-center gap-3 rounded-xl p-3.5 border animate-fadeIn"
          style={{
            backgroundColor: "var(--color-status-done-bg)",
            borderColor: "var(--color-status-done-border)",
          }}
        >
          <CheckCircle2 size={16} className="text-[var(--color-status-done)]" />
          <p className="text-xs font-medium text-[var(--color-ink)]">
            Overdue reminder dispatched via Email & Telegram connectors to 1 pending student!
          </p>
        </div>
      )}

      {/* ── Metric Cards ───────────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="rounded-xl border bg-[var(--color-surface)] p-4" style={{ borderColor: "var(--color-border-subtle)" }}>
          <div className="flex items-center gap-2 text-[var(--color-status-done)]">
            <CheckCircle2 size={16} />
            <span className="text-xs font-medium uppercase tracking-wider text-[var(--color-ink-faint)]">
              On-Time Rate
            </span>
          </div>
          <p className="mt-2 text-2xl font-bold font-heading text-[var(--color-ink)]">80%</p>
          <p className="mt-1 text-xs text-[var(--color-status-done)]">4 of 5 submitted on time</p>
        </div>

        <div className="rounded-xl border bg-[var(--color-surface)] p-4" style={{ borderColor: "var(--color-border-subtle)" }}>
          <div className="flex items-center gap-2 text-[var(--color-saffron)]">
            <Clock size={16} />
            <span className="text-xs font-medium uppercase tracking-wider text-[var(--color-ink-faint)]">
              Late Submissions
            </span>
          </div>
          <p className="mt-2 text-2xl font-bold font-heading text-[var(--color-saffron-dark)]">2</p>
          <p className="mt-1 text-xs text-[var(--color-ink-muted)]">Graduated penalty applied</p>
        </div>

        <div className="rounded-xl border bg-[var(--color-surface)] p-4" style={{ borderColor: "var(--color-border-subtle)" }}>
          <div className="flex items-center gap-2 text-[var(--color-status-failed)]">
            <AlertCircle size={16} />
            <span className="text-xs font-medium uppercase tracking-wider text-[var(--color-ink-faint)]">
              Overdue Students
            </span>
          </div>
          <p className="mt-2 text-2xl font-bold font-heading text-[var(--color-status-failed)]">1</p>
          <p className="mt-1 text-xs text-[var(--color-ink-muted)]">Deadline lapsed 8h ago</p>
        </div>

        <div className="rounded-xl border bg-[var(--color-surface)] p-4" style={{ borderColor: "var(--color-border-subtle)" }}>
          <div className="flex items-center gap-2 text-[var(--color-primary)]">
            <ShieldCheck size={16} />
            <span className="text-xs font-medium uppercase tracking-wider text-[var(--color-ink-faint)]">
              Avg Originality
            </span>
          </div>
          <p className="mt-2 text-2xl font-bold font-heading text-[var(--color-status-done)]">96.3%</p>
          <p className="mt-1 text-xs text-[var(--color-ink-muted)]">Plagiarism scan passed</p>
        </div>
      </div>

      {/* ── Submissions Table ──────────────────────────────────────────────── */}
      <div
        className="rounded-2xl border bg-[var(--color-surface)] shadow-sm overflow-hidden"
        style={{ borderColor: "var(--color-border-subtle)" }}
      >
        <div
          className="flex flex-wrap items-center justify-between gap-4 border-b px-6 py-4"
          style={{ borderColor: "var(--color-border-subtle)" }}
        >
          {/* Search Input */}
          <div
            className="flex items-center gap-2 rounded-lg border px-3 py-1.5 text-xs"
            style={{
              borderColor: "var(--color-border)",
              backgroundColor: "var(--color-surface-sunken)",
            }}
          >
            <Search size={14} className="text-[var(--color-ink-muted)]" />
            <input
              type="text"
              placeholder="Search student or roll…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="bg-transparent text-[var(--color-ink)] outline-none placeholder:text-[var(--color-ink-disabled)] w-48 sm:w-64"
            />
          </div>

          {/* Filters */}
          <div className="flex items-center gap-2 text-xs">
            <button
              onClick={() => setFilter("all")}
              className={`rounded-lg px-3 py-1.5 font-medium transition-colors cursor-pointer ${
                filter === "all"
                  ? "bg-[var(--color-primary)] text-white"
                  : "bg-[var(--color-surface-sunken)] text-[var(--color-ink-muted)] hover:text-[var(--color-ink)]"
              }`}
            >
              All Submissions
            </button>
            <button
              onClick={() => setFilter("on_time")}
              className={`rounded-lg px-3 py-1.5 font-medium transition-colors cursor-pointer ${
                filter === "on_time"
                  ? "bg-[var(--color-status-done)] text-white"
                  : "bg-[var(--color-surface-sunken)] text-[var(--color-ink-muted)] hover:text-[var(--color-ink)]"
              }`}
            >
              On-Time
            </button>
            <button
              onClick={() => setFilter("late")}
              className={`rounded-lg px-3 py-1.5 font-medium transition-colors cursor-pointer ${
                filter === "late"
                  ? "bg-[var(--color-saffron)] text-black font-semibold"
                  : "bg-[var(--color-surface-sunken)] text-[var(--color-ink-muted)] hover:text-[var(--color-ink)]"
              }`}
            >
              Late
            </button>
            <button
              onClick={() => setFilter("overdue")}
              className={`rounded-lg px-3 py-1.5 font-medium transition-colors cursor-pointer ${
                filter === "overdue"
                  ? "bg-[var(--color-status-failed)] text-white"
                  : "bg-[var(--color-surface-sunken)] text-[var(--color-ink-muted)] hover:text-[var(--color-ink)]"
              }`}
            >
              Overdue
            </button>
          </div>
        </div>

        {/* Table View */}
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr
                className="border-b text-left text-xs font-medium uppercase tracking-wider text-[var(--color-ink-faint)]"
                style={{ borderColor: "var(--color-border-subtle)" }}
              >
                <th className="px-6 py-3.5">Roll No.</th>
                <th className="px-4 py-3.5">Student Name</th>
                <th className="px-4 py-3.5">Assignment</th>
                <th className="px-4 py-3.5">Submitted At</th>
                <th className="px-4 py-3.5">Status</th>
                <th className="px-4 py-3.5 text-right">Marks</th>
                <th className="px-4 py-3.5">Similarity</th>
                <th className="px-6 py-3.5 text-right">LMS Sync</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((item) => (
                <tr
                  key={item.id}
                  className="border-b last:border-b-0 transition-colors hover:bg-[var(--color-surface-sunken)]"
                  style={{ borderColor: "var(--color-border-subtle)" }}
                >
                  <td className="px-6 py-3.5 font-mono text-xs text-[var(--color-ink)]">
                    {item.studentRoll}
                  </td>
                  <td className="px-4 py-3.5 font-medium text-[var(--color-ink)]">
                    {item.studentName}
                  </td>
                  <td className="px-4 py-3.5 text-xs text-[var(--color-ink-muted)]">
                    {item.assignmentTitle}
                  </td>
                  <td className="px-4 py-3.5 font-mono text-xs text-[var(--color-ink-muted)]">
                    {item.submittedAt}
                  </td>
                  <td className="px-4 py-3.5">
                    {item.classification === "on_time" ? (
                      <span className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-semibold bg-[var(--color-status-done-bg)] text-[var(--color-status-done)]">
                        <CheckCircle2 size={10} />
                        On-Time
                      </span>
                    ) : item.classification === "late" ? (
                      <span className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-semibold bg-[var(--color-status-waiting-bg)] text-[var(--color-saffron-dark)]">
                        <Clock size={10} />
                        Late
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-semibold bg-[var(--color-status-failed-bg)] text-[var(--color-status-failed)]">
                        <AlertCircle size={10} />
                        Overdue
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3.5 text-right font-mono text-xs font-semibold text-[var(--color-ink)]">
                    {item.marks}
                  </td>
                  <td className="px-4 py-3.5">
                    <span className="font-mono text-xs text-[var(--color-ink-muted)]">
                      {item.plagiarismScore > 0 ? `${item.plagiarismScore}%` : "—"}
                    </span>
                  </td>
                  <td className="px-6 py-3.5 text-right">
                    <span
                      className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-medium ${
                        item.lmsSyncStatus === "synced"
                          ? "bg-[var(--color-status-done-bg)] text-[var(--color-status-done)]"
                          : "bg-[var(--color-surface-sunken)] text-[var(--color-ink-muted)]"
                      }`}
                    >
                      {item.lmsSyncStatus === "synced" ? "Synced" : "Pending"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
