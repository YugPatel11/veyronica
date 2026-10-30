"use client";

import React, { useState } from "react";
import { Check, X, ShieldAlert } from "lucide-react";
import { RiskBadge } from "@/components/ui/risk-badge";
import { Button } from "@/components/ui/button";

export interface ConfirmationCardProps {
  confirmationToken: string;
  actionName: string;
  description: string;
  riskLevel: "low" | "medium" | "high" | "critical";
  affectedEntity: string;
  diffSummary?: Record<string, string | number>;
  onConfirm: (token: string) => void;
  onCancel: (token: string) => void;
}

export function ConfirmationCard({
  confirmationToken,
  actionName,
  description,
  riskLevel,
  affectedEntity,
  diffSummary = {},
  onConfirm,
  onCancel,
}: ConfirmationCardProps) {
  const [status, setStatus] = useState<"idle" | "confirmed" | "cancelled">("idle");

  const handleConfirm = () => {
    setStatus("confirmed");
    onConfirm(confirmationToken);
  };

  const handleCancel = () => {
    setStatus("cancelled");
    onCancel(confirmationToken);
  };

  if (status === "confirmed") {
    return (
      <div className="rounded-xl border border-emerald-500/30 bg-emerald-950/20 p-4 text-xs text-emerald-300 flex items-center gap-2">
        <Check size={16} className="text-emerald-400" />
        <span>Action <strong>{actionName}</strong> was confirmed and submitted for execution.</span>
      </div>
    );
  }

  if (status === "cancelled") {
    return (
      <div className="rounded-xl border border-slate-700 bg-slate-900/40 p-4 text-xs text-slate-400 flex items-center gap-2">
        <X size={16} />
        <span>Action was cancelled. No state changes were applied.</span>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-amber-500/30 bg-amber-950/20 p-5 shadow-lg backdrop-blur-sm space-y-4">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2">
          <ShieldAlert className="text-amber-400 h-5 w-5 shrink-0" />
          <h4 className="font-semibold text-sm text-slate-100">{actionName}</h4>
        </div>
        <RiskBadge level={riskLevel} />
      </div>

      <p className="text-xs text-slate-300 leading-relaxed">{description}</p>

      <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-3 text-xs space-y-1.5 font-mono">
        <div className="text-slate-400">
          Target: <span className="text-slate-200">{affectedEntity}</span>
        </div>
        {Object.entries(diffSummary).map(([key, val]) => (
          <div key={key} className="flex justify-between text-slate-400">
            <span>{key}:</span>
            <span className="text-amber-300">{val}</span>
          </div>
        ))}
      </div>

      <div className="flex items-center justify-end gap-2 pt-1">
        <Button
          size="sm"
          variant="outline"
          onClick={handleCancel}
          className="text-xs h-8"
        >
          <X size={14} className="mr-1" />
          Cancel
        </Button>
        <Button
          size="sm"
          variant="primary"
          onClick={handleConfirm}
          className="text-xs h-8 bg-amber-600 hover:bg-amber-500 text-white"
        >
          <Check size={14} className="mr-1" />
          Confirm & Execute
        </Button>
      </div>
    </div>
  );
}
