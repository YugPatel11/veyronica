import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import LoginPage from "@/app/page";

// Mock next/navigation
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
  usePathname: () => "/",
}));

describe("LoginPage", () => {
  it("renders the NEXUS wordmark", () => {
    render(<LoginPage />);
    expect(screen.getByText("NEXUS")).toBeInTheDocument();
  });

  it("renders email and password inputs", () => {
    render(<LoginPage />);
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
    expect(screen.getByLabelText("Password")).toBeInTheDocument();
  });

  it("renders the sign in button", () => {
    render(<LoginPage />);
    expect(screen.getByRole("button", { name: "Sign in" })).toBeInTheDocument();
  });

  it("has the forgot password link", () => {
    render(<LoginPage />);
    expect(screen.getByText("Forgot password?")).toBeInTheDocument();
  });

  it("shows password toggle button", () => {
    render(<LoginPage />);
    expect(
      screen.getByRole("button", { name: "Show password" })
    ).toBeInTheDocument();
  });

  it("has version text", () => {
    render(<LoginPage />);
    expect(screen.getByText(/v0\.1\.0/)).toBeInTheDocument();
  });
});
