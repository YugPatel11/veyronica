"use client";

import React from "react";
import { chartColors, defaultTooltipStyle } from "@/lib/chart-theme";

interface ChartContainerProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  className?: string;
}

export function ChartContainer({
  children,
  title,
  subtitle,
  className = "",
}: ChartContainerProps) {
  return (
    <div
      className={`rounded-xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-md transition-all hover:border-slate-700 ${className}`}
    >
      {(title || subtitle) && (
        <div className="mb-4">
          {title && <h3 className="text-sm font-semibold text-slate-100">{title}</h3>}
          {subtitle && <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>}
        </div>
      )}
      <div className="w-full overflow-hidden">{children}</div>
    </div>
  );
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{ name: string; value: number | string; color?: string }>;
  label?: string;
}

export function CustomChartTooltip({ active, payload, label }: CustomTooltipProps) {
  if (!active || !payload || !payload.length) return null;

  return (
    <div style={defaultTooltipStyle} className="space-y-1">
      {label && <div className="font-semibold text-slate-200 border-b border-slate-700/60 pb-1 mb-1">{label}</div>}
      {payload.map((entry, idx) => (
        <div key={idx} className="flex items-center justify-between gap-4 text-xs">
          <span className="flex items-center gap-1.5">
            <span
              className="inline-block h-2 w-2 rounded-full"
              style={{ backgroundColor: entry.color || chartColors.primary }}
            />
            <span className="text-slate-300">{entry.name}</span>
          </span>
          <span className="font-mono font-medium text-slate-100">{entry.value}</span>
        </div>
      ))}
    </div>
  );
}
