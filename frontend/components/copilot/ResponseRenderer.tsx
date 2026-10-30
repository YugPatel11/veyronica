"use client";

import React from "react";
import { ChartContainer } from "@/components/ui/chart-theme";

export interface ResponseRendererProps {
  format: "text" | "table" | "chart" | "confirmation";
  content: string;
  data?: Array<Record<string, unknown>>;
  title?: string;
}

export function ResponseRenderer({
  format,
  content,
  data = [],
  title,
}: ResponseRendererProps) {
  const firstRow = data && data.length > 0 ? data[0] : null;

  if (format === "table" && firstRow) {
    const columns = Object.keys(firstRow);

    return (
      <div className="space-y-3">
        {content && <p className="text-xs text-slate-300 leading-relaxed">{content}</p>}
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 overflow-hidden text-xs">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800 bg-slate-950/60 text-slate-400">
                  {columns.map((col) => (
                    <th key={col} className="p-2.5 font-medium uppercase tracking-wider text-[10px]">
                      {col.replace(/_/g, " ")}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {data.map((row, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                    {columns.map((col) => (
                      <td key={col} className="p-2.5 text-slate-200">
                        {String(row[col])}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  }

  if (format === "chart" && firstRow) {
    return (
      <ChartContainer title={title || "Analytics Summary"} subtitle={content}>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 py-2">
          {Object.entries(firstRow).map(([key, val]) => (
            <div key={key} className="rounded-lg border border-slate-800/80 bg-slate-950/40 p-3">
              <div className="text-[10px] uppercase font-mono text-slate-400">
                {key.replace(/_/g, " ")}
              </div>
              <div className="text-lg font-bold font-mono text-slate-100 mt-1">
                {String(val)}
              </div>
            </div>
          ))}
        </div>
      </ChartContainer>
    );
  }

  return (
    <div className="text-xs text-slate-200 leading-relaxed whitespace-pre-wrap">
      {content}
    </div>
  );
}
