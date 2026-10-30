"use client";

import { useState } from "react";
import { UserCheck, Eye, Zap } from "lucide-react";

export type AutonomyLevel = "assist" | "supervised" | "autonomous";

interface AutonomyDialProps {
  value?: AutonomyLevel;
  onChange?: (level: AutonomyLevel) => void;
  size?: "sm" | "md";
  className?: string;
  disabled?: boolean;
}

const MODES: Array<{
  id: AutonomyLevel;
  label: string;
  tagline: string;
  icon: typeof Eye;
  activeColor: string;
  activeBg: string;
  borderColor: string;
}> = [
  {
    id: "assist",
    label: "Assist",
    tagline: "Agent suggests drafts; humans execute every step",
    icon: UserCheck,
    activeColor: "var(--color-ink)",
    activeBg: "var(--color-surface-sunken)",
    borderColor: "var(--color-border-strong)",
  },
  {
    id: "supervised",
    label: "Supervised",
    tagline: "Agent executes routine tasks; human dual-approval required for critical mutations",
    icon: Eye,
    activeColor: "var(--color-primary)",
    activeBg: "var(--color-primary-subtle)",
    borderColor: "var(--color-primary)",
  },
  {
    id: "autonomous",
    label: "Autonomous",
    tagline: "Full policy-bounded autonomy with continuous cryptographic ledger auditing",
    icon: Zap,
    activeColor: "var(--color-ai-accent)",
    activeBg: "var(--color-ai-accent-bg)",
    borderColor: "var(--color-ai-accent)",
  },
];

export function AutonomyDial({
  value = "supervised",
  onChange,
  size = "md",
  className = "",
  disabled = false,
}: AutonomyDialProps) {
  const [currentLevel, setCurrentLevel] = useState<AutonomyLevel>(value);

  const activeMode = MODES.find((m) => m.id === currentLevel) ?? MODES[1] ?? {
    id: "supervised" as AutonomyLevel,
    label: "Supervised",
    tagline: "",
    icon: Eye,
    activeColor: "var(--color-primary)",
    activeBg: "var(--color-primary-subtle)",
    borderColor: "var(--color-primary)",
  };

  const handleSelect = (modeId: AutonomyLevel) => {
    if (disabled) return;
    setCurrentLevel(modeId);
    onChange?.(modeId);
  };

  return (
    <div className={`space-y-2 ${className}`}>
      {/* 3-segment switcher */}
      <div
        role="radiogroup"
        aria-label="Autonomy Level Selector"
        className="flex items-center rounded-xl p-1 border transition-all"
        style={{
          backgroundColor: "var(--color-surface-sunken)",
          borderColor: "var(--color-border-subtle)",
        }}
      >
        {MODES.map((mode) => {
          const isSelected = mode.id === currentLevel;
          const Icon = mode.icon;

          return (
            <button
              key={mode.id}
              role="radio"
              aria-checked={isSelected}
              disabled={disabled}
              onClick={() => handleSelect(mode.id)}
              className={`flex-1 flex items-center justify-center gap-2 rounded-lg font-medium transition-all ${
                size === "sm" ? "px-2.5 py-1.5 text-xs" : "px-3.5 py-2 text-sm"
              } ${
                isSelected
                  ? "shadow-sm border font-semibold"
                  : "text-[var(--color-ink-muted)] hover:text-[var(--color-ink)]"
              } ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
              style={{
                backgroundColor: isSelected ? "var(--color-surface)" : "transparent",
                borderColor: isSelected ? mode.borderColor : "transparent",
                color: isSelected ? mode.activeColor : undefined,
              }}
            >
              <Icon
                size={size === "sm" ? 13 : 15}
                className={isSelected ? "animate-pulse" : "opacity-70"}
                style={{ color: isSelected ? mode.activeColor : undefined }}
              />
              <span>{mode.label}</span>
            </button>
          );
        })}
      </div>

      {/* Description caption */}
      <p className="text-xs text-[var(--color-ink-muted)] flex items-center gap-1.5 px-1 leading-relaxed">
        <span
          className="inline-block h-1.5 w-1.5 rounded-full"
          style={{ backgroundColor: activeMode.activeColor }}
        />
        <span>{activeMode.tagline}</span>
      </p>
    </div>
  );
}
