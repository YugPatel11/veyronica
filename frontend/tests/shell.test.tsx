import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { Sidebar } from "../components/shell/Sidebar";
import { CommandPalette } from "../components/shell/CommandPalette";
import { Breadcrumbs } from "../components/shell/Breadcrumbs";

describe("Dashboard Shell Components (EPIC-12)", () => {
  it("renders role-aware sidebar with navigation items", () => {
    render(<Sidebar collapsed={false} onToggleCollapse={vi.fn()} userRole="admin" />);
    expect(screen.getByText("Mission Control")).toBeInTheDocument();
    expect(screen.getByText("Agent Map")).toBeInTheDocument();
    expect(screen.getByText("Workflows")).toBeInTheDocument();
    expect(screen.getByText("Approvals")).toBeInTheDocument();
    // Security should be visible for admin role
    expect(screen.getByText("Security")).toBeInTheDocument();
  });

  it("filters out restricted navigation items for faculty/student roles", () => {
    render(<Sidebar collapsed={false} onToggleCollapse={vi.fn()} userRole="student" />);
    expect(screen.getByText("Mission Control")).toBeInTheDocument();
    // Security requires admin/superadmin, so should not be in document
    expect(screen.queryByText("Security")).not.toBeInTheDocument();
  });

  it("renders CommandPalette when open and filters items by search input", () => {
    const handleClose = vi.fn();
    render(<CommandPalette open={true} onClose={handleClose} />);

    const searchInput = screen.getByPlaceholderText(/search pages/i);
    expect(searchInput).toBeInTheDocument();

    fireEvent.change(searchInput, { target: { value: "approvals" } });
    expect(screen.getByText(/approvals/i)).toBeInTheDocument();
  });

  it("renders Breadcrumbs home link", () => {
    render(<Breadcrumbs />);
    expect(screen.getByText("NEXUS")).toBeInTheDocument();
  });
});
