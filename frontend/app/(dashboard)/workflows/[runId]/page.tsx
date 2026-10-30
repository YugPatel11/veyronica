"use client";

import { useState, use } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  Play,
  Pause,
  RotateCcw,
  Clock,
  Shield,
  Layers,
  Key,
  ChevronRight,
  ChevronDown,
} from "lucide-react";
import { StatusBadge, type Status } from "@/components/ui/status-badge";
import { ConfidenceIndicator } from "@/components/ui/confidence-indicator";
import { Badge } from "@/components/ui/badge";

/**
 * Run Detail & Decision Replay — EPIC-14-T07 & EPIC-14-T08
 *
 * Vertical step timeline, state snapshot inspector, and progressive time slider replay.
 */

interface CheckpointState {
  stepIndex: number;
  stepName: string;
  agent: string;
  status: Status;
  timestamp: string;
  confidence: number;
  tokens: number;
  cost: string;
  modelTier: string;
  stateHash: string;
  inputSummary: string;
  outputSummary: string;
  approvalRequired?: boolean;
}

const MOCK_CHECKPOINTS: CheckpointState[] = [
  {
    stepIndex: 0,
    stepName: "Workflow Initialized",
    agent: "Master Dispatcher",
    status: "done",
    timestamp: "10:14:02",
    confidence: 1.0,
    tokens: 0,
    cost: "$0.00",
    modelTier: "system",
    stateHash: "0x8fa12b489c7d1e0f",
    inputSummary: JSON.stringify({ trigger: "manual", initiated_by: "faculty_priya_sharma", course: "CS301", batch_size: 47 }, null, 2),
    outputSummary: JSON.stringify({ run_id: "run_001", status: "running", steps_queued: 6 }, null, 2),
  },
  {
    stepIndex: 1,
    stepName: "Ingest Answer Sheets",
    agent: "Ingestion Agent",
    status: "done",
    timestamp: "10:14:15",
    confidence: 0.94,
    tokens: 4120,
    cost: "$0.06",
    modelTier: "standard",
    stateHash: "0x3e17b89f2a04cd55",
    inputSummary: JSON.stringify({ files_uploaded: 47, format: "pdf/scanned", resolution: "300dpi" }, null, 2),
    outputSummary: JSON.stringify({ extracted_pages: 94, questions_detected: 10, ocr_accuracy: "97.8%" }, null, 2),
  },
  {
    stepIndex: 2,
    stepName: "Evaluate Answers Against Rubric",
    agent: "Evaluation Agent",
    status: "done",
    timestamp: "10:15:28",
    confidence: 0.89,
    tokens: 18450,
    cost: "$0.28",
    modelTier: "premium",
    stateHash: "0x91df44a7201bb8ee",
    inputSummary: JSON.stringify({ rubric_id: "rubric_midterm_cs301", max_marks: 50 }, null, 2),
    outputSummary: JSON.stringify({ sheets_graded: 47, class_average: "36.8/50", low_confidence_count: 2 }, null, 2),
  },
  {
    stepIndex: 3,
    stepName: "Verify Marks Integrity",
    agent: "Verifier Agent",
    status: "done",
    timestamp: "10:15:42",
    confidence: 0.98,
    tokens: 1200,
    cost: "$0.01",
    modelTier: "economy",
    stateHash: "0xaa4201c9fe87134d",
    inputSummary: JSON.stringify({ marks_sum_check: true, range_max: 50, anomaly_scan: true }, null, 2),
    outputSummary: JSON.stringify({ math_discrepancies: 0, out_of_range: 0, flagged_sheets: 0 }, null, 2),
  },
  {
    stepIndex: 4,
    stepName: "Faculty Dual-Approval Gate",
    agent: "Policy Engine",
    status: "waiting",
    timestamp: "10:15:45",
    confidence: 0.92,
    tokens: 0,
    cost: "$0.00",
    modelTier: "governance",
    stateHash: "0x7c99201fa8842eb1",
    inputSummary: JSON.stringify({ policy: "POL-EXAM-001", approvals_required: 2, current_approvals: 1 }, null, 2),
    outputSummary: JSON.stringify({ status: "waiting_approval", approver_1: "Prof. Priya Sharma (Recorded)", approver_2: "Pending" }, null, 2),
    approvalRequired: true,
  },
  {
    stepIndex: 5,
    stepName: "Publish to Campus ERP",
    agent: "ERP Connector",
    status: "waiting",
    timestamp: "Pending",
    confidence: 0.0,
    tokens: 0,
    cost: "$0.00",
    modelTier: "connector",
    stateHash: "Pending",
    inputSummary: JSON.stringify({ target: "Campus ERP", endpoint: "/api/v2/exam/publish" }, null, 2),
    outputSummary: JSON.stringify({ status: "blocked_by_approval" }, null, 2),
  },
];

export default function RunDetailPage({ params }: { params: Promise<{ runId: string }> }) {
  const resolvedParams = use(params);
  const runId = resolvedParams.runId;

  // Decision Replay Scrubber State (EPIC-14-T08)
  const [replayStep, setReplayStep] = useState<number>(4);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [expandedStep, setExpandedStep] = useState<number | null>(4);

  const activeCheckpoint = MOCK_CHECKPOINTS[replayStep] ?? MOCK_CHECKPOINTS[0] ?? {
    stepIndex: 0,
    stepName: "Workflow Initialized",
    agent: "Master Dispatcher",
    status: "done" as Status,
    timestamp: "10:14:02",
    confidence: 1.0,
    tokens: 0,
    cost: "$0.00",
    modelTier: "system",
    stateHash: "0x8fa12b489c7d1e0f",
    inputSummary: "{}",
    outputSummary: "{}",
  };

  const handlePlayToggle = () => {
    if (isPlaying) {
      setIsPlaying(false);
    } else {
      setIsPlaying(true);
      let step = replayStep >= MOCK_CHECKPOINTS.length - 1 ? 0 : replayStep;
      setReplayStep(step);

      const interval = setInterval(() => {
        step++;
        if (step >= MOCK_CHECKPOINTS.length) {
          setIsPlaying(false);
          clearInterval(interval);
        } else {
          setReplayStep(step);
          setExpandedStep(step);
        }
      }, 1400);
    }
  };

  const handleResetReplay = () => {
    setIsPlaying(false);
    setReplayStep(0);
    setExpandedStep(0);
  };

  return (
    <div className="space-y-6">
      {/* ── Breadcrumb & Navigation Header ─────────────────────────────────── */}
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
                Exam Marks Processing
              </h1>
              <StatusBadge status="waiting" label="Awaiting Approval" />
            </div>
            <p className="mt-0.5 font-mono text-xs text-[var(--color-ink-muted)]">
              Run ID: {runId} · Trigger: Manual · Initiated by Dr. Priya Sharma
            </p>
          </div>
        </div>

        {/* Top Metric Strip */}
        <div className="flex items-center gap-4 text-xs">
          <div className="rounded-lg border bg-[var(--color-surface)] px-3 py-1.5" style={{ borderColor: "var(--color-border-subtle)" }}>
            <span className="text-[var(--color-ink-faint)]">Total Tokens: </span>
            <span className="font-mono font-semibold text-[var(--color-ink)]">23,770</span>
          </div>
          <div className="rounded-lg border bg-[var(--color-surface)] px-3 py-1.5" style={{ borderColor: "var(--color-border-subtle)" }}>
            <span className="text-[var(--color-ink-faint)]">Cost: </span>
            <span className="font-mono font-semibold text-[var(--color-status-done)]">$0.35</span>
          </div>
          <div className="rounded-lg border bg-[var(--color-surface)] px-3 py-1.5" style={{ borderColor: "var(--color-border-subtle)" }}>
            <span className="text-[var(--color-ink-faint)]">Autonomy: </span>
            <span className="font-semibold text-[var(--color-primary)]">Supervised</span>
          </div>
        </div>
      </div>

      {/* ── Decision Replay Scrubber Controller (EPIC-14-T08) ─────────────── */}
      <div
        className="rounded-2xl border bg-[var(--color-surface)] p-5 shadow-sm space-y-4"
        style={{ borderColor: "var(--color-border-subtle)" }}
      >
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Clock size={16} className="text-[var(--color-primary)]" />
            <h2 className="font-heading text-sm font-semibold text-[var(--color-ink)]">
              Decision Replay & State Scrubber
            </h2>
            <Badge variant="outline" className="font-mono text-[10px]">
              EPIC-14-T08
            </Badge>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handlePlayToggle}
              className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold text-white shadow-xs transition-opacity hover:opacity-90 cursor-pointer"
              style={{ backgroundColor: "var(--color-primary)" }}
            >
              {isPlaying ? <Pause size={13} /> : <Play size={13} className="fill-current" />}
              <span>{isPlaying ? "Pause Replay" : "Play Replay"}</span>
            </button>

            <button
              onClick={handleResetReplay}
              className="flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium text-[var(--color-ink-muted)] hover:text-[var(--color-ink)] hover:bg-[var(--color-surface-sunken)] transition-colors cursor-pointer"
              style={{ borderColor: "var(--color-border)" }}
            >
              <RotateCcw size={13} />
              <span>Reset</span>
            </button>
          </div>
        </div>

        {/* Time Slider Range Input */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs font-mono text-[var(--color-ink-muted)]">
            <span>Step 1: Init</span>
            <span className="font-semibold text-[var(--color-primary)]">
              Replay Position: Step {replayStep + 1} of {MOCK_CHECKPOINTS.length} (
              {activeCheckpoint.stepName})
            </span>
            <span>Step {MOCK_CHECKPOINTS.length}: Publish</span>
          </div>

          <input
            type="range"
            min={0}
            max={MOCK_CHECKPOINTS.length - 1}
            value={replayStep}
            onChange={(e) => {
              const val = Number(e.target.value);
              setReplayStep(val);
              setExpandedStep(val);
            }}
            className="w-full accent-[var(--color-primary)] cursor-pointer h-2 bg-[var(--color-surface-sunken)] rounded-lg"
          />
        </div>

        {/* Current Replay Checkpoint Snapshot Banner */}
        <div
          className="flex flex-wrap items-center justify-between gap-3 rounded-xl p-3 border text-xs"
          style={{
            backgroundColor: "var(--color-surface-sunken)",
            borderColor: "var(--color-border-subtle)",
          }}
        >
          <div className="flex items-center gap-3">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-[var(--color-primary-tint)] text-[var(--color-primary)] font-bold font-mono">
              {replayStep + 1}
            </div>
            <div>
              <p className="font-semibold text-[var(--color-ink)]">
                {activeCheckpoint.stepName} · {activeCheckpoint.agent}
              </p>
              <p className="font-mono text-[11px] text-[var(--color-ink-faint)]">
                Timestamp: {activeCheckpoint.timestamp} · State Hash: {activeCheckpoint.stateHash}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <ConfidenceIndicator value={activeCheckpoint.confidence} showLabel />
            <span className="font-mono text-[11px] text-[var(--color-ink-muted)]">
              {activeCheckpoint.tokens} tokens ({activeCheckpoint.cost})
            </span>
          </div>
        </div>
      </div>

      {/* ── Main Two-Column Layout: Timeline & Snapshot Inspector ──────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Vertical Timeline (Spans 2 cols) */}
        <div
          className="col-span-1 lg:col-span-2 rounded-2xl border bg-[var(--color-surface)] p-6 shadow-sm space-y-4"
          style={{ borderColor: "var(--color-border-subtle)" }}
        >
          <h3 className="font-heading text-base font-semibold text-[var(--color-ink)]">
            Execution Checkpoint Timeline
          </h3>

          <div className="relative space-y-4">
            {MOCK_CHECKPOINTS.map((cp, idx) => {
              const isPastOrCurrent = idx <= replayStep;
              const isExpanded = expandedStep === idx;

              return (
                <div key={cp.stepName} className="relative pl-8">
                  {/* Vertical connector line */}
                  {idx < MOCK_CHECKPOINTS.length - 1 && (
                    <div
                      className="absolute left-3 top-8 h-full w-0.5 -ml-[1px] transition-colors"
                      style={{
                        backgroundColor: isPastOrCurrent
                          ? "var(--color-primary)"
                          : "var(--color-border-subtle)",
                      }}
                    />
                  )}

                  {/* Dot Icon */}
                  <div
                    onClick={() => {
                      setReplayStep(idx);
                      setExpandedStep(idx);
                    }}
                    className={`absolute left-0 top-1.5 flex h-6 w-6 items-center justify-center rounded-full font-mono text-[10px] font-bold cursor-pointer transition-all ${
                      idx === replayStep
                        ? "bg-[var(--color-primary)] text-white ring-4 ring-[var(--color-primary-tint)] scale-110"
                        : isPastOrCurrent
                        ? "bg-[var(--color-status-done)] text-white"
                        : "bg-[var(--color-surface-sunken)] text-[var(--color-ink-disabled)] border border-[var(--color-border)]"
                    }`}
                  >
                    {idx + 1}
                  </div>

                  {/* Step Box */}
                  <div
                    className={`rounded-xl border p-4 transition-all ${
                      idx === replayStep
                        ? "border-[var(--color-primary)] bg-[var(--color-primary-subtle)] shadow-xs"
                        : "border-[var(--color-border-subtle)] bg-[var(--color-surface)] hover:border-[var(--color-border-strong)]"
                    }`}
                  >
                    <div
                      onClick={() => setExpandedStep(isExpanded ? null : idx)}
                      className="flex items-center justify-between cursor-pointer"
                    >
                      <div className="flex items-center gap-3">
                        <div>
                          <div className="flex items-center gap-2">
                            <h4 className="text-sm font-semibold text-[var(--color-ink)]">
                              {cp.stepName}
                            </h4>
                            <StatusBadge status={cp.status} />
                          </div>
                          <p className="mt-0.5 text-xs text-[var(--color-ink-muted)]">
                            Agent: {cp.agent} · Tier: {cp.modelTier}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-3">
                        <span className="font-mono text-xs text-[var(--color-ink-faint)]">
                          {cp.timestamp}
                        </span>
                        {isExpanded ? (
                          <ChevronDown size={16} className="text-[var(--color-ink-muted)]" />
                        ) : (
                          <ChevronRight size={16} className="text-[var(--color-ink-muted)]" />
                        )}
                      </div>
                    </div>

                    {/* Collapsible Step Detail Drawer */}
                    {isExpanded && (
                      <div
                        className="mt-4 space-y-3 border-t pt-3 animate-fadeIn"
                        style={{ borderColor: "var(--color-border-subtle)" }}
                      >
                        {/* If step requires approval, show human action callout */}
                        {cp.approvalRequired && (
                          <div
                            className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 rounded-xl p-3 border"
                            style={{
                              backgroundColor: "var(--color-status-waiting-bg)",
                              borderColor: "var(--color-status-waiting-border)",
                            }}
                          >
                            <div className="flex items-center gap-2">
                              <Shield size={16} className="text-[var(--color-saffron-dark)]" />
                              <div>
                                <p className="text-xs font-semibold text-[var(--color-ink)]">
                                  Dual-Approval Required (1 of 2 Complete)
                                </p>
                                <p className="text-[11px] text-[var(--color-ink-muted)]">
                                  Final authorization required from Academic Dean or Subject Coordinator.
                                </p>
                              </div>
                            </div>
                            <Link
                              href="/approvals"
                              className="inline-flex items-center justify-center rounded-lg px-3 py-1.5 text-xs font-semibold text-white shadow-xs"
                              style={{ backgroundColor: "var(--color-primary)" }}
                            >
                              Go to Approval Inbox
                            </Link>
                          </div>
                        )}

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                          <div>
                            <span className="font-mono text-[11px] font-semibold text-[var(--color-ink-faint)]">
                              Input Payload
                            </span>
                            <pre
                              className="mt-1 rounded-lg p-2.5 font-mono text-[11px] overflow-x-auto border"
                              style={{
                                backgroundColor: "var(--color-surface-sunken)",
                                borderColor: "var(--color-border-subtle)",
                                color: "var(--color-ink)",
                              }}
                            >
                              {cp.inputSummary}
                            </pre>
                          </div>

                          <div>
                            <span className="font-mono text-[11px] font-semibold text-[var(--color-ink-faint)]">
                              Output State
                            </span>
                            <pre
                              className="mt-1 rounded-lg p-2.5 font-mono text-[11px] overflow-x-auto border"
                              style={{
                                backgroundColor: "var(--color-surface-sunken)",
                                borderColor: "var(--color-border-subtle)",
                                color: "var(--color-ink)",
                              }}
                            >
                              {cp.outputSummary}
                            </pre>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Active Snapshot Inspector (Spans 1 col) */}
        <div
          className="col-span-1 rounded-2xl border bg-[var(--color-surface)] p-6 shadow-sm space-y-5"
          style={{ borderColor: "var(--color-border-subtle)" }}
        >
          <div className="flex items-center justify-between border-b pb-3" style={{ borderColor: "var(--color-border-subtle)" }}>
            <div className="flex items-center gap-2">
              <Layers size={16} className="text-[var(--color-primary)]" />
              <h3 className="font-heading text-sm font-semibold text-[var(--color-ink)]">
                Snapshot State
              </h3>
            </div>
            <span className="font-mono text-xs text-[var(--color-ink-muted)]">
              Index #{activeCheckpoint.stepIndex}
            </span>
          </div>

          <div className="space-y-4 text-xs">
            <div>
              <span className="text-[11px] font-medium uppercase tracking-wider text-[var(--color-ink-faint)]">
                Cryptographic Checkpoint Hash
              </span>
              <div
                className="mt-1 flex items-center gap-2 rounded-lg p-2.5 font-mono text-[11px] border"
                style={{
                  backgroundColor: "var(--color-surface-sunken)",
                  borderColor: "var(--color-border-subtle)",
                  color: "var(--color-ink)",
                }}
              >
                <Key size={13} className="text-[var(--color-primary)] shrink-0" />
                <span className="truncate">{activeCheckpoint.stateHash}</span>
              </div>
            </div>

            <div className="space-y-2 rounded-xl border p-3.5" style={{ borderColor: "var(--color-border-subtle)" }}>
              <div className="flex items-center justify-between">
                <span className="text-[var(--color-ink-muted)]">Active Node:</span>
                <span className="font-semibold text-[var(--color-ink)]">
                  {activeCheckpoint.stepName}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[var(--color-ink-muted)]">Assigned Agent:</span>
                <span className="font-medium text-[var(--color-primary)]">
                  {activeCheckpoint.agent}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[var(--color-ink-muted)]">Model Tier:</span>
                <span className="font-mono font-medium capitalize text-[var(--color-ink)]">
                  {activeCheckpoint.modelTier}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[var(--color-ink-muted)]">Confidence:</span>
                <ConfidenceIndicator value={activeCheckpoint.confidence} showLabel />
              </div>
            </div>

            <div className="rounded-xl border p-3.5 space-y-2" style={{ borderColor: "var(--color-border-subtle)" }}>
              <div className="flex items-center justify-between">
                <span className="text-[var(--color-ink-muted)]">Step Token Usage:</span>
                <span className="font-mono font-semibold text-[var(--color-ink)]">
                  {activeCheckpoint.tokens.toLocaleString()} tokens
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[var(--color-ink-muted)]">Step Estimated Cost:</span>
                <span className="font-mono font-semibold text-[var(--color-status-done)]">
                  {activeCheckpoint.cost}
                </span>
              </div>
            </div>

            <div className="border-t pt-3" style={{ borderColor: "var(--color-border-subtle)" }}>
              <Link
                href="/audit"
                className="flex items-center justify-between text-xs text-[var(--color-primary)] font-medium hover:underline"
              >
                <span>Inspect in Hash-Chained Audit Ledger</span>
                <ArrowLeft size={13} className="rotate-180" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
