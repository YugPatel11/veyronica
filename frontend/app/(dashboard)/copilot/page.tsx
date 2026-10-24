"use client";

import { MessageSquare, Send, Zap } from "lucide-react";
import { useState } from "react";

/**
 * Copilot — EPIC-17-T06
 *
 * Chat UI for Admin Copilot agent.
 */
export default function CopilotPage() {
  const [input, setInput] = useState("");

  return (
    <div className="flex h-[calc(100vh-10rem)] flex-col">
      <div>
        <h1 className="font-heading text-2xl font-bold text-[var(--color-ink)]">Copilot</h1>
        <p className="mt-1 text-sm text-[var(--color-ink-muted)]">Ask anything about your campus data</p>
      </div>

      {/* Chat area */}
      <div className="mt-6 flex-1 overflow-y-auto rounded-[var(--radius-lg)] border bg-[var(--color-surface)] p-6" style={{ borderColor: "var(--color-border-subtle)" }}>
        <div className="flex flex-col items-center justify-center h-full text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-[var(--color-ai-accent-bg)]">
            <Zap size={24} className="text-[var(--color-ai-accent)]" />
          </div>
          <h2 className="mt-4 font-heading text-lg font-semibold text-[var(--color-ink)]">NEXUS Copilot</h2>
          <p className="mt-2 max-w-md text-sm text-[var(--color-ink-muted)]">
            Ask questions about students, marks, attendance, or request operations like &quot;show me students below 40% in CS301&quot;
          </p>
          <div className="mt-6 flex flex-wrap justify-center gap-2">
            {["Show pass/fail ratio CS301", "Students below threshold", "Compare exam averages", "Today's pending approvals"].map((q) => (
              <button
                key={q}
                onClick={() => setInput(q)}
                className="rounded-full border px-3 py-1.5 text-xs text-[var(--color-ink-muted)] transition-colors hover:bg-[var(--color-surface-sunken)] hover:text-[var(--color-ink)]"
                style={{ borderColor: "var(--color-border)" }}
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Input */}
      <div className="mt-3 flex items-center gap-3 rounded-[var(--radius-lg)] border bg-[var(--color-surface)] px-4 py-3" style={{ borderColor: "var(--color-border)" }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask the Copilot…"
          className="flex-1 bg-transparent text-sm text-[var(--color-ink)] placeholder:text-[var(--color-ink-disabled)] outline-none"
        />
        <button
          className="flex h-8 w-8 items-center justify-center rounded-[var(--radius-md)] text-white transition-opacity disabled:opacity-40"
          style={{ backgroundColor: "var(--color-primary)" }}
          disabled={!input.trim()}
        >
          <Send size={14} />
        </button>
      </div>
    </div>
  );
}
