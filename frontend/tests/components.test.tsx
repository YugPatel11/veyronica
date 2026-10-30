import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/ui/status-badge";
import { Breadcrumbs } from "@/components/shell/Breadcrumbs";
import { PlanProgress } from "@/components/copilot/PlanProgress";
import { ResponseRenderer } from "@/components/copilot/ResponseRenderer";

describe("Design System & Component Library (TEST-02)", () => {
  it("renders buttons with different variants", () => {
    const { rerender } = render(<Button variant="primary">Primary Action</Button>);
    expect(screen.getByText("Primary Action")).toBeDefined();

    rerender(<Button variant="danger">Delete Record</Button>);
    expect(screen.getByText("Delete Record")).toBeDefined();

    rerender(<Button variant="outline" size="sm">Small Outline</Button>);
    expect(screen.getByText("Small Outline")).toBeDefined();
  });

  it("renders StatusBadge with animated glow and labels", () => {
    const { rerender } = render(<StatusBadge status="done" />);
    expect(screen.getByText(/completed/i)).toBeDefined();

    rerender(<StatusBadge status="failed" />);
    expect(screen.getByText(/failed/i)).toBeDefined();

    rerender(<StatusBadge status="waiting" />);
    expect(screen.getByText(/waiting/i)).toBeDefined();
  });

  it("renders Breadcrumbs with root branding", () => {
    render(<Breadcrumbs />);
    expect(screen.getByText("NEXUS")).toBeDefined();
  });

  it("renders PlanProgress with active and completed steps", () => {
    const steps = [
      { stepId: "s1", title: "Extract answers", description: "OCR scan", status: "completed" as const },
      { stepId: "s2", title: "Rubric evaluation", description: "Evaluate concepts", status: "running" as const },
      { stepId: "s3", title: "Sync ERP", description: "Push marks", status: "pending" as const },
    ];
    render(
      <PlanProgress
        planId="plan_123"
        goal="Exam Marking Plan"
        steps={steps}
        progressPercentage={33}
      />
    );
    expect(screen.getByText("Execution Plan")).toBeDefined();
    expect(screen.getByText("Exam Marking Plan")).toBeDefined();
    expect(screen.getByText("Extract answers")).toBeDefined();
    expect(screen.getByText("Rubric evaluation")).toBeDefined();
    expect(screen.getByText("Sync ERP")).toBeDefined();
    expect(screen.getByText("33%")).toBeDefined();
  });

  it("renders ResponseRenderer in text and table formats", () => {
    const tableData = [
      { subject: "Algorithms", students: 45, pass_rate: "95%" },
      { subject: "Database Systems", students: 50, pass_rate: "88%" },
    ];
    render(
      <ResponseRenderer
        format="table"
        content="Subject performance summary"
        data={tableData}
      />
    );
    expect(screen.getByText("Subject performance summary")).toBeDefined();
    expect(screen.getByText("Algorithms")).toBeDefined();
    expect(screen.getByText("Database Systems")).toBeDefined();
  });
});
