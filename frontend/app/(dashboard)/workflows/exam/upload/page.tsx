"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  UploadCloud,
  FileText,
  CheckCircle2,
  BookOpen,
  Layers,
  Trash2,
  ArrowLeft,
  Sparkles,
} from "lucide-react";
import { AutonomyDial } from "@/components/dashboard/autonomy-dial";
import { Badge } from "@/components/ui/badge";

/**
 * Exam Ingestion & Upload Page — EPIC-15-T11
 *
 * Drag-and-drop answer sheet batch upload, rubric attachment, and ingestion dispatch.
 */

interface UploadedItem {
  id: string;
  name: string;
  size: string;
  status: "ready" | "processing" | "uploaded";
  rollRange: string;
  pageCount: number;
}

const SAMPLE_RUBRICS = [
  { id: "rubric_cs301_midterm", name: "CS301: Midterm Exam 2026 (50 Marks)", questions: 5, status: "Verified" },
  { id: "rubric_cs201_dsa", name: "CS201: Data Structures Lab Quiz (25 Marks)", questions: 3, status: "Verified" },
  { id: "rubric_phy101_final", name: "PHY101: Engineering Physics Comprehensive (100 Marks)", questions: 8, status: "Verified" },
];

export default function ExamUploadPage() {
  const router = useRouter();
  const [course, setCourse] = useState("CS301 - Database Engineering");
  const [rubric, setRubric] = useState(SAMPLE_RUBRICS[0]?.id ?? "");
  const [dragOver, setDragOver] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [files, setFiles] = useState<UploadedItem[]>([
    {
      id: "f_01",
      name: "CS301_Midterm_Batch_A_Roll_001_to_025.pdf",
      size: "18.4 MB",
      status: "ready",
      rollRange: "001 – 025",
      pageCount: 50,
    },
    {
      id: "f_02",
      name: "CS301_Midterm_Batch_B_Roll_026_to_050.pdf",
      size: "17.9 MB",
      status: "ready",
      rollRange: "026 – 050",
      pageCount: 50,
    },
  ]);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);

    // Mock file addition
    const newFile: UploadedItem = {
      id: "f_" + Math.random().toString(36).substring(2, 6),
      name: "CS301_Supplementary_Scan_" + (files.length + 1) + ".pdf",
      size: "8.6 MB",
      status: "ready",
      rollRange: "051 – 060",
      pageCount: 20,
    };
    setFiles((prev) => [...prev, newFile]);
  };

  const handleRemoveFile = (id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const handleStartIngestion = () => {
    setIsSubmitting(true);
    setTimeout(() => {
      router.push("/workflows/exam/review");
    }, 1200);
  };

  const totalSheets = files.reduce((acc, f) => acc + f.pageCount / 2, 0);

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* ── Breadcrumb Header ─────────────────────────────────────────────── */}
      <div className="flex items-center justify-between">
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
                Exam Answer Sheet Ingestion
              </h1>
              <Badge variant="outline" className="text-xs">
                WF1 Pipeline
              </Badge>
            </div>
            <p className="mt-0.5 text-xs text-[var(--color-ink-muted)]">
              Upload scanned student scripts for AI evaluation, sum-verification, and faculty approval
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Form & Drag-and-Drop (Spans 2 cols) */}
        <div className="col-span-1 lg:col-span-2 space-y-6">
          {/* Metadata Card */}
          <div
            className="rounded-2xl border bg-[var(--color-surface)] p-6 shadow-sm space-y-4"
            style={{ borderColor: "var(--color-border-subtle)" }}
          >
            <h2 className="font-heading text-sm font-semibold text-[var(--color-ink)] flex items-center gap-2">
              <BookOpen size={16} className="text-[var(--color-primary)]" />
              <span>Exam & Course Parameters</span>
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-[var(--color-ink-muted)] mb-1">
                  Target Course
                </label>
                <select
                  value={course}
                  onChange={(e) => setCourse(e.target.value)}
                  className="w-full rounded-lg border px-3 py-2 text-sm bg-[var(--color-surface)] text-[var(--color-ink)] outline-none"
                  style={{ borderColor: "var(--color-border)" }}
                >
                  <option value="CS301 - Database Engineering">CS301 — Database Engineering</option>
                  <option value="CS201 - Data Structures">CS201 — Data Structures</option>
                  <option value="PHY101 - Engineering Physics">PHY101 — Engineering Physics</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-[var(--color-ink-muted)] mb-1">
                  Evaluation Rubric
                </label>
                <select
                  value={rubric}
                  onChange={(e) => setRubric(e.target.value)}
                  className="w-full rounded-lg border px-3 py-2 text-sm bg-[var(--color-surface)] text-[var(--color-ink)] outline-none"
                  style={{ borderColor: "var(--color-border)" }}
                >
                  {SAMPLE_RUBRICS.map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Drag & Drop Zone */}
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            className={`rounded-2xl border-2 border-dashed p-8 text-center transition-all cursor-pointer ${
              dragOver
                ? "border-[var(--color-primary)] bg-[var(--color-primary-subtle)] scale-[1.01]"
                : "border-[var(--color-border)] bg-[var(--color-surface)] hover:border-[var(--color-border-strong)]"
            }`}
          >
            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-[var(--color-primary-tint)] text-[var(--color-primary)]">
              <UploadCloud size={28} />
            </div>
            <h3 className="mt-4 font-heading text-base font-semibold text-[var(--color-ink)]">
              Drag & Drop Scanned Answer Sheets
            </h3>
            <p className="mt-1 text-xs text-[var(--color-ink-muted)] max-w-sm mx-auto">
              Supports multipage PDF or ZIP bundles. OCR automatically extracts roll numbers, question
              boundaries, and student handwritten answers.
            </p>
            <button
              type="button"
              onClick={() => {
                const dummy: UploadedItem = {
                  id: "f_" + Math.random().toString(36).substring(2, 6),
                  name: `CS301_Midterm_Batch_C_Roll_${files.length * 25 + 1}.pdf`,
                  size: "14.2 MB",
                  status: "ready",
                  rollRange: `${files.length * 25 + 1} – ${(files.length + 1) * 25}`,
                  pageCount: 50,
                };
                setFiles((prev) => [...prev, dummy]);
              }}
              className="mt-4 inline-flex items-center gap-2 rounded-lg border px-3 py-1.5 text-xs font-semibold text-[var(--color-ink)] hover:bg-[var(--color-surface-sunken)] transition-colors"
              style={{ borderColor: "var(--color-border)" }}
            >
              <UploadCloud size={13} />
              <span>Browse Local Files</span>
            </button>
          </div>

          {/* Upload Queue List */}
          <div
            className="rounded-2xl border bg-[var(--color-surface)] p-6 shadow-sm space-y-3"
            style={{ borderColor: "var(--color-border-subtle)" }}
          >
            <div className="flex items-center justify-between border-b pb-3" style={{ borderColor: "var(--color-border-subtle)" }}>
              <div className="flex items-center gap-2">
                <Layers size={16} className="text-[var(--color-primary)]" />
                <h3 className="font-heading text-sm font-semibold text-[var(--color-ink)]">
                  Staged Answer Sheet Batches ({files.length})
                </h3>
              </div>
              <span className="font-mono text-xs text-[var(--color-ink-muted)]">
                ≈ {totalSheets} Answer Scripts
              </span>
            </div>

            <div className="divide-y" style={{ borderColor: "var(--color-border-subtle)" }}>
              {files.map((file) => (
                <div key={file.id} className="flex items-center justify-between py-3">
                  <div className="flex items-center gap-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[var(--color-surface-sunken)] text-[var(--color-primary)]">
                      <FileText size={18} />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-[var(--color-ink)] truncate max-w-sm">
                        {file.name}
                      </p>
                      <p className="text-[11px] text-[var(--color-ink-faint)]">
                        Roll: {file.rollRange} · {file.pageCount} pages · {file.size}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-semibold bg-[var(--color-status-done-bg)] text-[var(--color-status-done)]">
                      <CheckCircle2 size={10} />
                      Ready
                    </span>
                    <button
                      onClick={() => handleRemoveFile(file.id)}
                      className="p-1 text-[var(--color-ink-disabled)] hover:text-[var(--color-status-failed)] transition-colors cursor-pointer"
                    >
                      <Trash2 size={15} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Execution Configuration & Launch (Spans 1 col) */}
        <div className="col-span-1 space-y-6">
          <div
            className="rounded-2xl border bg-[var(--color-surface)] p-6 shadow-sm space-y-5"
            style={{ borderColor: "var(--color-border-subtle)" }}
          >
            <div className="flex items-center justify-between border-b pb-3" style={{ borderColor: "var(--color-border-subtle)" }}>
              <h3 className="font-heading text-sm font-semibold text-[var(--color-ink)]">
                Pipeline Settings
              </h3>
              <Badge variant="outline" className="text-[10px]">
                Policy Guarded
              </Badge>
            </div>

            {/* Autonomy Dial */}
            <div>
              <span className="block text-xs font-medium text-[var(--color-ink-muted)] mb-2">
                Autonomy Level
              </span>
              <AutonomyDial size="sm" value="supervised" />
            </div>

            {/* Ingestion & Eval Rules */}
            <div className="space-y-3 rounded-xl border p-4 text-xs" style={{ borderColor: "var(--color-border-subtle)" }}>
              <div className="flex items-center justify-between">
                <span className="text-[var(--color-ink-muted)]">OCR Vision Model:</span>
                <span className="font-semibold text-[var(--color-ink)]">Claude 3.5 Sonnet</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[var(--color-ink-muted)]">Verifier Sum Check:</span>
                <span className="font-semibold text-[var(--color-status-done)]">Mandatory (100%)</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[var(--color-ink-muted)]">Confidence Threshold:</span>
                <span className="font-mono font-semibold text-[var(--color-primary)]">≥ 0.85</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[var(--color-ink-muted)]">Dual-Approval:</span>
                <span className="font-semibold text-[var(--color-saffron-dark)]">Faculty Required</span>
              </div>
            </div>

            {/* Cost & Latency Estimate */}
            <div
              className="rounded-xl p-4 border text-xs space-y-1.5"
              style={{
                backgroundColor: "var(--color-surface-sunken)",
                borderColor: "var(--color-border-subtle)",
              }}
            >
              <div className="flex items-center justify-between">
                <span className="text-[var(--color-ink-muted)]">Estimated LLM Cost:</span>
                <span className="font-mono font-semibold text-[var(--color-status-done)]">
                  ≈ $0.35 USD
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[var(--color-ink-muted)]">Estimated Processing Time:</span>
                <span className="font-mono font-semibold text-[var(--color-ink)]">~ 2m 15s</span>
              </div>
            </div>

            {/* Submit Action */}
            <button
              onClick={handleStartIngestion}
              disabled={isSubmitting || files.length === 0}
              className="w-full flex items-center justify-center gap-2 rounded-xl py-3 text-sm font-semibold text-white shadow-sm transition-all hover:opacity-95 active:scale-98 disabled:opacity-50 cursor-pointer"
              style={{ backgroundColor: "var(--color-primary)" }}
            >
              <Sparkles size={16} className={isSubmitting ? "animate-spin" : ""} />
              <span>{isSubmitting ? "Dispatching Pipeline…" : "Start Ingestion & Evaluation"}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
