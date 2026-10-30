"use client";

import { useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  CheckCircle2,
  AlertTriangle,
  Send,
  Edit3,
  BarChart2,
  Search,
  Users,
  Award,
  Sparkles,
} from "lucide-react";
import { ConfidenceIndicator } from "@/components/ui/confidence-indicator";
import { Badge } from "@/components/ui/badge";

/**
 * Exam Results Review — EPIC-15-T12
 *
 * Grade curve visualization, student marks breakdown, confidence audit, and dual-approval trigger.
 */

interface StudentResult {
  roll: string;
  name: string;
  q1: number; // max 10
  q2: number; // max 10
  q3: number; // max 10
  q4: number; // max 10
  q5: number; // max 10
  total: number; // max 50
  confidence: number;
  status: "verified" | "flagged" | "edited";
  note?: string;
}

const INITIAL_RESULTS: StudentResult[] = [
  { roll: "2024-CS-001", name: "Aarav Sharma", q1: 9, q2: 8, q3: 10, q4: 9, q5: 8, total: 44, confidence: 0.96, status: "verified" },
  { roll: "2024-CS-002", name: "Diya Patel", q1: 7, q2: 8, q3: 8, q4: 6, q5: 7, total: 36, confidence: 0.91, status: "verified" },
  { roll: "2024-CS-003", name: "Rohan Verma", q1: 6, q2: 5, q3: 7, q4: 4, q5: 6, total: 28, confidence: 0.78, status: "flagged", note: "Handwriting in Q4 partially smudged" },
  { roll: "2024-CS-004", name: "Ananya Iyer", q1: 10, q2: 10, q3: 9, q4: 10, q5: 10, total: 49, confidence: 0.98, status: "verified" },
  { roll: "2024-CS-005", name: "Vikram Malhotra", q1: 8, q2: 7, q3: 8, q4: 8, q5: 7, total: 38, confidence: 0.89, status: "verified" },
  { roll: "2024-CS-006", name: "Sneha Nair", q1: 5, q2: 6, q3: 6, q4: 5, q5: 6, total: 28, confidence: 0.82, status: "flagged", note: "Low confidence in Q2 OCR extraction" },
  { roll: "2024-CS-007", name: "Kunal Ghosh", q1: 8, q2: 9, q3: 8, q4: 7, q5: 9, total: 41, confidence: 0.94, status: "verified" },
  { roll: "2024-CS-008", name: "Pooja Reddy", q1: 7, q2: 8, q3: 7, q4: 8, q5: 8, total: 38, confidence: 0.92, status: "verified" },
];

export default function ExamReviewPage() {
  const [results, setResults] = useState<StudentResult[]>(INITIAL_RESULTS);
  const [search, setSearch] = useState("");
  const [filterMode, setFilterMode] = useState<"all" | "flagged" | "verified">("all");
  const [editingStudent, setEditingStudent] = useState<StudentResult | null>(null);
  const [editTotal, setEditTotal] = useState<number>(0);
  const [publishSubmitted, setPublishSubmitted] = useState(false);

  const filtered = results.filter((s) => {
    const matchesSearch =
      search === "" ||
      s.name.toLowerCase().includes(search.toLowerCase()) ||
      s.roll.toLowerCase().includes(search.toLowerCase());

    if (!matchesSearch) return false;
    if (filterMode === "flagged") return s.status === "flagged";
    if (filterMode === "verified") return s.status === "verified";
    return true;
  });

  const handleSaveEdit = () => {
    if (!editingStudent) return;
    setResults((prev) =>
      prev.map((item) =>
        item.roll === editingStudent.roll
          ? { ...item, total: editTotal, status: "edited", confidence: 1.0 }
          : item
      )
    );
    setEditingStudent(null);
  };

  const flaggedCount = results.filter((r) => r.status === "flagged").length;
  const avgMarks = (results.reduce((sum, r) => sum + r.total, 0) / results.length).toFixed(1);

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* ── Breadcrumb & Top Bar ───────────────────────────────────────────── */}
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
                CS301: Midterm Marks Review & Grading
              </h1>
              <Badge variant="outline" className="text-xs">
                Batch 2024–2026
              </Badge>
            </div>
            <p className="mt-0.5 text-xs text-[var(--color-ink-muted)]">
              Evaluated against Rubric ID: rubric_cs301_midterm · Total: 47 Scripts Processed
            </p>
          </div>
        </div>

        <button
          onClick={() => setPublishSubmitted(true)}
          className="flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-semibold text-white shadow-sm transition-all hover:opacity-95 active:scale-95 cursor-pointer"
          style={{ backgroundColor: "var(--color-primary)" }}
        >
          <Send size={14} />
          <span>Submit for Dual-Approval</span>
        </button>
      </div>

      {/* ── Approval Submitted Banner ───────────────────────────────────────── */}
      {publishSubmitted && (
        <div
          className="flex items-center justify-between rounded-xl p-4 border transition-all animate-fadeIn"
          style={{
            backgroundColor: "var(--color-status-done-bg)",
            borderColor: "var(--color-status-done-border)",
          }}
        >
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[var(--color-status-done)] text-white">
              <CheckCircle2 size={16} />
            </div>
            <div>
              <p className="text-sm font-medium text-[var(--color-ink)]">
                Marks submitted to Policy Engine! Dual-Approval request #appr_001 created.
              </p>
              <p className="text-xs text-[var(--color-ink-muted)]">
                Awaiting sign-off from Subject Coordinator and Dean before ERP write.
              </p>
            </div>
          </div>
          <Link
            href="/approvals"
            className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold text-white"
            style={{ backgroundColor: "var(--color-status-done)" }}
          >
            <span>View in Approvals</span>
          </Link>
        </div>
      )}

      {/* ── Key Metrics Cards ──────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="rounded-xl border bg-[var(--color-surface)] p-4" style={{ borderColor: "var(--color-border-subtle)" }}>
          <div className="flex items-center gap-2 text-[var(--color-primary)]">
            <Users size={16} />
            <span className="text-xs font-medium uppercase tracking-wider text-[var(--color-ink-faint)]">
              Total Evaluated
            </span>
          </div>
          <p className="mt-2 text-2xl font-bold font-heading text-[var(--color-ink)]">
            {results.length} Students
          </p>
          <p className="mt-1 text-xs text-[var(--color-status-done)]">100% of batch ingested</p>
        </div>

        <div className="rounded-xl border bg-[var(--color-surface)] p-4" style={{ borderColor: "var(--color-border-subtle)" }}>
          <div className="flex items-center gap-2 text-[var(--color-ai-accent)]">
            <Award size={16} />
            <span className="text-xs font-medium uppercase tracking-wider text-[var(--color-ink-faint)]">
              Batch Average
            </span>
          </div>
          <p className="mt-2 text-2xl font-bold font-heading text-[var(--color-ink)]">
            {avgMarks} <span className="text-xs font-normal text-[var(--color-ink-muted)]">/ 50</span>
          </p>
          <p className="mt-1 text-xs text-[var(--color-ink-muted)]">73.6% class performance</p>
        </div>

        <div className="rounded-xl border bg-[var(--color-surface)] p-4" style={{ borderColor: "var(--color-border-subtle)" }}>
          <div className="flex items-center gap-2 text-[var(--color-status-waiting)]">
            <AlertTriangle size={16} />
            <span className="text-xs font-medium uppercase tracking-wider text-[var(--color-ink-faint)]">
              Flagged for Review
            </span>
          </div>
          <p className="mt-2 text-2xl font-bold font-heading text-[var(--color-saffron-dark)]">
            {flaggedCount} Sheets
          </p>
          <p className="mt-1 text-xs text-[var(--color-ink-muted)]">Confidence below 0.85</p>
        </div>

        <div className="rounded-xl border bg-[var(--color-surface)] p-4" style={{ borderColor: "var(--color-border-subtle)" }}>
          <div className="flex items-center gap-2 text-[var(--color-status-done)]">
            <Sparkles size={16} />
            <span className="text-xs font-medium uppercase tracking-wider text-[var(--color-ink-faint)]">
              Verifier Sum Checks
            </span>
          </div>
          <p className="mt-2 text-2xl font-bold font-heading text-[var(--color-status-done)]">
            0 Mismatches
          </p>
          <p className="mt-1 text-xs text-[var(--color-ink-muted)]">All Q1–Q5 sums verified</p>
        </div>
      </div>

      {/* ── Grade Distribution Mini Curve ──────────────────────────────────── */}
      <div
        className="rounded-2xl border bg-[var(--color-surface)] p-6 shadow-sm space-y-3"
        style={{ borderColor: "var(--color-border-subtle)" }}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BarChart2 size={16} className="text-[var(--color-primary)]" />
            <h3 className="font-heading text-sm font-semibold text-[var(--color-ink)]">
              Marks Distribution Curve
            </h3>
          </div>
          <span className="text-xs text-[var(--color-ink-muted)]">Passing threshold: 20 marks (40%)</span>
        </div>

        <div className="grid grid-cols-4 gap-3 pt-2">
          {[
            { range: "< 20 Marks (Fail)", count: 0, pct: "0%" },
            { range: "20 – 30 Marks", count: 2, pct: "25%" },
            { range: "31 – 40 Marks", count: 4, pct: "50%" },
            { range: "41 – 50 Marks (Top)", count: 2, pct: "25%" },
          ].map((bucket) => (
            <div
              key={bucket.range}
              className="rounded-xl p-3 border text-center space-y-1"
              style={{
                backgroundColor: "var(--color-surface-sunken)",
                borderColor: "var(--color-border-subtle)",
              }}
            >
              <p className="text-xs font-medium text-[var(--color-ink-muted)]">{bucket.range}</p>
              <p className="text-lg font-bold text-[var(--color-ink)]">{bucket.count} students</p>
              <div className="h-1.5 w-full rounded-full bg-[var(--color-border)] overflow-hidden">
                <div
                  className="h-full bg-[var(--color-primary)] rounded-full"
                  style={{ width: bucket.pct }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Student Results Table ─────────────────────────────────────────── */}
      <div
        className="rounded-2xl border bg-[var(--color-surface)] shadow-sm overflow-hidden"
        style={{ borderColor: "var(--color-border-subtle)" }}
      >
        <div
          className="flex flex-wrap items-center justify-between gap-4 border-b px-6 py-4"
          style={{ borderColor: "var(--color-border-subtle)" }}
        >
          {/* Search */}
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
              placeholder="Search by student name or roll…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="bg-transparent text-[var(--color-ink)] outline-none placeholder:text-[var(--color-ink-disabled)] w-48 sm:w-64"
            />
          </div>

          {/* Filter Pills */}
          <div className="flex items-center gap-2 text-xs">
            <button
              onClick={() => setFilterMode("all")}
              className={`rounded-lg px-3 py-1.5 font-medium transition-colors cursor-pointer ${
                filterMode === "all"
                  ? "bg-[var(--color-primary)] text-white"
                  : "bg-[var(--color-surface-sunken)] text-[var(--color-ink-muted)] hover:text-[var(--color-ink)]"
              }`}
            >
              All ({results.length})
            </button>
            <button
              onClick={() => setFilterMode("flagged")}
              className={`rounded-lg px-3 py-1.5 font-medium transition-colors cursor-pointer ${
                filterMode === "flagged"
                  ? "bg-[var(--color-saffron)] text-black font-semibold"
                  : "bg-[var(--color-surface-sunken)] text-[var(--color-ink-muted)] hover:text-[var(--color-ink)]"
              }`}
            >
              Flagged ({flaggedCount})
            </button>
            <button
              onClick={() => setFilterMode("verified")}
              className={`rounded-lg px-3 py-1.5 font-medium transition-colors cursor-pointer ${
                filterMode === "verified"
                  ? "bg-[var(--color-status-done)] text-white font-semibold"
                  : "bg-[var(--color-surface-sunken)] text-[var(--color-ink-muted)] hover:text-[var(--color-ink)]"
              }`}
            >
              Verified ({results.length - flaggedCount})
            </button>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr
                className="border-b text-left text-xs font-medium uppercase tracking-wider text-[var(--color-ink-faint)]"
                style={{ borderColor: "var(--color-border-subtle)" }}
              >
                <th className="px-6 py-3.5">Roll No.</th>
                <th className="px-4 py-3.5">Student Name</th>
                <th className="px-3 py-3.5 text-center">Q1</th>
                <th className="px-3 py-3.5 text-center">Q2</th>
                <th className="px-3 py-3.5 text-center">Q3</th>
                <th className="px-3 py-3.5 text-center">Q4</th>
                <th className="px-3 py-3.5 text-center">Q5</th>
                <th className="px-4 py-3.5 text-right">Total Marks</th>
                <th className="px-4 py-3.5">Confidence</th>
                <th className="px-4 py-3.5">Status</th>
                <th className="px-4 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((s) => (
                <tr
                  key={s.roll}
                  className="border-b last:border-b-0 transition-colors hover:bg-[var(--color-surface-sunken)]"
                  style={{ borderColor: "var(--color-border-subtle)" }}
                >
                  <td className="px-6 py-3.5 font-mono text-xs text-[var(--color-ink)]">
                    {s.roll}
                  </td>
                  <td className="px-4 py-3.5 font-medium text-[var(--color-ink)]">
                    <div>
                      {s.name}
                      {s.note && (
                        <p className="text-[11px] text-[var(--color-saffron-dark)] mt-0.5">
                          {s.note}
                        </p>
                      )}
                    </div>
                  </td>
                  <td className="px-3 py-3.5 text-center font-mono text-xs text-[var(--color-ink-muted)]">
                    {s.q1}
                  </td>
                  <td className="px-3 py-3.5 text-center font-mono text-xs text-[var(--color-ink-muted)]">
                    {s.q2}
                  </td>
                  <td className="px-3 py-3.5 text-center font-mono text-xs text-[var(--color-ink-muted)]">
                    {s.q3}
                  </td>
                  <td className="px-3 py-3.5 text-center font-mono text-xs text-[var(--color-ink-muted)]">
                    {s.q4}
                  </td>
                  <td className="px-3 py-3.5 text-center font-mono text-xs text-[var(--color-ink-muted)]">
                    {s.q5}
                  </td>
                  <td className="px-4 py-3.5 text-right font-mono text-xs font-bold text-[var(--color-ink)]">
                    {s.total} / 50
                  </td>
                  <td className="px-4 py-3.5">
                    <ConfidenceIndicator value={s.confidence} size={26} showLabel />
                  </td>
                  <td className="px-4 py-3.5">
                    {s.status === "flagged" ? (
                      <span className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-semibold bg-[var(--color-status-waiting-bg)] text-[var(--color-saffron-dark)]">
                        <AlertTriangle size={10} />
                        Flagged
                      </span>
                    ) : s.status === "edited" ? (
                      <span className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-semibold bg-[var(--color-primary-tint)] text-[var(--color-primary)]">
                        Faculty Edited
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-semibold bg-[var(--color-status-done-bg)] text-[var(--color-status-done)]">
                        <CheckCircle2 size={10} />
                        Verified
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3.5 text-right">
                    <button
                      onClick={() => {
                        setEditingStudent(s);
                        setEditTotal(s.total);
                      }}
                      className="inline-flex items-center gap-1 rounded-lg border px-2.5 py-1 text-xs font-medium text-[var(--color-ink-muted)] hover:text-[var(--color-ink)] hover:bg-[var(--color-surface-sunken)] transition-colors cursor-pointer"
                      style={{ borderColor: "var(--color-border)" }}
                    >
                      <Edit3 size={11} />
                      <span>Edit</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* ── Edit Modal / Drawer ───────────────────────────────────────────── */}
      {editingStudent && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <div
            className="w-full max-w-md rounded-2xl border bg-[var(--color-surface)] p-6 shadow-xl space-y-4"
            style={{ borderColor: "var(--color-border-strong)" }}
          >
            <div className="flex items-center justify-between border-b pb-3" style={{ borderColor: "var(--color-border-subtle)" }}>
              <h3 className="font-heading text-base font-bold text-[var(--color-ink)]">
                Override Student Marks
              </h3>
              <Badge variant="outline" className="font-mono text-xs">
                {editingStudent.roll}
              </Badge>
            </div>

            <div className="space-y-3 text-xs">
              <p className="text-[var(--color-ink-muted)]">
                Modifying evaluated score for{" "}
                <span className="font-semibold text-[var(--color-ink)]">{editingStudent.name}</span>.
                All faculty edits are recorded with cryptographic attribution in the ledger.
              </p>

              <div>
                <label className="block text-xs font-medium text-[var(--color-ink-muted)] mb-1">
                  Total Marks (out of 50)
                </label>
                <input
                  type="number"
                  min={0}
                  max={50}
                  value={editTotal}
                  onChange={(e) => setEditTotal(Number(e.target.value))}
                  className="w-full rounded-lg border px-3 py-2 text-sm bg-[var(--color-surface-sunken)] text-[var(--color-ink)] outline-none font-mono"
                  style={{ borderColor: "var(--color-border)" }}
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-3 border-t" style={{ borderColor: "var(--color-border-subtle)" }}>
              <button
                onClick={() => setEditingStudent(null)}
                className="rounded-lg border px-3.5 py-1.5 text-xs font-medium text-[var(--color-ink-muted)] hover:text-[var(--color-ink)]"
                style={{ borderColor: "var(--color-border)" }}
              >
                Cancel
              </button>
              <button
                onClick={handleSaveEdit}
                className="rounded-lg px-4 py-1.5 text-xs font-semibold text-white shadow-xs"
                style={{ backgroundColor: "var(--color-primary)" }}
              >
                Save & Verify
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
