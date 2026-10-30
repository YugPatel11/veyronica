"use client";

import { useState } from "react";
import Link from "next/link";
import {
  GitBranch,
  ArrowRight,
  Play,
  Clock,
  Layers,
  Zap,
  CheckCircle2,
  Cpu,
  Shield,
  FileCode,
  Settings2,
  ChevronRight,
  Plus,
  Radio,
  Calendar,
} from "lucide-react";
import { AutonomyDial, type AutonomyLevel } from "@/components/dashboard/autonomy-dial";
import { Badge } from "@/components/ui/badge";
import { StatusBadge } from "@/components/ui/status-badge";

/**
 * Workflow Studio — EPIC-14-T05 & EPIC-14-T06
 *
 * Visual interactive workflow canvas, autonomy dial, step inspector, and YAML viewer.
 */

interface WorkflowStep {
  name: string;
  type: "agent" | "approval" | "connector" | "parallel" | "branch";
  agent?: string;
  connector?: string;
  description: string;
  modelTier?: "economy" | "standard" | "premium";
  riskLevel?: "low" | "medium" | "high";
}

interface WorkflowDef {
  slug: string;
  name: string;
  description: string;
  trigger: "manual" | "webhook" | "scheduled" | "copilot";
  autonomyDefault: AutonomyLevel;
  runsToday: number;
  status: "active" | "draft";
  steps: WorkflowStep[];
  yamlCode: string;
}

const WORKFLOW_DEFS: WorkflowDef[] = [
  {
    slug: "exam-marks-processing",
    name: "Exam Marks Processing",
    description: "End-to-end exam marks ingestion, OCR extraction, rubric evaluation, verifier sum checks, and ERP publication.",
    trigger: "manual",
    autonomyDefault: "supervised",
    runsToday: 4,
    status: "active",
    steps: [
      {
        name: "Ingest Answer Sheets",
        type: "agent",
        agent: "Ingestion Agent",
        description: "Validate PDF/TIFF scans, run OCR extraction, and segment questions",
        modelTier: "standard",
      },
      {
        name: "Evaluate Answers",
        type: "agent",
        agent: "Evaluation Agent",
        description: "Score student answers against rubric criteria with confidence tracking",
        modelTier: "premium",
      },
      {
        name: "Verify Marks",
        type: "agent",
        agent: "Verifier Agent",
        description: "Deterministic math sum audit and grade range sanity checks",
        modelTier: "economy",
      },
      {
        name: "Faculty Dual-Approval",
        type: "approval",
        description: "Dual-key authorization required before grade ledger write",
        riskLevel: "high",
      },
      {
        name: "Publish to Campus ERP",
        type: "connector",
        connector: "Campus ERP",
        description: "Push verified student grade book through secure ERP gateway",
      },
      {
        name: "Notify Stakeholders",
        type: "parallel",
        description: "Send parent notifications via Email/SMS and update Student CRM records",
      },
    ],
    yamlCode: `name: "Exam Marks Processing"
slug: "exam-marks-processing"
version: 1
trigger: manual
autonomy_default: supervised
on_failure: escalate
steps:
  - name: "Ingest Answer Sheets"
    type: agent
    agent: ingestion
    model_tier: standard
    timeout_seconds: 600
  - name: "Evaluate Answers"
    type: agent
    agent: evaluation
    model_tier: premium
    timeout_seconds: 900
  - name: "Verify Marks"
    type: agent
    agent: verifier
    model_tier: economy
    timeout_seconds: 120
  - name: "Faculty Dual-Approval"
    type: approval
    risk_level: high
  - name: "Publish to ERP"
    type: connector
    connector: campus-erp
    operation: publish_marks
  - name: "Notify Stakeholders"
    type: parallel
    steps:
      - name: "Email Parent"
        type: agent
        agent: communication
      - name: "CRM Note"
        type: connector
        connector: student-crm`,
  },
  {
    slug: "assignment-cycle",
    name: "Assignment Cycle & Deadline Engine",
    description: "Webhook-triggered student assignment classification, automated rubric scoring, and overdue notices.",
    trigger: "webhook",
    autonomyDefault: "supervised",
    runsToday: 12,
    status: "active",
    steps: [
      {
        name: "Submission Classification",
        type: "agent",
        agent: "Assignment Agent",
        description: "Timestamp validation, late penalty calculation, plagiarism pre-check",
        modelTier: "economy",
      },
      {
        name: "Automated Evaluation",
        type: "agent",
        agent: "Evaluation Agent",
        description: "Rubric evaluation with inline constructive feedback generation",
        modelTier: "standard",
      },
      {
        name: "Verification Audit",
        type: "agent",
        agent: "Verifier Agent",
        description: "Consistency checks against historical course averages",
        modelTier: "economy",
      },
      {
        name: "Faculty Batch Approval",
        type: "approval",
        description: "Single-tap review of high-confidence scores",
        riskLevel: "medium",
      },
      {
        name: "LMS Marks Sync",
        type: "connector",
        connector: "Moodle/Canvas LMS",
        description: "Sync final grades and comments to LMS grade book",
      },
    ],
    yamlCode: `name: "Assignment Cycle"
slug: "assignment-cycle"
version: 1
trigger: webhook
autonomy_default: supervised
steps:
  - name: "Submission Classification"
    type: agent
    agent: assignment
  - name: "Automated Evaluation"
    type: agent
    agent: evaluation
  - name: "Verification Audit"
    type: agent
    agent: verifier
  - name: "Faculty Batch Approval"
    type: approval
  - name: "LMS Marks Sync"
    type: connector
    connector: lms`,
  },
  {
    slug: "security-incident",
    name: "Security Incident Response (WF4)",
    description: "Detect brute-force or credential stuffing, isolate offending session, apply temporary lock, and notify sysadmin.",
    trigger: "webhook",
    autonomyDefault: "autonomous",
    runsToday: 2,
    status: "active",
    steps: [
      {
        name: "Anomaly Detection",
        type: "agent",
        agent: "Security Agent",
        description: "Correlate failed logins across IP subnet and user accounts",
        modelTier: "economy",
      },
      {
        name: "Policy Evaluation",
        type: "agent",
        agent: "Policy Engine",
        description: "Match against campus security threshold rules",
        modelTier: "economy",
      },
      {
        name: "Automated Containment",
        type: "connector",
        connector: "Identity Provider",
        description: "15-minute temporary IP block & MFA re-challenge trigger",
      },
      {
        name: "Admin Escalation",
        type: "parallel",
        description: "Emergency push notification to SysAdmin Telegram & ledger incident logging",
      },
    ],
    yamlCode: `name: "Security Incident Response"
slug: "security-incident"
version: 1
trigger: webhook
autonomy_default: autonomous
steps:
  - name: "Anomaly Detection"
    type: agent
    agent: security
  - name: "Policy Evaluation"
    type: agent
    agent: policy
  - name: "Automated Containment"
    type: connector
    connector: idp
  - name: "Admin Escalation"
    type: parallel`,
  },
  {
    slug: "leave-application",
    name: "Student Leave Processing (HR/Academic)",
    description: "Review leave documentation, verify attendance thresholds, compute syllabus impact, and record to ERP.",
    trigger: "webhook",
    autonomyDefault: "supervised",
    runsToday: 5,
    status: "active",
    steps: [
      {
        name: "Document Verification",
        type: "agent",
        agent: "Verifier Agent",
        description: "Extract medical certificates, check dates against academic calendar",
        modelTier: "standard",
      },
      {
        name: "Impact Assessment",
        type: "agent",
        agent: "Analysis Agent",
        description: "Check course attendance minimum (75%) and pending mid-terms",
        modelTier: "standard",
      },
      {
        name: "HOD Approval",
        type: "approval",
        description: "Department Head approval if attendance falls below threshold",
        riskLevel: "low",
      },
      {
        name: "ERP Attendance Update",
        type: "connector",
        connector: "Campus ERP",
        description: "Flag approved excused absence in student record",
      },
    ],
    yamlCode: `name: "Leave Application Processing"
slug: "leave-application"
version: 1
trigger: webhook
autonomy_default: supervised
steps:
  - name: "Document Verification"
    type: agent
    agent: verifier
  - name: "Impact Assessment"
    type: agent
    agent: analysis
  - name: "HOD Approval"
    type: approval
  - name: "ERP Attendance Update"
    type: connector
    connector: campus-erp`,
  },
];

const triggerConfig = {
  manual: { icon: Play, label: "Manual Trigger", color: "var(--color-primary)" },
  webhook: { icon: Zap, label: "Webhook Trigger", color: "var(--color-ai-accent)" },
  scheduled: { icon: Clock, label: "Scheduled Cron", color: "var(--color-saffron)" },
  copilot: { icon: Layers, label: "Copilot Dispatch", color: "var(--color-status-done)" },
};

export default function WorkflowsPage() {
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowDef>(WORKFLOW_DEFS[0] ?? {
    slug: "exam-marks-processing",
    name: "Exam Marks Processing",
    description: "",
    trigger: "manual",
    autonomyDefault: "supervised",
    runsToday: 0,
    status: "active",
    steps: [],
    yamlCode: "",
  });

  const [activeTab, setActiveTab] = useState<"visual" | "yaml" | "runs">("visual");
  const [autonomy, setAutonomy] = useState<AutonomyLevel>(selectedWorkflow.autonomyDefault);
  const [selectedStepIndex, setSelectedStepIndex] = useState<number>(0);
  const [isStartingRun, setIsStartingRun] = useState(false);
  const [runStartedId, setRunStartedId] = useState<string | null>(null);

  const selectedStep = selectedWorkflow.steps[selectedStepIndex];

  const handleStartWorkflow = () => {
    setIsStartingRun(true);
    setTimeout(() => {
      setIsStartingRun(false);
      setRunStartedId("run_live_" + Math.random().toString(36).substring(2, 7));
    }, 900);
  };

  return (
    <div className="space-y-6">
      {/* ── Page Header ──────────────────────────────────────────────────────── */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="font-heading text-2xl font-bold text-[var(--color-ink)]">
              Workflow Studio
            </h1>
            <Badge variant="outline" className="text-xs">
              EPIC-14
            </Badge>
          </div>
          <p className="mt-1 text-sm text-[var(--color-ink-muted)]">
            Design, inspect, and execute policy-governed campus workflows with adaptive autonomy
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <Link
            href="/workflows/timetable"
            className="flex items-center gap-1.5 rounded-lg border px-3 py-2 text-xs font-medium transition-colors hover:bg-[var(--color-surface-sunken)]"
            style={{
              borderColor: "var(--color-border)",
              color: "var(--color-ink)",
            }}
          >
            <Calendar size={14} />
            <span>Timetable (WF5)</span>
          </Link>

          <Link
            href="/workflows/question-paper"
            className="flex items-center gap-1.5 rounded-lg border px-3 py-2 text-xs font-medium transition-colors hover:bg-[var(--color-surface-sunken)]"
            style={{
              borderColor: "var(--color-border)",
              color: "var(--color-ink)",
            }}
          >
            <FileCode size={14} />
            <span>Question Paper (WF6)</span>
          </Link>

          <Link
            href="/workflows/exam/upload"
            className="flex items-center gap-1.5 rounded-lg border px-3 py-2 text-xs font-medium transition-colors hover:bg-[var(--color-surface-sunken)]"
            style={{
              borderColor: "var(--color-border)",
              color: "var(--color-ink)",
            }}
          >
            <Plus size={14} />
            <span>Upload Exam (WF1)</span>
          </Link>

          <button
            onClick={handleStartWorkflow}
            disabled={isStartingRun}
            className="flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold text-white shadow-sm transition-all hover:opacity-95 active:scale-95 disabled:opacity-50 cursor-pointer"
            style={{ backgroundColor: "var(--color-primary)" }}
          >
            <Play size={14} className={isStartingRun ? "animate-spin" : "fill-current"} />
            <span>{isStartingRun ? "Starting Run…" : "Run Workflow"}</span>
          </button>
        </div>
      </div>

      {/* ── Banner: Workflow Run Started Notification ─────────────────────── */}
      {runStartedId && (
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
                Workflow run successfully initiated! ID:{" "}
                <span className="font-mono font-semibold">{runStartedId}</span>
              </p>
              <p className="text-xs text-[var(--color-ink-muted)]">
                State saved with cryptographic hash checkpoint. Live execution in progress.
              </p>
            </div>
          </div>
          <Link
            href={`/workflows/${runStartedId}`}
            className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold text-white transition-opacity hover:opacity-90"
            style={{ backgroundColor: "var(--color-status-done)" }}
          >
            <span>View Run Timeline</span>
            <ArrowRight size={13} />
          </Link>
        </div>
      )}

      {/* ── Workflow Selector Strip ────────────────────────────────────────── */}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {WORKFLOW_DEFS.map((wf) => {
          const isSelected = wf.slug === selectedWorkflow.slug;
          const trig = triggerConfig[wf.trigger];
          const TrigIcon = trig.icon;

          return (
            <div
              key={wf.slug}
              onClick={() => {
                setSelectedWorkflow(wf);
                setAutonomy(wf.autonomyDefault);
                setSelectedStepIndex(0);
              }}
              className={`rounded-xl border p-4 cursor-pointer transition-all ${
                isSelected
                  ? "border-[var(--color-primary)] shadow-sm bg-[var(--color-surface)] ring-1 ring-[var(--color-primary-tint)]"
                  : "border-[var(--color-border-subtle)] bg-[var(--color-surface)] hover:border-[var(--color-border-strong)] opacity-80 hover:opacity-100"
              }`}
            >
              <div className="flex items-start justify-between">
                <div
                  className="flex h-8 w-8 items-center justify-center rounded-lg"
                  style={{
                    backgroundColor: isSelected
                      ? "var(--color-primary-tint)"
                      : "var(--color-surface-sunken)",
                  }}
                >
                  <GitBranch
                    size={16}
                    className={
                      isSelected ? "text-[var(--color-primary)]" : "text-[var(--color-ink-muted)]"
                    }
                  />
                </div>
                <span
                  className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-medium"
                  style={{
                    backgroundColor: "var(--color-surface-sunken)",
                    color: trig.color,
                  }}
                >
                  <TrigIcon size={10} />
                  {trig.label}
                </span>
              </div>

              <h3 className="mt-3 text-sm font-semibold text-[var(--color-ink)] truncate">
                {wf.name}
              </h3>
              <p className="mt-1 text-xs text-[var(--color-ink-muted)] line-clamp-2 leading-relaxed">
                {wf.description}
              </p>

              <div
                className="mt-3 flex items-center justify-between border-t pt-2 text-[11px] text-[var(--color-ink-faint)]"
                style={{ borderColor: "var(--color-border-subtle)" }}
              >
                <span>{wf.steps.length} nodes</span>
                <span>{wf.runsToday} runs today</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* ── Main Studio Work Area ──────────────────────────────────────────── */}
      <div
        className="rounded-2xl border bg-[var(--color-surface)] shadow-sm overflow-hidden"
        style={{ borderColor: "var(--color-border-subtle)" }}
      >
        {/* Top Control Bar */}
        <div
          className="flex flex-wrap items-center justify-between gap-4 border-b px-6 py-4"
          style={{ borderColor: "var(--color-border-subtle)" }}
        >
          <div className="flex items-center gap-3">
            <div>
              <div className="flex items-center gap-2">
                <h2 className="font-heading text-lg font-semibold text-[var(--color-ink)]">
                  {selectedWorkflow.name}
                </h2>
                <Badge variant="outline" className="font-mono text-xs">
                  v1.0
                </Badge>
              </div>
              <p className="text-xs text-[var(--color-ink-muted)] mt-0.5">
                Slug: <code className="font-mono">{selectedWorkflow.slug}</code> · Trigger:{" "}
                {selectedWorkflow.trigger}
              </p>
            </div>
          </div>

          {/* Autonomy Dial Integration (EPIC-14-T06) */}
          <div className="flex items-center gap-4">
            <div className="flex flex-col items-end">
              <span className="text-[11px] font-medium uppercase tracking-wider text-[var(--color-ink-faint)]">
                Autonomy Dial
              </span>
              <span className="text-xs text-[var(--color-ink-muted)]">
                Active execution governance
              </span>
            </div>
            <div className="w-64 sm:w-72">
              <AutonomyDial
                size="sm"
                value={autonomy}
                onChange={(lvl) => setAutonomy(lvl)}
              />
            </div>
          </div>

          {/* View mode switcher */}
          <div
            className="flex items-center rounded-lg p-1 border text-xs font-medium"
            style={{
              backgroundColor: "var(--color-surface-sunken)",
              borderColor: "var(--color-border-subtle)",
            }}
          >
            <button
              onClick={() => setActiveTab("visual")}
              className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 transition-all cursor-pointer ${
                activeTab === "visual"
                  ? "bg-[var(--color-surface)] text-[var(--color-ink)] font-semibold shadow-xs"
                  : "text-[var(--color-ink-muted)] hover:text-[var(--color-ink)]"
              }`}
            >
              <Cpu size={13} />
              <span>Visual Graph</span>
            </button>
            <button
              onClick={() => setActiveTab("yaml")}
              className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 transition-all cursor-pointer ${
                activeTab === "yaml"
                  ? "bg-[var(--color-surface)] text-[var(--color-ink)] font-semibold shadow-xs"
                  : "text-[var(--color-ink-muted)] hover:text-[var(--color-ink)]"
              }`}
            >
              <FileCode size={13} />
              <span>YAML Spec</span>
            </button>
            <Link
              href="/workflows/run_001"
              className="flex items-center gap-1.5 rounded-md px-3 py-1.5 text-[var(--color-ink-muted)] hover:text-[var(--color-ink)] cursor-pointer"
            >
              <Radio size={13} />
              <span>Live Replay</span>
            </Link>
          </div>
        </div>

        {/* Tab 1: Visual Interactive Step Flow */}
        {activeTab === "visual" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 min-h-[460px]">
            {/* Visual Canvas (Spans 2 cols) */}
            <div
              className="col-span-1 lg:col-span-2 p-6 border-b lg:border-b-0 lg:border-r relative overflow-y-auto"
              style={{
                borderColor: "var(--color-border-subtle)",
                backgroundColor: "var(--color-surface)",
              }}
            >
              <div className="mb-4 flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wider text-[var(--color-ink-faint)]">
                  Sequential Step Pipeline
                </span>
                <span className="text-xs text-[var(--color-ink-muted)]">
                  Click any step node to inspect parameters & model tier
                </span>
              </div>

              {/* Step Sequence Flow */}
              <div className="space-y-3 relative">
                {selectedWorkflow.steps.map((step, idx) => {
                  const isCurrent = idx === selectedStepIndex;
                  const isApproval = step.type === "approval";
                  const isParallel = step.type === "parallel";

                  return (
                    <div key={step.name} className="relative">
                      {/* Connector Line to next step */}
                      {idx < selectedWorkflow.steps.length - 1 && (
                        <div
                          className="absolute left-6 top-12 h-6 w-0.5 -ml-[1px] transition-colors"
                          style={{
                            backgroundColor: isCurrent
                              ? "var(--color-primary)"
                              : "var(--color-border)",
                          }}
                        />
                      )}

                      {/* Step Card Node */}
                      <div
                        onClick={() => setSelectedStepIndex(idx)}
                        className={`flex items-center justify-between rounded-xl border p-4 cursor-pointer transition-all ${
                          isCurrent
                            ? "border-[var(--color-primary)] bg-[var(--color-primary-subtle)] shadow-xs scale-[1.01]"
                            : "border-[var(--color-border-subtle)] bg-[var(--color-surface)] hover:border-[var(--color-border-strong)]"
                        }`}
                      >
                        <div className="flex items-center gap-3.5">
                          {/* Step Index Badge */}
                          <div
                            className={`flex h-8 w-8 items-center justify-center rounded-lg font-mono text-xs font-bold transition-colors ${
                              isCurrent
                                ? "bg-[var(--color-primary)] text-white shadow-xs"
                                : "bg-[var(--color-surface-sunken)] text-[var(--color-ink-muted)]"
                            }`}
                          >
                            {idx + 1}
                          </div>

                          <div>
                            <div className="flex items-center gap-2">
                              <h4 className="text-sm font-semibold text-[var(--color-ink)]">
                                {step.name}
                              </h4>
                              {isApproval && (
                                <span
                                  className="rounded-full px-2 py-0.5 text-[10px] font-semibold"
                                  style={{
                                    backgroundColor: "var(--color-status-waiting-bg)",
                                    color: "var(--color-saffron-dark)",
                                  }}
                                >
                                  Human Gate
                                </span>
                              )}
                              {isParallel && (
                                <span
                                  className="rounded-full px-2 py-0.5 text-[10px] font-semibold"
                                  style={{
                                    backgroundColor: "var(--color-primary-tint)",
                                    color: "var(--color-primary)",
                                  }}
                                >
                                  Parallel Fan-Out
                                </span>
                              )}
                            </div>
                            <p className="mt-0.5 text-xs text-[var(--color-ink-muted)] line-clamp-1">
                              {step.description}
                            </p>
                          </div>
                        </div>

                        {/* Right metadata badges */}
                        <div className="flex items-center gap-2">
                          {step.modelTier && (
                            <span className="font-mono text-[11px] rounded px-2 py-0.5 border text-[var(--color-ink-muted)] border-[var(--color-border-subtle)]">
                              {step.modelTier}
                            </span>
                          )}
                          <ChevronRight
                            size={16}
                            className={`transition-transform ${
                              isCurrent
                                ? "rotate-90 text-[var(--color-primary)]"
                                : "text-[var(--color-ink-faint)]"
                            }`}
                          />
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Step Detail Inspector (Spans 1 col) */}
            <div
              className="col-span-1 p-6 space-y-6"
              style={{ backgroundColor: "var(--color-surface-sunken)" }}
            >
              <div className="flex items-center justify-between border-b pb-3" style={{ borderColor: "var(--color-border-subtle)" }}>
                <div className="flex items-center gap-2">
                  <Settings2 size={16} className="text-[var(--color-primary)]" />
                  <h3 className="font-heading text-sm font-semibold text-[var(--color-ink)]">
                    Step Inspector
                  </h3>
                </div>
                <Badge variant="outline" className="font-mono text-[11px]">
                  Step {selectedStepIndex + 1} of {selectedWorkflow.steps.length}
                </Badge>
              </div>

              {selectedStep ? (
                <div className="space-y-5">
                  <div>
                    <span className="text-[11px] uppercase tracking-wider font-medium text-[var(--color-ink-faint)]">
                      Step Name
                    </span>
                    <h4 className="mt-1 font-heading text-base font-bold text-[var(--color-ink)]">
                      {selectedStep.name}
                    </h4>
                    <p className="mt-1 text-xs text-[var(--color-ink-muted)] leading-relaxed">
                      {selectedStep.description}
                    </p>
                  </div>

                  <div className="space-y-3 rounded-xl border bg-[var(--color-surface)] p-4" style={{ borderColor: "var(--color-border-subtle)" }}>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-[var(--color-ink-muted)]">Step Type:</span>
                      <span className="font-mono font-medium uppercase text-[var(--color-ink)]">
                        {selectedStep.type}
                      </span>
                    </div>

                    {selectedStep.agent && (
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-[var(--color-ink-muted)]">Assigned Agent:</span>
                        <span className="font-medium text-[var(--color-primary)]">
                          {selectedStep.agent}
                        </span>
                      </div>
                    )}

                    {selectedStep.connector && (
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-[var(--color-ink-muted)]">Connector Target:</span>
                        <span className="font-medium text-[var(--color-ink)]">
                          {selectedStep.connector}
                        </span>
                      </div>
                    )}

                    {selectedStep.modelTier && (
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-[var(--color-ink-muted)]">LLM Tier:</span>
                        <span className="font-mono font-semibold capitalize text-[var(--color-ink)]">
                          {selectedStep.modelTier} Model
                        </span>
                      </div>
                    )}

                    {selectedStep.riskLevel && (
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-[var(--color-ink-muted)]">Risk Classification:</span>
                        <span className="font-semibold uppercase text-[var(--color-status-failed)]">
                          {selectedStep.riskLevel} Risk
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Autonomy Dial Behavior for this node */}
                  <div
                    className="rounded-xl p-4 border text-xs space-y-2"
                    style={{
                      backgroundColor:
                        autonomy === "autonomous" && selectedStep.type !== "approval"
                          ? "var(--color-ai-accent-bg)"
                          : "var(--color-surface)",
                      borderColor: "var(--color-border-subtle)",
                    }}
                  >
                    <div className="flex items-center gap-2 font-semibold text-[var(--color-ink)]">
                      <Shield size={14} className="text-[var(--color-primary)]" />
                      <span>Governance Policy Rule</span>
                    </div>
                    <p className="text-[var(--color-ink-muted)] leading-relaxed">
                      {selectedStep.type === "approval"
                        ? "Dual-Approval required under Supervised mode. In Autonomous mode, can only auto-resolve if confidence >= 0.95."
                        : `Step runs autonomously under ${autonomy} mode with continuous ledger event emission.`}
                    </p>
                  </div>
                </div>
              ) : (
                <p className="text-xs text-[var(--color-ink-muted)]">No step selected.</p>
              )}
            </div>
          </div>
        )}

        {/* Tab 2: YAML Specification */}
        {activeTab === "yaml" && (
          <div className="p-6">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold uppercase tracking-wider text-[var(--color-ink-faint)]">
                YAML Workflow Definition (Pydantic Validated)
              </span>
              <span className="font-mono text-xs text-[var(--color-ink-muted)]">
                {selectedWorkflow.slug}.yaml
              </span>
            </div>
            <pre
              className="rounded-xl p-5 font-mono text-xs leading-relaxed overflow-x-auto border"
              style={{
                backgroundColor: "var(--color-surface-sunken)",
                borderColor: "var(--color-border-subtle)",
                color: "var(--color-ink)",
              }}
            >
              {selectedWorkflow.yamlCode}
            </pre>
          </div>
        )}
      </div>

      {/* ── Recent Runs for this Workflow ──────────────────────────────────── */}
      <div
        className="rounded-2xl border bg-[var(--color-surface)] shadow-sm overflow-hidden"
        style={{ borderColor: "var(--color-border-subtle)" }}
      >
        <div
          className="flex items-center justify-between border-b px-6 py-4"
          style={{ borderColor: "var(--color-border-subtle)" }}
        >
          <div className="flex items-center gap-2">
            <Radio size={16} className="text-[var(--color-primary)]" />
            <h3 className="font-heading text-base font-semibold text-[var(--color-ink)]">
              Recent Execution Runs
            </h3>
          </div>
          <span className="text-xs text-[var(--color-ink-muted)]">
            Click any run to open vertical timeline & step-by-step decision replay
          </span>
        </div>

        <div className="divide-y" style={{ borderColor: "var(--color-border-subtle)" }}>
          {[
            {
              id: "run_001",
              name: "Exam Marks Processing — CS301",
              status: "running" as const,
              step: "Evaluate Answers (Step 2/6)",
              started: "4 min ago",
              cost: "$0.32",
              autonomy: "Supervised",
            },
            {
              id: "run_002",
              name: "Assignment Cycle — CS201 Midterms",
              status: "waiting" as const,
              step: "Faculty Approval Gate (Step 4/5)",
              started: "22 min ago",
              cost: "$1.18",
              autonomy: "Supervised",
            },
            {
              id: "run_003",
              name: "Student Leave — Roll 2024-CS-041",
              status: "done" as const,
              step: "ERP Attendance Updated (Step 4/4)",
              started: "1h ago",
              cost: "$0.09",
              autonomy: "Autonomous",
            },
          ].map((run) => (
            <Link
              key={run.id}
              href={`/workflows/${run.id}`}
              className="flex items-center justify-between px-6 py-4 transition-colors hover:bg-[var(--color-surface-sunken)] group cursor-pointer"
            >
              <div className="flex items-center gap-4">
                <StatusBadge status={run.status} />
                <div>
                  <h4 className="text-sm font-semibold text-[var(--color-ink)] group-hover:text-[var(--color-primary)] transition-colors">
                    {run.name}
                  </h4>
                  <div className="mt-1 flex items-center gap-2 font-mono text-xs text-[var(--color-ink-muted)]">
                    <span>{run.id}</span>
                    <span>·</span>
                    <span>{run.step}</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-6">
                <div className="text-right hidden sm:block">
                  <p className="text-xs font-medium text-[var(--color-ink)]">{run.autonomy}</p>
                  <p className="font-mono text-[11px] text-[var(--color-ink-faint)]">
                    {run.cost} · {run.started}
                  </p>
                </div>
                <ArrowRight
                  size={15}
                  className="text-[var(--color-ink-faint)] group-hover:text-[var(--color-primary)] group-hover:translate-x-1 transition-all"
                />
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
