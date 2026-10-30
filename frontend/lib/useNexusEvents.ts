"use client";

import { useEffect, useRef, useState, useCallback } from "react";

export interface NexusEventPayload {
  id: string;
  type: string;
  run_id?: string | null;
  task_id?: string | null;
  agent_id?: string | null;
  data: Record<string, unknown>;
  timestamp: string;
}

interface UseNexusEventsOptions {
  runId?: string;
  eventType?: string;
  autoConnect?: boolean;
}

/**
 * useNexusEvents — EPIC-10-T04
 *
 * Real-time SSE hook for connecting to the event stream with auto-reconnect,
 * event filtering, and graceful in-memory simulation when offline.
 */
export function useNexusEvents({
  runId,
  eventType,
  autoConnect = true,
}: UseNexusEventsOptions = {}) {
  const [events, setEvents] = useState<NexusEventPayload[]>([]);
  const [latestEvent, setLatestEvent] = useState<NexusEventPayload | null>(null);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const retryCountRef = useRef<number>(0);

  const handleEvent = useCallback(
    (event: NexusEventPayload) => {
      // Filter by runId if requested
      if (runId && event.run_id && event.run_id !== runId) return;
      // Filter by eventType if requested
      if (eventType && event.type !== eventType) return;

      setLatestEvent(event);
      setEvents((prev) => [event, ...prev.slice(0, 99)]);
    },
    [runId, eventType]
  );

  const connect = useCallback(() => {
    if (typeof window === "undefined") return;

    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const token = sessionStorage.getItem("nexus_access_token") || "";
    const params = new URLSearchParams();
    if (runId) params.append("run_id", runId);
    if (eventType) params.append("event_type", eventType);
    if (token) params.append("token", token);

    const streamUrl = `${apiUrl}/api/v1/events/stream?${params.toString()}`;

    try {
      const es = new EventSource(streamUrl, { withCredentials: false });
      eventSourceRef.current = es;

      es.onopen = () => {
        setIsConnected(true);
        setError(null);
        retryCountRef.current = 0;
      };

      es.onmessage = (e) => {
        try {
          const parsed = JSON.parse(e.data) as NexusEventPayload;
          handleEvent(parsed);
        } catch {
          // ignore non-json keepalive comments
        }
      };

      es.onerror = () => {
        setIsConnected(false);
        es.close();

        // Exponential backoff reconnect
        const wait = Math.min(1000 * Math.pow(2, retryCountRef.current), 15000);
        retryCountRef.current += 1;
        setError(`Disconnected. Retrying in ${Math.round(wait / 1000)}s...`);

        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, wait);
      };
    } catch (err) {
      setIsConnected(false);
      setError(err instanceof Error ? err.message : "Failed to open event stream");
    }
  }, [runId, eventType, handleEvent]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setIsConnected(false);
  }, []);

  // In-memory simulation fallback for local testing / demo mode
  const emitMockEvent = useCallback(
    (type: string, data: Record<string, unknown> = {}) => {
      const mock: NexusEventPayload = {
        id: `mock_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`,
        type,
        run_id: runId || "run_demo_001",
        data,
        timestamp: new Date().toISOString(),
      };
      handleEvent(mock);
    },
    [runId, handleEvent]
  );

  useEffect(() => {
    if (autoConnect) {
      connect();
    }
    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  return {
    events,
    latestEvent,
    isConnected,
    error,
    connect,
    disconnect,
    emitMockEvent,
  };
}
