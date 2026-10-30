import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ConfirmationCard } from "../components/copilot/ConfirmationCard";
import { ResponseRenderer } from "../components/copilot/ResponseRenderer";
import { PlanProgress, type PlanStepItem } from "../components/copilot/PlanProgress";

describe("Copilot Frontend Components (EPIC-17)", () => {
  it("renders ConfirmationCard with risk badge and action details", () => {
    const handleConfirm = vi.fn();
    const handleCancel = vi.fn();

    render(
      <ConfirmationCard
        confirmationToken="tok_123"
        actionName="Publish Grades"
        description="Will sync grades to ERP."
        riskLevel="high"
        affectedEntity="CS301-Section-A"
        diffSummary={{ records: 40 }}
        onConfirm={handleConfirm}
        onCancel={handleCancel}
      />
    );

    expect(screen.getByText("Publish Grades")).toBeInTheDocument();
    expect(screen.getByText(/high/i)).toBeInTheDocument();
    expect(screen.getByText("CS301-Section-A")).toBeInTheDocument();

    const confirmBtn = screen.getByRole("button", { name: /confirm & execute/i });
    fireEvent.click(confirmBtn);
    expect(handleConfirm).toHaveBeenCalledWith("tok_123");
  });

  it("renders ResponseRenderer in table format", () => {
    const data = [
      { roll: "CS-01", score: 85 },
      { roll: "CS-02", score: 42 },
    ];
    render(
      <ResponseRenderer
        format="table"
        content="Marks table:"
        data={data}
      />
    );

    expect(screen.getByText("Marks table:")).toBeInTheDocument();
    expect(screen.getByText("CS-01")).toBeInTheDocument();
    expect(screen.getByText("85")).toBeInTheDocument();
  });

  it("renders PlanProgress with stepped execution checklist", () => {
    const steps: PlanStepItem[] = [
      { stepId: "s1", title: "Query DB", description: "Fetch failing students", status: "completed" },
      { stepId: "s2", title: "Process", description: "Analyze trends", status: "running" },
      { stepId: "s3", title: "Notify", description: "Send emails", status: "pending" },
    ];

    render(
      <PlanProgress
        planId="p_001"
        goal="Remedial plan"
        steps={steps}
        progressPercentage={33.3}
      />
    );

    expect(screen.getByText("Execution Plan")).toBeInTheDocument();
    expect(screen.getByText("Query DB")).toBeInTheDocument();
    expect(screen.getByText("33.3%")).toBeInTheDocument();
  });
});
