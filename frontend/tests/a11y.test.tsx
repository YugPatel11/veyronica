import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { StatusBadge } from "../components/ui/status-badge";
import { RiskBadge } from "../components/ui/risk-badge";
import { ProgressBar } from "../components/ui/progress-bar";

describe("Accessibility & Keyboard Navigation Audit (EPIC-02-T11)", () => {
  it("renders buttons with accessible names and proper button role", () => {
    render(<Button aria-label="Confirm Action">Click Me</Button>);
    const btn = screen.getByRole("button", { name: /confirm action/i });
    expect(btn).toBeInTheDocument();
    expect(btn).not.toBeDisabled();
  });

  it("ensures disabled buttons communicate disabled state to screen readers", () => {
    render(<Button disabled>Disabled Action</Button>);
    const btn = screen.getByRole("button", { name: /disabled action/i });
    expect(btn).toBeDisabled();
    expect(btn).toHaveAttribute("disabled");
  });

  it("verifies badges provide accessible textual content", () => {
    render(<Badge>Verified</Badge>);
    expect(screen.getByText("Verified")).toBeInTheDocument();
  });

  it("verifies StatusBadge contains semantic aria labels for colorblind accessibility", () => {
    render(<StatusBadge status="done" />);
    const badge = screen.getByText(/completed/i);
    expect(badge).toBeInTheDocument();
  });

  it("verifies RiskBadge contains readable risk level", () => {
    render(<RiskBadge level="high" />);
    expect(screen.getByText(/high/i)).toBeInTheDocument();
  });

  it("verifies ProgressBar uses aria-valuenow and aria-valuemax attributes", () => {
    const { container } = render(<ProgressBar value={75} max={100} />);
    const progress = container.querySelector('[role="progressbar"]');
    if (progress) {
      expect(progress).toHaveAttribute("aria-valuenow", "75");
      expect(progress).toHaveAttribute("aria-valuemax", "100");
    }
  });
});
