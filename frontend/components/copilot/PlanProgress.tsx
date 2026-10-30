"use client";

import React from "react";
import { CheckCircle2, Loader2, Clock, AlertCircle } from "lucide-react";
import { ProgressBar } from "@/components/ui/progress-bar";

export interface PlanStepItem {
  stepId: string;
  title: string;
  description: string;
  status: "pending" | "running" | "completed" | "failed";
}

export interface PlanProgressProps {
  planId: string;
  goal: string;
  steps: PlanStepItem[];
  progressPercentage: number;
}

export function PlanProgress({
  goal,
  steps,
  progressPercentage,
}: PlanProgressProps) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4 space-y-4 backdrop-blur-xs">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h4 className="text-xs font-semibold text-slate-200">Execution Plan</h4>
          <p className="text-[11px] text-slate-400 mt-0.5 truncate max-w-sm">{goal}</p>
        </div>
        <span className="font-mono text-xs font-semibold text-indigo-400">
          {progressPercentage}%
        </span>
      </div>

      <ProgressBar value={progressPercentage} max={100} />

      <div className="space-y-2 pt-1">
        {steps.map((step) => {
          let Icon = Clock;
          let colorClass = "text-slate-500 bg-slate-900 border-slate-700";

          if (step.status === "completed") {
            Icon = CheckCircle2;
            colorClass = "text-emerald-400 bg-emerald-950/40 border-emerald-500/40";
          } else if (step.status === "running") {
            Icon = Loader2;
            colorClass = "text-indigo-400 bg-indigo-950/40 border-indigo-500/40 animate-pulse";
          } else if (step.status === "failed") {
            Icon = AlertCircle;
            colorClass = "text-rose-400 bg-rose-950/40 border-rose-500/40";
          }

          return (
            <div
              key={step.stepId}
              className="flex items-start gap-2.5 rounded-lg border border-slate-800/60 bg-slate-950/40 p-2.5 text-xs"
            >
              <div className={`rounded-full p-1 border mt-0.5 shrink-0 ${colorClass}`}>
                <Icon size={12} className={step.status === "running" ? "animate-spin" : ""} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-medium text-slate-200">{step.title}</div>
                <div className="text-[11px] text-slate-400 mt-0.5 leading-snug">
                  {step.description}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
