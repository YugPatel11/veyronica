"use client";

import { Shield, AlertTriangle, Lock, Eye, Activity } from "lucide-react";
import { StatCard } from "@/components/ui/stat-card";
import { StatusBadge } from "@/components/ui/status-badge";

/**
 * Security Center — EPIC-18
 */

const incidents = [
  { id: "sec_001", type: "Brute Force", target: "admin@nexus.edu", status: "resolved" as const, time: "1h ago", severity: "high" },
  { id: "sec_002", type: "Unusual Login", target: "faculty@nexus.edu", status: "monitoring" as const, time: "3h ago", severity: "medium" },
  { id: "sec_003", type: "Rate Limit Hit", target: "API /auth/login", status: "resolved" as const, time: "5h ago", severity: "low" },
];

const statusMap = { resolved: "done" as const, monitoring: "running" as const, active: "failed" as const };

export default function SecurityPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-heading text-2xl font-bold text-[var(--color-ink)]">Security Center</h1>
        <p className="mt-1 text-sm text-[var(--color-ink-muted)]">Incident monitoring and access control</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Active Incidents" value="0" trend="neutral" icon={AlertTriangle} />
        <StatCard label="Blocked Entities" value="2" delta="1 IP, 1 user" trend="neutral" icon={Lock} />
        <StatCard label="Login Attempts (24h)" value="47" delta="3 failed" trend="neutral" icon={Eye} />
        <StatCard label="Avg Response Time" value="< 2s" trend="up" icon={Activity} />
      </div>

      <div className="rounded-[var(--radius-lg)] border bg-[var(--color-surface)]" style={{ borderColor: "var(--color-border-subtle)" }}>
        <div className="border-b px-5 py-4" style={{ borderColor: "var(--color-border-subtle)" }}>
          <h2 className="font-heading text-base font-semibold text-[var(--color-ink)]">Recent Incidents</h2>
        </div>
        <div className="divide-y" style={{ borderColor: "var(--color-border-subtle)" }}>
          {incidents.map((inc) => (
            <div key={inc.id} className="flex items-center justify-between px-5 py-3.5 transition-colors hover:bg-[var(--color-surface-sunken)]">
              <div className="flex items-center gap-3">
                <Shield size={16} className="text-[var(--color-ink-muted)]" />
                <div>
                  <p className="text-sm font-medium text-[var(--color-ink)]">{inc.type}</p>
                  <p className="text-[11px] text-[var(--color-ink-faint)]">{inc.target} · {inc.time}</p>
                </div>
              </div>
              <StatusBadge status={statusMap[inc.status]} label={inc.status.charAt(0).toUpperCase() + inc.status.slice(1)} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
