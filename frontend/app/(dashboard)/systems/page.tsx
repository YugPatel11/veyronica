"use client";

import {
  Plug,
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  XCircle,
} from "lucide-react";
import { ProgressBar } from "@/components/ui/progress-bar";
import { useState } from "react";

/**
 * Connected Systems — EPIC-13-T07
 *
 * Connector health grid with status, latency, circuit state, and uptime.
 */

interface Connector {
  id: string;
  name: string;
  type: string;
  baseUrl: string;
  status: "healthy" | "degraded" | "down";
  circuit: "closed" | "open" | "half_open";
  latency: number;
  uptime: number;
  callsToday: number;
  errorsToday: number;
  lastChecked: string;
}

const CONNECTORS: Connector[] = [
  { id: "campus-erp", name: "Campus ERP", type: "ERP", baseUrl: "http://erp:8001", status: "healthy", circuit: "closed", latency: 42, uptime: 99.9, callsToday: 234, errorsToday: 0, lastChecked: "30s ago" },
  { id: "lms", name: "Learning Management System", type: "LMS", baseUrl: "http://lms:8002", status: "healthy", circuit: "closed", latency: 38, uptime: 99.7, callsToday: 89, errorsToday: 1, lastChecked: "30s ago" },
  { id: "student-crm", name: "Student CRM", type: "CRM", baseUrl: "http://crm:8003", status: "degraded", circuit: "half_open", latency: 210, uptime: 94.2, callsToday: 56, errorsToday: 12, lastChecked: "30s ago" },
  { id: "email-smtp", name: "Email (SMTP + Resend)", type: "Email", baseUrl: "smtp://mailpit:1025", status: "healthy", circuit: "closed", latency: 120, uptime: 99.8, callsToday: 45, errorsToday: 0, lastChecked: "30s ago" },
  { id: "object-storage", name: "Object Storage (MinIO)", type: "Storage", baseUrl: "http://minio:9000", status: "healthy", circuit: "closed", latency: 18, uptime: 100, callsToday: 67, errorsToday: 0, lastChecked: "30s ago" },
  { id: "telegram", name: "Telegram Bot", type: "Messaging", baseUrl: "https://api.telegram.org", status: "down", circuit: "open", latency: 0, uptime: 78.4, callsToday: 3, errorsToday: 3, lastChecked: "30s ago" },
];

const statusStyle = {
  healthy: { icon: CheckCircle2, color: "text-[var(--color-status-done)]", bg: "bg-[var(--color-status-done-bg)]", label: "Healthy" },
  degraded: { icon: AlertTriangle, color: "text-[var(--color-saffron-dark)]", bg: "bg-[var(--color-status-waiting-bg)]", label: "Degraded" },
  down: { icon: XCircle, color: "text-[var(--color-status-failed)]", bg: "bg-[var(--color-status-failed-bg)]", label: "Down" },
};

export default function SystemsPage() {
  const [refreshing, setRefreshing] = useState(false);

  const healthyCt = CONNECTORS.filter((c) => c.status === "healthy").length;
  const totalCt = CONNECTORS.length;

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="font-heading text-2xl font-bold text-[var(--color-ink)]">Connected Systems</h1>
          <p className="mt-1 text-sm text-[var(--color-ink-muted)]">
            {healthyCt}/{totalCt} systems healthy
          </p>
        </div>
        <button
          onClick={() => { setRefreshing(true); setTimeout(() => setRefreshing(false), 1000); }}
          className="flex items-center gap-2 rounded-[var(--radius-md)] border px-3 py-1.5 text-sm font-medium text-[var(--color-ink-muted)] transition-colors hover:text-[var(--color-ink)]"
          style={{ borderColor: "var(--color-border)" }}
        >
          <RefreshCw size={14} className={refreshing ? "animate-spin" : ""} />
          Check All
        </button>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
        {CONNECTORS.map((c) => {
          const s = statusStyle[c.status];
          const Icon = s.icon;
          return (
            <div
              key={c.id}
              className="rounded-[var(--radius-lg)] border bg-[var(--color-surface)] p-5 transition-shadow hover:shadow-[var(--shadow-sm)]"
              style={{ borderColor: "var(--color-border-subtle)" }}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-[var(--radius-md)] bg-[var(--color-surface-sunken)]">
                    <Plug size={20} className="text-[var(--color-ink-muted)]" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-[var(--color-ink)]">{c.name}</h3>
                    <p className="text-[11px] text-[var(--color-ink-faint)]">{c.type}</p>
                  </div>
                </div>
                <span className={`flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium ${s.bg} ${s.color}`}>
                  <Icon size={10} />
                  {s.label}
                </span>
              </div>

              <div className="mt-4 grid grid-cols-2 gap-3">
                <div>
                  <p className="text-[11px] text-[var(--color-ink-faint)]">Latency</p>
                  <p className="font-mono text-sm font-medium text-[var(--color-ink)]">{c.latency > 0 ? `${c.latency}ms` : "—"}</p>
                </div>
                <div>
                  <p className="text-[11px] text-[var(--color-ink-faint)]">Circuit</p>
                  <p className="text-sm font-medium text-[var(--color-ink)]">{c.circuit.replace("_", "-")}</p>
                </div>
                <div>
                  <p className="text-[11px] text-[var(--color-ink-faint)]">Calls Today</p>
                  <p className="font-mono text-sm font-medium text-[var(--color-ink)]">{c.callsToday}</p>
                </div>
                <div>
                  <p className="text-[11px] text-[var(--color-ink-faint)]">Errors</p>
                  <p className={`font-mono text-sm font-medium ${c.errorsToday > 0 ? "text-[var(--color-status-failed)]" : "text-[var(--color-ink)]"}`}>{c.errorsToday}</p>
                </div>
              </div>

              <div className="mt-4">
                <ProgressBar
                  value={c.uptime}
                  max={100}
                  label="Uptime"
                  showValue
                  size="sm"
                  color={c.uptime > 99 ? "success" : c.uptime > 90 ? "warning" : "danger"}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
