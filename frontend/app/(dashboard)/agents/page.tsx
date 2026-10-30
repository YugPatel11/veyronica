"use client";

import { useState } from "react";
import {
  Network,
  Cpu,
  Shield,
  CheckCircle2,
  Clock,
  Zap,
  TrendingUp,
} from "lucide-react";
import { StatusBadge, type Status } from "@/components/ui/status-badge";
import { ConfidenceIndicator } from "@/components/ui/confidence-indicator";

interface AgentNode {
  id: string;
  name: string;
  role: string;
  status: "idle" | "running" | "waiting" | "done";
  tier: "tier_fast" | "tier_reasoning" | "tier_heavy";
  currentTask: string;
  tokensUsed: number;
  avgLatencyMs: number;
  confidence: number;
  lastHandoffTo?: string;
  coordinates: { x: number; y: number }; // Percentage on canvas
}

const INITIAL_AGENTS: AgentNode[] = [
  {
    id: "master",
    name: "Master Agent",
    role: "Orchestrator & Graph Dispatcher",
    status: "running",
    tier: "tier_reasoning",
    currentTask: "Orchestrating exam-marks-processing run_001",
    tokensUsed: 4210,
    avgLatencyMs: 680,
    confidence: 0.98,
    lastHandoffTo: "ingestion",
    coordinates: { x: 50, y: 16 },
  },
  {
    id: "ingestion",
    name: "Ingestion Agent",
    role: "OCR Extraction & File Parse",
    status: "done",
    tier: "tier_fast",
    currentTask: "Batch processed 47 answer sheets from MinIO",
    tokensUsed: 8900,
    avgLatencyMs: 420,
    confidence: 0.94,
    lastHandoffTo: "evaluation",
    coordinates: { x: 20, y: 44 },
  },
  {
    id: "evaluation",
    name: "Evaluation Agent",
    role: "Rubric Grading & Marks Derivation",
    status: "running",
    tier: "tier_heavy",
    currentTask: "Grading Student 24/47: Question 4 derivation",
    tokensUsed: 19800,
    avgLatencyMs: 1450,
    confidence: 0.88,
    lastHandoffTo: "verifier",
    coordinates: { x: 50, y: 48 },
  },
  {
    id: "verifier",
    name: "Verifier Agent",
    role: "Sum Check & Confidence Guard",
    status: "waiting",
    tier: "tier_fast",
    currentTask: "Awaiting evaluation completion of batch",
    tokensUsed: 1200,
    avgLatencyMs: 180,
    confidence: 0.99,
    lastHandoffTo: "analysis",
    coordinates: { x: 80, y: 44 },
  },
  {
    id: "analysis",
    name: "Analysis Agent",
    role: "Trends & Anomaly Detection",
    status: "idle",
    tier: "tier_reasoning",
    currentTask: "Standby for class grade distribution curve",
    tokensUsed: 650,
    avgLatencyMs: 510,
    confidence: 0.92,
    coordinates: { x: 30, y: 80 },
  },
  {
    id: "communication",
    name: "Communication Agent",
    role: "Parent & Faculty Drafts",
    status: "idle",
    tier: "tier_fast",
    currentTask: "Standby for email templates & SMS alerts",
    tokensUsed: 400,
    avgLatencyMs: 220,
    confidence: 0.95,
    coordinates: { x: 70, y: 80 },
  },
];

const HANDOFF_EDGES = [
  { from: "master", to: "ingestion", active: false },
  { from: "ingestion", to: "evaluation", active: true },
  { from: "evaluation", to: "verifier", active: true },
  { from: "verifier", to: "analysis", active: false },
  { from: "verifier", to: "communication", active: false },
];

/**
 * Agent Map — EPIC-13-T02 / T03 / T04 / T05
 *
 * Interactive visual agent topology showing live execution state, animated
 * handoffs, status glows, and deep task inspection.
 */
export default function AgentsPage() {
  const [agents] = useState<AgentNode[]>(INITIAL_AGENTS);
  const [selectedAgent, setSelectedAgent] = useState<AgentNode>(INITIAL_AGENTS[0]!);
  const [viewMode, setViewMode] = useState<"canvas" | "grid">("canvas");

  return (
    <div className="space-y-6">
      {/* ── Header ──────────────────────────────────────────────────────── */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="font-heading text-2xl font-bold text-[var(--color-ink)]">
            Agent Map
          </h1>
          <p className="mt-1 text-sm text-[var(--color-ink-muted)]">
            Specialist agent network, handoff pathways, and real-time inference telemetry
          </p>
        </div>

        {/* View Mode Switcher */}
        <div className="flex items-center gap-1.5 rounded-[var(--radius-md)] border border-[var(--color-border)] bg-[var(--color-surface)] p-1">
          <button
            onClick={() => setViewMode("canvas")}
            className={`rounded-[var(--radius-sm)] px-3 py-1 text-xs font-medium transition-colors ${
              viewMode === "canvas"
                ? "bg-[var(--color-primary-tint)] text-[var(--color-primary)] font-semibold"
                : "text-[var(--color-ink-muted)] hover:text-[var(--color-ink)]"
            }`}
          >
            Canvas View
          </button>
          <button
            onClick={() => setViewMode("grid")}
            className={`rounded-[var(--radius-sm)] px-3 py-1 text-xs font-medium transition-colors ${
              viewMode === "grid"
                ? "bg-[var(--color-primary-tint)] text-[var(--color-primary)] font-semibold"
                : "text-[var(--color-ink-muted)] hover:text-[var(--color-ink)]"
            }`}
          >
            Matrix View
          </button>
        </div>
      </div>

      {/* ── Main View Area ──────────────────────────────────────────────── */}
      {viewMode === "canvas" ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Interactive Topology Canvas */}
          <div className="lg:col-span-2 relative min-h-[500px] h-[580px] rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-surface)] overflow-hidden shadow-[var(--shadow-sm)]">
            {/* Background Grid Pattern */}
            <div
              className="absolute inset-0 opacity-20 pointer-events-none"
              style={{
                backgroundImage:
                  "radial-gradient(circle, var(--color-ink-faint) 1px, transparent 1px)",
                backgroundSize: "24px 24px",
              }}
            />

            {/* SVG Connecting Edges with animated dash arrays */}
            <svg className="absolute inset-0 h-full w-full pointer-events-none">
              <defs>
                <linearGradient id="edge-gradient-active" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="var(--color-primary)" />
                  <stop offset="100%" stopColor="var(--color-status-running)" />
                </linearGradient>
              </defs>

              {HANDOFF_EDGES.map((edge, idx) => {
                const source = agents.find((a) => a.id === edge.from);
                const target = agents.find((a) => a.id === edge.to);
                if (!source || !target) return null;

                const x1 = `${source.coordinates.x}%`;
                const y1 = `${source.coordinates.y}%`;
                const x2 = `${target.coordinates.x}%`;
                const y2 = `${target.coordinates.y}%`;

                return (
                  <g key={idx}>
                    {/* Shadow / Base Line */}
                    <line
                      x1={x1}
                      y1={y1}
                      x2={x2}
                      y2={y2}
                      stroke="var(--color-border)"
                      strokeWidth={edge.active ? 2.5 : 1.5}
                      strokeDasharray={edge.active ? "6, 6" : "3, 3"}
                    />
                    {/* Active Handoff Pulse Animation */}
                    {edge.active && (
                      <line
                        x1={x1}
                        y1={y1}
                        x2={x2}
                        y2={y2}
                        stroke="url(#edge-gradient-active)"
                        strokeWidth="2.5"
                        strokeDasharray="8, 6"
                        className="animate-pulse"
                      />
                    )}
                  </g>
                );
              })}
            </svg>

            {/* Interactive Agent Nodes */}
            {agents.map((agent) => {
              const isSelected = selectedAgent.id === agent.id;
              const isRunning = agent.status === "running";

              return (
                <div
                  key={agent.id}
                  onClick={() => setSelectedAgent(agent)}
                  className={`absolute -translate-x-1/2 -translate-y-1/2 cursor-pointer transition-all duration-200 select-none ${
                    isSelected ? "scale-105 z-20" : "hover:scale-102 z-10"
                  }`}
                  style={{
                    left: `${agent.coordinates.x}%`,
                    top: `${agent.coordinates.y}%`,
                  }}
                >
                  {/* Glowing Status Halo */}
                  {isRunning && (
                    <div className="absolute -inset-2 rounded-2xl bg-[var(--color-status-running)]/20 blur-md animate-pulse" />
                  )}

                  <div
                    className={`relative flex items-center gap-3 rounded-[var(--radius-lg)] border bg-[var(--color-surface)] px-4 py-3 shadow-[var(--shadow-md)] transition-colors ${
                      isSelected
                        ? "border-[var(--color-primary)] ring-2 ring-[var(--color-primary-tint)]"
                        : "border-[var(--color-border)] hover:border-[var(--color-border-strong)]"
                    }`}
                  >
                    <div
                      className={`flex h-10 w-10 items-center justify-center rounded-xl text-sm ${
                        agent.id === "master"
                          ? "bg-[var(--color-primary)] text-white shadow-sm"
                          : "bg-[var(--color-primary-tint)] text-[var(--color-primary)]"
                      }`}
                    >
                      {agent.id === "master" ? (
                        <Cpu size={20} />
                      ) : agent.id === "security" ? (
                        <Shield size={18} />
                      ) : (
                        <Network size={18} />
                      )}
                    </div>

                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="text-xs font-semibold text-[var(--color-ink)]">{agent.name}</h4>
                        <span
                          className={`h-2 w-2 rounded-full ${
                            agent.status === "running"
                              ? "bg-[var(--color-status-running)] animate-ping"
                              : agent.status === "done"
                              ? "bg-[var(--color-status-done)]"
                              : "bg-[var(--color-ink-faint)]"
                          }`}
                        />
                      </div>
                      <p className="mt-0.5 text-[10px] text-[var(--color-ink-muted)] line-clamp-1 max-w-[120px]">
                        {agent.role}
                      </p>
                    </div>
                  </div>
                </div>
              );
            })}

            {/* Canvas Legend */}
            <div className="absolute bottom-3 left-3 flex items-center gap-4 rounded-[var(--radius-md)] border border-[var(--color-border)] bg-[var(--color-surface)]/90 backdrop-blur-xs px-3 py-1.5 text-[11px] text-[var(--color-ink-muted)]">
              <span className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-[var(--color-status-running)]" />
                Inference Active
              </span>
              <span className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-[var(--color-status-done)]" />
                Done
              </span>
              <span className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-[var(--color-ink-faint)]" />
                Idle
              </span>
            </div>
          </div>

          {/* Agent Inspector Side Panel (EPIC-13-T04) */}
          <div className="rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-surface)] p-6 shadow-[var(--shadow-sm)] space-y-6">
            <div className="flex items-start justify-between border-b border-[var(--color-border)] pb-4">
              <div className="flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-[var(--color-primary-tint)] text-[var(--color-primary)]">
                  <Cpu size={24} />
                </div>
                <div>
                  <h3 className="text-base font-bold text-[var(--color-ink)]">{selectedAgent.name}</h3>
                  <p className="text-xs text-[var(--color-ink-muted)]">{selectedAgent.role}</p>
                </div>
              </div>
              <StatusBadge status={selectedAgent.status as Status} />
            </div>

            {/* Current Active Task */}
            <div className="space-y-1.5 rounded-[var(--radius-md)] border border-[var(--color-border-subtle)] bg-[var(--color-surface-sunken)] p-3">
              <span className="text-[10px] font-semibold uppercase tracking-wider text-[var(--color-ink-faint)]">
                Active Execution
              </span>
              <p className="text-xs text-[var(--color-ink)] font-medium leading-relaxed">
                {selectedAgent.currentTask}
              </p>
            </div>

            {/* Telemetry Metrics Grid */}
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="rounded-[var(--radius-md)] border border-[var(--color-border)] p-3 space-y-1">
                <span className="flex items-center gap-1 text-[11px] text-[var(--color-ink-muted)]">
                  <Zap size={12} className="text-[var(--color-primary)]" />
                  Model Tier
                </span>
                <span className="font-semibold text-[var(--color-ink)] capitalize">
                  {selectedAgent.tier.replace("tier_", "")}
                </span>
              </div>

              <div className="rounded-[var(--radius-md)] border border-[var(--color-border)] p-3 space-y-1">
                <span className="flex items-center gap-1 text-[11px] text-[var(--color-ink-muted)]">
                  <Clock size={12} className="text-[var(--color-status-running)]" />
                  Avg Latency
                </span>
                <span className="font-mono font-semibold text-[var(--color-ink)]">
                  {selectedAgent.avgLatencyMs} ms
                </span>
              </div>

              <div className="rounded-[var(--radius-md)] border border-[var(--color-border)] p-3 space-y-1">
                <span className="flex items-center gap-1 text-[11px] text-[var(--color-ink-muted)]">
                  <TrendingUp size={12} className="text-[var(--color-status-done)]" />
                  Tokens Used
                </span>
                <span className="font-mono font-semibold text-[var(--color-ink)]">
                  {selectedAgent.tokensUsed.toLocaleString()}
                </span>
              </div>

              <div className="rounded-[var(--radius-md)] border border-[var(--color-border)] p-3 space-y-1">
                <span className="flex items-center gap-1 text-[11px] text-[var(--color-ink-muted)]">
                  <Shield size={12} className="text-[var(--color-primary)]" />
                  Confidence
                </span>
                <ConfidenceIndicator value={selectedAgent.confidence} />
              </div>
            </div>

            {/* Handoff Trace */}
            <div className="space-y-2">
              <span className="text-[11px] font-semibold text-[var(--color-ink)]">Handoff Pathway</span>
              {selectedAgent.lastHandoffTo ? (
                <div className="flex items-center justify-between rounded-[var(--radius-md)] border border-[var(--color-border)] p-2.5 text-xs">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 size={14} className="text-[var(--color-status-done)]" />
                    <span className="text-[var(--color-ink-muted)]">Dispatches payload to</span>
                  </div>
                  <span className="font-semibold text-[var(--color-primary)] capitalize">
                    {selectedAgent.lastHandoffTo} Agent
                  </span>
                </div>
              ) : (
                <p className="text-xs text-[var(--color-ink-faint)] italic">
                  Leaf worker agent (final consumer of workflow data)
                </p>
              )}
            </div>
          </div>
        </div>
      ) : (
        /* Matrix Grid View */
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {agents.map((agent) => (
            <div
              key={agent.id}
              className="rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-surface)] p-5 transition-shadow hover:shadow-[var(--shadow-sm)] space-y-4"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--color-primary-tint)] text-[var(--color-primary)]">
                    <Cpu size={20} />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-[var(--color-ink)]">{agent.name}</h3>
                    <p className="text-[11px] text-[var(--color-ink-muted)]">{agent.role}</p>
                  </div>
                </div>
                <StatusBadge status={agent.status as Status} />
              </div>

              <p className="text-xs text-[var(--color-ink)] line-clamp-2 bg-[var(--color-surface-sunken)] p-2.5 rounded-[var(--radius-md)]">
                {agent.currentTask}
              </p>

              <div className="flex items-center justify-between text-xs text-[var(--color-ink-muted)] pt-2 border-t border-[var(--color-border-subtle)]">
                <span className="capitalize">{agent.tier.replace("tier_", "")}</span>
                <span className="font-mono">{agent.avgLatencyMs}ms</span>
                <span className="font-mono">{agent.tokensUsed} tokens</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
