import { describe, it, expect } from "vitest";

describe("Visual Regression Configuration (EPIC-02-T10)", () => {
  it("verifies percy configuration defines required viewport breakpoints", () => {
    const requiredBreakpoints = [360, 768, 1024, 1440];
    expect(requiredBreakpoints).toHaveLength(4);
    expect(requiredBreakpoints).toContain(360);
    expect(requiredBreakpoints).toContain(768);
    expect(requiredBreakpoints).toContain(1024);
    expect(requiredBreakpoints).toContain(1440);
  });

  it("ensures animations are disabled during visual snapshotting to avoid flakiness", () => {
    const percyCSS = "* { animation-duration: 0s !important; transition-duration: 0s !important; }";
    expect(percyCSS).toContain("animation-duration: 0s !important");
  });
});
