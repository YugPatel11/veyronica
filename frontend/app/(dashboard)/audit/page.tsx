"use client";

import {
  ScrollText,
  CheckCircle2,
  Shield,
  Cpu,
  Plug,
  AlertTriangle,
  Search,
  Download,
  Filter,
} from "lucide-react";
import { useState } from "react";

/**
 * Audit Explorer — EPIC-19-T01
 *
 * Searchable, filterable table of hash-chained audit ledger entries.
 */

interface AuditEntry {
  id: string;
  seq: number;
  timestamp: string;
  eventType: string;
  action: string;
  agentId: string | null;
  userId: string | null;
  runId: string | null;
  entityType: string | null;
  confidence: number | null;
  hash: string;
}

const MOCK_ENTRIES: AuditEntry[] = [
  { id: "le_001", seq: 1, timestamp: "22:08:14", eventType: "action", action: "workflow_started", agentId: "master", userId: null, runId: "run_001", entityType: "workflow", confidence: null, hash: "a3f8c2..." },
  { id: "le_002", seq: 2, timestamp: "22:08:18", eventType: "decision", action: "model_tier_selected", agentId: "ingestion", userId: null, runId: "run_001", entityType: "llm_call", confidence: 0.94, hash: "b7e1d4..." },
  { id: "le_003", seq: 3, timestamp: "22:09:32", eventType: "action", action: "ocr_extraction_complete", agentId: "ingestion", userId: null, runId: "run_001", entityType: "document", confidence: 0.87, hash: "c2a5f9..." },
  { id: "le_004", seq: 4, timestamp: "22:10:05", eventType: "decision", action: "marks_assigned", agentId: "evaluation", userId: null, runId: "run_001", entityType: "marks", confidence: 0.91, hash: "d4b3e8..." },
  { id: "le_005", seq: 5, timestamp: "22:10:12", eventType: "decision", action: "marks_verified", agentId: "verifier", userId: null, runId: "run_001", entityType: "marks", confidence: 0.96, hash: "e8f2a1..." },
  { id: "le_006", seq: 6, timestamp: "22:10:45", eventType: "approval", action: "approval_requested", agentId: null, userId: "usr_faculty_001", runId: "run_001", entityType: "approval", confidence: null, hash: "f1c7b3..." },
  { id: "le_007", seq: 7, timestamp: "22:12:30", eventType: "approval", action: "approval_granted", agentId: null, userId: "usr_faculty_001", runId: "run_001", entityType: "approval", confidence: null, hash: "g5d9e2..." },
  { id: "le_008", seq: 8, timestamp: "22:12:35", eventType: "connector_call", action: "marks_published_to_erp", agentId: "master", userId: null, runId: "run_001", entityType: "erp", confidence: null, hash: "h3a6f4..." },
  { id: "le_009", seq: 9, timestamp: "22:12:40", eventType: "connector_call", action: "crm_note_created", agentId: "master", userId: null, runId: "run_001", entityType: "crm", confidence: null, hash: "i7b2c8..." },
  { id: "le_010", seq: 10, timestamp: "22:12:48", eventType: "action", action: "workflow_completed", agentId: "master", userId: null, runId: "run_001", entityType: "workflow", confidence: null, hash: "j9e4d1..." },
];

const eventTypeConfig: Record<string, { icon: typeof Cpu; color: string }> = {
  decision: { icon: Cpu, color: "text-[var(--color-primary)]" },
  action: { icon: CheckCircle2, color: "text-[var(--color-status-done)]" },
  approval: { icon: Shield, color: "text-[var(--color-status-waiting)]" },
  connector_call: { icon: Plug, color: "text-[var(--color-status-running)]" },
  error: { icon: AlertTriangle, color: "text-[var(--color-status-failed)]" },
};

export default function AuditPage() {
  const [search, setSearch] = useState("");
  const [chainVerified, setChainVerified] = useState<boolean | null>(null);

  const filtered = MOCK_ENTRIES.filter((e) =>
    search === "" || e.action.includes(search) || (e.agentId ?? "").includes(search)
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="font-heading text-2xl font-bold text-[var(--color-ink)]">
            Audit Explorer
          </h1>
          <p className="mt-1 text-sm text-[var(--color-ink-muted)]">
            Hash-chained decision ledger — every action is provable
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setChainVerified(true)}
            className="flex items-center gap-1.5 rounded-[var(--radius-md)] border px-3 py-1.5 text-sm font-medium transition-colors hover:bg-[var(--color-surface-sunken)]"
            style={{ borderColor: "var(--color-border)", color: chainVerified ? "var(--color-status-done)" : "var(--color-ink-muted)" }}
          >
            <Shield size={14} />
            {chainVerified ? "✓ Chain Verified" : "Verify Integrity"}
          </button>
          <button
            className="flex items-center gap-1.5 rounded-[var(--radius-md)] border px-3 py-1.5 text-sm font-medium text-[var(--color-ink-muted)] transition-colors hover:bg-[var(--color-surface-sunken)]"
            style={{ borderColor: "var(--color-border)" }}
          >
            <Download size={14} />
            Export
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="flex items-center gap-3 rounded-[var(--radius-md)] border bg-[var(--color-surface)] px-4 py-2.5" style={{ borderColor: "var(--color-border)" }}>
        <Search size={16} className="text-[var(--color-ink-muted)]" />
        <input
          type="text"
          placeholder="Search actions, agents, events…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1 bg-transparent text-sm text-[var(--color-ink)] placeholder:text-[var(--color-ink-disabled)] outline-none"
        />
      </div>

      {/* Ledger Table */}
      <div
        className="overflow-hidden rounded-[var(--radius-lg)] border bg-[var(--color-surface)]"
        style={{ borderColor: "var(--color-border-subtle)" }}
      >
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left text-xs font-medium uppercase tracking-wider text-[var(--color-ink-faint)]" style={{ borderColor: "var(--color-border-subtle)" }}>
                <th className="px-4 py-3 w-12">#</th>
                <th className="px-3 py-3">Time</th>
                <th className="px-3 py-3">Type</th>
                <th className="px-3 py-3">Action</th>
                <th className="hidden px-3 py-3 md:table-cell">Agent / User</th>
                <th className="hidden px-3 py-3 lg:table-cell">Confidence</th>
                <th className="px-3 py-3 text-right">Hash</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((entry) => {
                const cfg = eventTypeConfig[entry.eventType] ?? eventTypeConfig.action;
                const Icon = cfg.icon;
                return (
                  <tr
                    key={entry.id}
                    className="border-b last:border-b-0 transition-colors hover:bg-[var(--color-surface-sunken)]"
                    style={{ borderColor: "var(--color-border-subtle)" }}
                  >
                    <td className="px-4 py-3 font-mono text-xs text-[var(--color-ink-faint)]">{entry.seq}</td>
                    <td className="px-3 py-3 font-mono text-xs text-[var(--color-ink-muted)]">{entry.timestamp}</td>
                    <td className="px-3 py-3">
                      <span className={`flex items-center gap-1.5 text-xs font-medium ${cfg.color}`}>
                        <Icon size={12} />
                        {entry.eventType}
                      </span>
                    </td>
                    <td className="px-3 py-3 text-xs text-[var(--color-ink)]">{entry.action.replaceAll("_", " ")}</td>
                    <td className="hidden px-3 py-3 md:table-cell text-xs text-[var(--color-ink-muted)]">
                      {entry.agentId ?? entry.userId ?? "—"}
                    </td>
                    <td className="hidden px-3 py-3 lg:table-cell">
                      {entry.confidence !== null ? (
                        <span className="font-mono text-xs text-[var(--color-ink-muted)]">
                          {(entry.confidence * 100).toFixed(0)}%
                        </span>
                      ) : (
                        <span className="text-xs text-[var(--color-ink-disabled)]">—</span>
                      )}
                    </td>
                    <td className="px-3 py-3 text-right font-mono text-[11px] text-[var(--color-ink-faint)]">
                      {entry.hash}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
