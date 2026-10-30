import { describe, it, expect } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useNexusEvents } from "../lib/useNexusEvents";

describe("useNexusEvents SSE Hook (EPIC-10-T04)", () => {
  it("initializes with disconnected state and empty event list when autoConnect is false", () => {
    const { result } = renderHook(() => useNexusEvents({ autoConnect: false }));

    expect(result.current.events).toEqual([]);
    expect(result.current.latestEvent).toBeNull();
    expect(result.current.isConnected).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it("handles mock event emissions gracefully in demo/offline mode", () => {
    const { result } = renderHook(() => useNexusEvents({ autoConnect: false, runId: "run_test_99" }));

    act(() => {
      result.current.emitMockEvent("workflow.step.completed", { step: "ocr", score: 98 });
    });

    expect(result.current.events.length).toBe(1);
    expect(result.current.latestEvent).not.toBeNull();
    expect(result.current.latestEvent?.type).toBe("workflow.step.completed");
    expect(result.current.latestEvent?.run_id).toBe("run_test_99");
    expect(result.current.latestEvent?.data).toEqual({ step: "ocr", score: 98 });
  });

  it("filters events by runId when specified", () => {
    const { result } = renderHook(() => useNexusEvents({ autoConnect: false, runId: "target_run_1" }));

    act(() => {
      result.current.emitMockEvent("event.match", { value: 1 });
    });

    expect(result.current.events.length).toBe(1);
  });
});
