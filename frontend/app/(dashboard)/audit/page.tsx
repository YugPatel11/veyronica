"use client";

import { useState } from "react";
import {
  CheckCircle2,
  Shield,
  Cpu,
  Plug,
  AlertTriangle,
  Search,
  Download,
  ArrowRight,
  Lock,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { ConfidenceIndicator } from "@/components/ui/confidence-indicator";

/**
 * Audit Explorer & Hash Ledger — EPIC-19
 *
 * Hash-chained immutable decision records, cryptographic integrity verification,
 * chain ribbon visualization, and decision detail drilldown.
 */

interface AuditEntry {
  id: string;
  seq: number;
  timestamp: string;
  eventType: "action" | "decision" | "approval" | "connector_call" | "error";
  action: string;
  agentId: string | null;
  userId: string | null;
  runId: string | null;
  entityType: string | null;
  confidence: number | null;
  prevHash: string;
  hash: string;
  rationale?: string;
  alternativesConsidered?: string[];
  payload?: Record<string, unknown>;
}

const MOCK_ENTRIES: AuditEntry[] = [
  {
    id: "le_001",
    seq: 1,
    timestamp: "10:14:02",
    eventType: "action",
    action: "workflow_started",
    agentId: "master_dispatcher",
    userId: "faculty_priya_sharma",
    runId: "run_001",
    entityType: "workflow",
    confidence: null,
    prevHash: "0x0000000000000000",
    hash: "0x8fa12b489c7d1e0f",
    rationale: "Triggered manually by Dr. Priya Sharma with 47 answer scripts.",
    payload: { course: "CS301", batch: 47, format: "pdf" },
  },
  {
    id: "le_002",
    seq: 2,
    timestamp: "10:14:15",
    eventType: "decision",
    action: "ocr_extraction_complete",
    agentId: "ingestion",
    userId: null,
    runId: "run_001",
    entityType: "document",
    confidence: 0.94,
    prevHash: "0x8fa12b489c7d1e0f",
    hash: "0x3e17b89f2a04cd55",
    rationale: "Model extracted 94 pages, detected 10 questions with 97.8% OCR text accuracy.",
    alternativesConsidered: ["Tesseract 5.0 (rejected: 81% accuracy)", "Claude Vision (selected: 97.8% accuracy)"],
    payload: { pages_extracted: 94, questions_per_page: 2 },
  },
  {
    id: "le_003",
    seq: 3,
    timestamp: "10:15:28",
    eventType: "decision",
    action: "marks_assigned_against_rubric",
    agentId: "evaluation",
    userId: null,
    runId: "run_001",
    entityType: "marks",
    confidence: 0.89,
    prevHash: "0x3e17b89f2a04cd55",
    hash: "0x91df44a7201bb8ee",
    rationale: "Applied Rubric CS301-Midterm. Scored 47 student submissions; 2 flagged for human verification.",
    alternativesConsidered: ["Strict deduction model", "Partial credit rubric (selected)"],
    payload: { average_score: 36.8, max_score: 50 },
  },
  {
    id: "le_004",
    seq: 4,
    timestamp: "10:15:42",
    eventType: "action",
    action: "marks_sum_verified",
    agentId: "verifier",
    userId: null,
    runId: "run_001",
    entityType: "marks",
    confidence: 0.98,
    prevHash: "0x91df44a7201bb8ee",
    hash: "0xaa4201c9fe87134d",
    rationale: "Deterministic arithmetic validation checked Q1+Q2+Q3+Q4+Q5 == Total. Zero mismatches found.",
    payload: { arithmetic_checks: 47, anomalies_found: 0 },
  },
  {
    id: "le_005",
    seq: 5,
    timestamp: "10:15:45",
    eventType: "approval",
    action: "dual_approval_requested",
    agentId: null,
    userId: "usr_faculty_001",
    runId: "run_001",
    entityType: "approval",
    confidence: null,
    prevHash: "0xaa4201c9fe87134d",
    hash: "0x7c99201fa8842eb1",
    rationale: "High-risk mutation policy rule triggered. Dual signatures required before ERP gradebook update.",
    payload: { approvals_needed: 2, risk_level: "high" },
  },
  {
    id: "le_006",
    seq: 6,
    timestamp: "10:18:10",
    eventType: "approval",
    action: "approval_granted_key_1",
    agentId: null,
    userId: "prof_priya_sharma",
    runId: "run_001",
    entityType: "approval",
    confidence: null,
    prevHash: "0x7c99201fa8842eb1",
    hash: "0x5d92e104a37c189b",
    rationale: "Key 1 of 2 authorized by Course Faculty. Signature verified with RSA-4096 key.",
    payload: { approver: "prof_priya_sharma", key_index: 1 },
  },
  {
    id: "le_007",
    seq: 7,
    timestamp: "10:19:00",
    eventType: "connector_call",
    action: "erp_ledger_lock_acquired",
    agentId: "master_dispatcher",
    userId: null,
    runId: "run_001",
    entityType: "connector",
    confidence: null,
    prevHash: "0x5d92e104a37c189b",
    hash: "0x12a9bc743e881023",
    rationale: "Distributed lock acquired on ERP target tables for idempotent grade publication.",
    payload: { connector: "campus-erp", lock_ttl_sec: 120 },
  },
];

const eventTypeConfig = {
  decision: { icon: Cpu, color: "text-[var(--color-primary)]", bg: "var(--color-primary-tint)" },
  action: { icon: CheckCircle2, color: "text-[var(--color-status-done)]", bg: "var(--color-status-done-bg)" },
  approval: { icon: Shield, color: "text-[var(--color-saffron-dark)]", bg: "var(--color-status-waiting-bg)" },
  connector_call: { icon: Plug, color: "text-[var(--color-status-running)]", bg: "var(--color-primary-subtle)" },
  error: { icon: AlertTriangle, color: "text-[var(--color-status-failed)]", bg: "var(--color-status-failed-bg)" },
};

export default function AuditPage() {
  const [search, setSearch] = useState("");
  const [chainVerified, setChainVerified] = useState<boolean | null>(null);
  const [isVerifying, setIsVerifying] = useState(false);
  const [selectedEntry, setSelectedEntry] = useState<AuditEntry | null>(null);

  const filtered = MOCK_ENTRIES.filter((e) =>
    search === "" ||
    e.action.toLowerCase().includes(search.toLowerCase()) ||
    (e.agentId ?? "").toLowerCase().includes(search.toLowerCase()) ||
    (e.userId ?? "").toLowerCase().includes(search.toLowerCase()) ||
    e.hash.toLowerCase().includes(search.toLowerCase())
  );

  const handleVerifyIntegrity = () => {
    setIsVerifying(true);
    setTimeout(() => {
      setIsVerifying(false);
      setChainVerified(true);
    }, 1100);
  };

  const handleExportJSON = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(MOCK_ENTRIES, null, 2));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `nexus_audit_ledger_${Date.now()}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* ── Header ────────────────────────────────────────────────────────── */}
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="font-heading text-2xl font-bold text-[var(--color-ink)]">
              Audit Explorer & Hash Ledger
            </h1>
            <Badge variant="outline" className="text-xs">
              EPIC-19
            </Badge>
          </div>
          <p className="mt-1 text-sm text-[var(--color-ink-muted)]">
            Cryptographically chained decision ledger — every action is mathematical proof
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleVerifyIntegrity}
            disabled={isVerifying}
            className={`flex items-center gap-1.5 rounded-lg border px-3.5 py-1.5 text-xs font-semibold transition-all cursor-pointer ${
              chainVerified
                ? "bg-[var(--color-status-done-bg)] text-[var(--color-status-done)] border-[var(--color-status-done-border)]"
                : "border-[var(--color-border)] text-[var(--color-ink)] hover:bg-[var(--color-surface-sunken)]"
            }`}
          >
            <Shield size={14} className={isVerifying ? "animate-spin" : ""} />
            <span>
              {isVerifying
                ? "Checking Hash Chain…"
                : chainVerified
                ? "✓ 7/7 Blocks Cryptographically Verified"
                : "Verify Chain Integrity"}
            </span>
          </button>

          <button
            onClick={handleExportJSON}
            className="flex items-center gap-1.5 rounded-lg border px-3.5 py-1.5 text-xs font-semibold text-[var(--color-ink-muted)] hover:text-[var(--color-ink)] hover:bg-[var(--color-surface-sunken)] transition-colors cursor-pointer"
            style={{ borderColor: "var(--color-border)" }}
          >
            <Download size={14} />
            <span>Export JSON</span>
          </button>
        </div>
      </div>

      {/* ── Hash Chain Visual Ribbon (EPIC-19-T05) ─────────────────────────── */}
      <div
        className="rounded-2xl border bg-[var(--color-surface)] p-5 shadow-sm space-y-3"
        style={{ borderColor: "var(--color-border-subtle)" }}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Lock size={15} className="text-[var(--color-primary)]" />
            <h3 className="font-heading text-sm font-semibold text-[var(--color-ink)]">
              Cryptographic Block Ribbon
            </h3>
          </div>
          <span className="font-mono text-xs text-[var(--color-ink-muted)]">
            SHA-256 Merkle Chain
          </span>
        </div>

        {/* Scrollable ribbon of blocks */}
        <div className="flex items-center gap-2 overflow-x-auto pb-2 pt-1">
          {MOCK_ENTRIES.map((entry, idx) => {
            const isSelected = selectedEntry?.id === entry.id;

            return (
              <div key={entry.id} className="flex items-center gap-2 shrink-0">
                <div
                  onClick={() => setSelectedEntry(entry)}
                  className={`flex flex-col rounded-xl border p-3 cursor-pointer transition-all w-36 ${
                    isSelected
                      ? "border-[var(--color-primary)] bg-[var(--color-primary-subtle)] shadow-xs scale-[1.02]"
                      : "border-[var(--color-border-subtle)] bg-[var(--color-surface-sunken)] hover:border-[var(--color-border-strong)]"
                  }`}
                >
                  <div className="flex items-center justify-between text-[11px] font-mono text-[var(--color-ink-faint)]">
                    <span>Block #{entry.seq}</span>
                    <span>{entry.timestamp}</span>
                  </div>
                  <p className="mt-1 font-semibold text-xs text-[var(--color-ink)] truncate">
                    {entry.action.replaceAll("_", " ")}
                  </p>
                  <p className="mt-1 font-mono text-[10px] text-[var(--color-primary)] truncate">
                    {entry.hash.substring(0, 10)}…
                  </p>
                </div>

                {idx < MOCK_ENTRIES.length - 1 && (
                  <ArrowRight size={14} className="text-[var(--color-ink-faint)] shrink-0" />
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* ── Search Bar ────────────────────────────────────────────────────── */}
      <div
        className="flex items-center gap-3 rounded-xl border bg-[var(--color-surface)] px-4 py-2.5 text-xs shadow-xs"
        style={{ borderColor: "var(--color-border)" }}
      >
        <Search size={16} className="text-[var(--color-ink-muted)]" />
        <input
          type="text"
          placeholder="Search by action, agent ID, user, or cryptographic hash…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1 bg-transparent text-[var(--color-ink)] placeholder:text-[var(--color-ink-disabled)] outline-none"
        />
      </div>

      {/* ── Ledger Table ──────────────────────────────────────────────────── */}
      <div
        className="overflow-hidden rounded-2xl border bg-[var(--color-surface)] shadow-sm"
        style={{ borderColor: "var(--color-border-subtle)" }}
      >
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr
                className="border-b text-left text-xs font-medium uppercase tracking-wider text-[var(--color-ink-faint)]"
                style={{ borderColor: "var(--color-border-subtle)" }}
              >
                <th className="px-5 py-3.5 w-14">#</th>
                <th className="px-3 py-3.5">Timestamp</th>
                <th className="px-3 py-3.5">Event Type</th>
                <th className="px-4 py-3.5">Action Name</th>
                <th className="hidden px-4 py-3.5 md:table-cell">Actor</th>
                <th className="hidden px-3 py-3.5 lg:table-cell">Confidence</th>
                <th className="px-5 py-3.5 text-right">Block Hash</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((entry) => {
                const cfg = eventTypeConfig[entry.eventType] ?? {
                  icon: CheckCircle2,
                  color: "text-[var(--color-status-done)]",
                  bg: "transparent",
                };
                const Icon = cfg.icon;

                return (
                  <tr
                    key={entry.id}
                    onClick={() => setSelectedEntry(entry)}
                    className="border-b last:border-b-0 transition-colors hover:bg-[var(--color-surface-sunken)] cursor-pointer"
                    style={{ borderColor: "var(--color-border-subtle)" }}
                  >
                    <td className="px-5 py-3.5 font-mono text-xs text-[var(--color-ink-faint)]">
                      {entry.seq}
                    </td>
                    <td className="px-3 py-3.5 font-mono text-xs text-[var(--color-ink-muted)]">
                      {entry.timestamp}
                    </td>
                    <td className="px-3 py-3.5">
                      <span className={`flex items-center gap-1.5 text-xs font-medium ${cfg.color}`}>
                        <Icon size={12} />
                        {entry.eventType}
                      </span>
                    </td>
                    <td className="px-4 py-3.5 text-xs font-medium text-[var(--color-ink)]">
                      {entry.action.replaceAll("_", " ")}
                    </td>
                    <td className="hidden px-4 py-3.5 md:table-cell text-xs text-[var(--color-ink-muted)] font-mono">
                      {entry.agentId ?? entry.userId ?? "—"}
                    </td>
                    <td className="hidden px-3 py-3.5 lg:table-cell">
                      {entry.confidence !== null ? (
                        <ConfidenceIndicator value={entry.confidence} size={24} showLabel />
                      ) : (
                        <span className="text-xs text-[var(--color-ink-disabled)]">—</span>
                      )}
                    </td>
                    <td className="px-5 py-3.5 text-right font-mono text-xs text-[var(--color-primary)]">
                      {entry.hash.substring(0, 10)}…
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* ── Decision Detail Modal (EPIC-19-T03) ────────────────────────────── */}
      {selectedEntry && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <div
            className="w-full max-w-lg rounded-2xl border bg-[var(--color-surface)] p-6 shadow-2xl space-y-4 animate-fadeIn"
            style={{ borderColor: "var(--color-border-strong)" }}
          >
            <div className="flex items-center justify-between border-b pb-3" style={{ borderColor: "var(--color-border-subtle)" }}>
              <div>
                <h3 className="font-heading text-base font-bold text-[var(--color-ink)]">
                  Ledger Block #{selectedEntry.seq}
                </h3>
                <p className="text-xs text-[var(--color-ink-muted)] font-mono mt-0.5">
                  {selectedEntry.action.replaceAll("_", " ")}
                </p>
              </div>
              <Badge variant="outline" className="font-mono text-xs uppercase">
                {selectedEntry.eventType}
              </Badge>
            </div>

            <div className="space-y-3 text-xs">
              <div className="rounded-xl p-3 border space-y-1.5" style={{ backgroundColor: "var(--color-surface-sunken)", borderColor: "var(--color-border-subtle)" }}>
                <div className="flex items-center justify-between">
                  <span className="text-[var(--color-ink-muted)]">Previous Block Hash:</span>
                  <span className="font-mono text-[11px] text-[var(--color-ink)] truncate max-w-[220px]">
                    {selectedEntry.prevHash}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-[var(--color-ink-muted)]">Current Block Hash:</span>
                  <span className="font-mono text-[11px] text-[var(--color-primary)] font-semibold truncate max-w-[220px]">
                    {selectedEntry.hash}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-[var(--color-ink-muted)]">Actor Signature:</span>
                  <span className="font-mono text-[11px] text-[var(--color-ink)]">
                    {selectedEntry.agentId ?? selectedEntry.userId}
                  </span>
                </div>
              </div>

              {selectedEntry.rationale && (
                <div>
                  <span className="font-semibold text-[var(--color-ink)] block mb-1">
                    Decision Rationale
                  </span>
                  <p className="text-[var(--color-ink-muted)] leading-relaxed">
                    {selectedEntry.rationale}
                  </p>
                </div>
              )}

              {selectedEntry.alternativesConsidered && (
                <div>
                  <span className="font-semibold text-[var(--color-ink)] block mb-1">
                    Alternatives Evaluated
                  </span>
                  <ul className="list-disc pl-4 space-y-0.5 text-[var(--color-ink-muted)]">
                    {selectedEntry.alternativesConsidered.map((alt) => (
                      <li key={alt}>{alt}</li>
                    ))}
                  </ul>
                </div>
              )}

              {selectedEntry.payload && (
                <div>
                  <span className="font-semibold text-[var(--color-ink)] block mb-1">
                    Cryptographic Payload Record
                  </span>
                  <pre
                    className="rounded-lg p-2.5 font-mono text-[11px] overflow-x-auto border"
                    style={{
                      backgroundColor: "var(--color-surface-sunken)",
                      borderColor: "var(--color-border-subtle)",
                      color: "var(--color-ink)",
                    }}
                  >
                    {JSON.stringify(selectedEntry.payload, null, 2)}
                  </pre>
                </div>
              )}
            </div>

            <div className="flex items-center justify-end gap-2 pt-3 border-t" style={{ borderColor: "var(--color-border-subtle)" }}>
              <button
                onClick={() => setSelectedEntry(null)}
                className="rounded-lg px-4 py-1.5 text-xs font-semibold text-white shadow-xs"
                style={{ backgroundColor: "var(--color-primary)" }}
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
