"use client";

import { useState } from "react";
import { Sheet } from "@/components/ui/sheet";
import { Send, Sparkles, Bot, User, CheckCircle2 } from "lucide-react";

interface CopilotMessage {
  id: string;
  sender: "user" | "copilot";
  content: string;
  timestamp: string;
  plan?: { step: string; status: "done" | "running" | "pending" }[];
}

const INITIAL_MESSAGES: CopilotMessage[] = [
  {
    id: "msg_1",
    sender: "copilot",
    content:
      "Hello! I'm your Nexus Admin Copilot. You can ask me to run queries on student marks, draft communications, check connector health, or inspect audit ledger blocks.",
    timestamp: "Just now",
  },
];

const SUGGESTED_QUERIES = [
  "Show students in Division A failing CS301",
  "Check Campus ERP sync status",
  "Summarize pending approvals count",
  "What was the latest audit ledger block?",
];

interface CopilotSheetProps {
  open: boolean;
  onClose: () => void;
}

/**
 * CopilotSheet — EPIC-12-T04 / EPIC-17-T06
 *
 * Slide-over sheet for the Admin Copilot accessible from every page.
 */
export function CopilotSheet({ open, onClose }: CopilotSheetProps) {
  const [messages, setMessages] = useState<CopilotMessage[]>(INITIAL_MESSAGES);
  const [input, setInput] = useState("");
  const [isThinking, setIsThinking] = useState(false);

  const handleSend = (text?: string) => {
    const query = text || input;
    if (!query.trim() || isThinking) return;

    const userMsg: CopilotMessage = {
      id: `msg_u_${Date.now()}`,
      sender: "user",
      content: query,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsThinking(true);

    // Simulate intelligent copilot response with structured plan
    setTimeout(() => {
      let replyContent = "I've analyzed your request against the live campus database.";
      let plan: CopilotMessage["plan"] = undefined;

      const lower = query.toLowerCase();
      if (lower.includes("division a") || lower.includes("failing") || lower.includes("cs301")) {
        replyContent =
          "Found 2 students in Division A with marks below 40% in CS301:\n• Riya Patel (Roll 101): 32/100\n• Karan Mehta (Roll 102): 38/100\nRecommended next step: trigger a parent notification draft or schedule tutoring via CRM.";
        plan = [
          { step: "Query Campus ERP student marks", status: "done" },
          { step: "Filter Division A & marks < 40", status: "done" },
          { step: "Compile student summary report", status: "done" },
        ];
      } else if (lower.includes("connector") || lower.includes("sync") || lower.includes("erp")) {
        replyContent =
          "All 6 registered enterprise connectors are healthy:\n• Campus ERP (Port 8101): 42ms latency, circuit CLOSED\n• LMS (Port 8102): 35ms latency, circuit CLOSED\n• CRM (Port 8103): 38ms latency, circuit CLOSED\n• SMTP & Telegram: operational";
        plan = [
          { step: "Ping registry health aggregators", status: "done" },
          { step: "Inspect circuit breaker states", status: "done" },
        ];
      } else if (lower.includes("approval")) {
        replyContent =
          "There is currently 1 pending approval:\n• Publish CS301 Marks to Campus ERP (Risk: High, Type: Supervised approval, 47 student records impacted).";
      } else {
        replyContent = `Processed query: "${query}". All parameters verified against policy rules and RBAC permissions.`;
      }

      const copilotMsg: CopilotMessage = {
        id: `msg_c_${Date.now()}`,
        sender: "copilot",
        content: replyContent,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        plan,
      };

      setMessages((prev) => [...prev, copilotMsg]);
      setIsThinking(false);
    }, 600);
  };

  return (
    <Sheet open={open} onClose={onClose} title="Nexus Copilot" width="480px">
      <div className="flex h-[calc(100vh-5rem)] flex-col justify-between">
        {/* Message Thread */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-3 text-sm ${msg.sender === "user" ? "flex-row-reverse" : "flex-row"}`}
            >
              <div
                className={`flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full text-xs ${
                  msg.sender === "user"
                    ? "bg-[var(--color-primary)] text-white"
                    : "bg-[var(--color-surface-sunken)] text-[var(--color-primary)] border border-[var(--color-border)]"
                }`}
              >
                {msg.sender === "user" ? <User size={14} /> : <Bot size={14} />}
              </div>

              <div
                className={`max-w-[82%] rounded-[var(--radius-lg)] p-3 ${
                  msg.sender === "user"
                    ? "bg-[var(--color-primary)] text-white"
                    : "bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-ink)] shadow-[var(--shadow-xs)]"
                }`}
              >
                <p className="whitespace-pre-line text-xs leading-relaxed">{msg.content}</p>

                {msg.plan && (
                  <div className="mt-2.5 rounded-[var(--radius-sm)] border border-[var(--color-border-subtle)] bg-[var(--color-surface-sunken)] p-2 space-y-1.5">
                    <p className="text-[10px] font-semibold uppercase tracking-wider text-[var(--color-ink-faint)]">
                      Execution Steps
                    </p>
                    {msg.plan.map((p, idx) => (
                      <div key={idx} className="flex items-center gap-1.5 text-[11px] text-[var(--color-ink-muted)]">
                        <CheckCircle2 size={12} className="text-[var(--color-status-done)]" />
                        <span>{p.step}</span>
                      </div>
                    ))}
                  </div>
                )}

                <span
                  className={`mt-1.5 block text-[10px] ${
                    msg.sender === "user" ? "text-white/70" : "text-[var(--color-ink-faint)]"
                  }`}
                >
                  {msg.timestamp}
                </span>
              </div>
            </div>
          ))}

          {isThinking && (
            <div className="flex gap-3 text-sm">
              <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-[var(--color-surface-sunken)] text-[var(--color-primary)] border border-[var(--color-border)]">
                <Bot size={14} />
              </div>
              <div className="flex items-center gap-1.5 rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-surface)] px-3 py-2 text-xs text-[var(--color-ink-muted)]">
                <Sparkles size={12} className="animate-spin text-[var(--color-primary)]" />
                <span>Thinking & querying enterprise tools…</span>
              </div>
            </div>
          )}
        </div>

        {/* Suggested Queries */}
        <div className="border-t border-[var(--color-border)] p-3 bg-[var(--color-surface-sunken)]">
          <p className="mb-2 text-[10px] font-semibold uppercase tracking-wider text-[var(--color-ink-faint)]">
            Quick Prompts
          </p>
          <div className="flex flex-wrap gap-1.5">
            {SUGGESTED_QUERIES.map((q, i) => (
              <button
                key={i}
                onClick={() => handleSend(q)}
                className="rounded-full border border-[var(--color-border)] bg-[var(--color-surface)] px-2.5 py-1 text-[11px] text-[var(--color-ink-muted)] transition-colors hover:border-[var(--color-primary)] hover:text-[var(--color-primary)]"
              >
                {q}
              </button>
            ))}
          </div>
        </div>

        {/* Input Bar */}
        <div className="border-t border-[var(--color-border)] p-3 bg-[var(--color-surface)]">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center gap-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask Copilot anything about campus operations..."
              className="flex-1 rounded-[var(--radius-md)] border border-[var(--color-border)] bg-[var(--color-surface-sunken)] px-3 py-2 text-xs text-[var(--color-ink)] placeholder-[var(--color-ink-faint)] outline-none transition-colors focus:border-[var(--color-primary)]"
            />
            <button
              type="submit"
              disabled={!input.trim() || isThinking}
              className="flex h-8 w-8 items-center justify-center rounded-[var(--radius-md)] bg-[var(--color-primary)] text-white transition-opacity disabled:opacity-40 hover:opacity-90"
              aria-label="Send message"
            >
              <Send size={13} />
            </button>
          </form>
          <div className="mt-1 flex items-center justify-between text-[10px] text-[var(--color-ink-faint)]">
            <span>Press Enter to send</span>
            <span>Shortcut: ⌘J</span>
          </div>
        </div>
      </div>
    </Sheet>
  );
}
