"use client";

import { useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  Calendar,
  CheckCircle2,
  Sparkles,
  Send,
  Building2,
  Users,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";

/**
 * Timetable Generation & Faculty Grid — EPIC-26-T05
 *
 * Interactive visual weekly schedule matrix, constraint clash alerts,
 * and dual-approval publishing.
 */

interface TimetableSlotItem {
  id: string;
  day: "Monday" | "Tuesday" | "Wednesday" | "Thursday" | "Friday";
  period: number; // 1 to 5
  time: string;
  courseCode: string;
  courseName: string;
  faculty: string;
  division: string;
  room: string;
  isConflict?: boolean;
}

const INITIAL_SCHEDULE: TimetableSlotItem[] = [
  {
    id: "slot_1",
    day: "Monday",
    period: 1,
    time: "09:00 – 10:15",
    courseCode: "CS301",
    courseName: "Database Systems",
    faculty: "Prof. Priya Sharma",
    division: "Div-A (CSE)",
    room: "LH-101",
  },
  {
    id: "slot_2",
    day: "Monday",
    period: 3,
    time: "11:30 – 12:45",
    courseCode: "CS201",
    courseName: "Data Structures",
    faculty: "Prof. Arjun Kapoor",
    division: "Div-A (CSE)",
    room: "LH-102",
  },
  {
    id: "slot_3",
    day: "Tuesday",
    period: 2,
    time: "10:15 – 11:30",
    courseCode: "PHY101",
    courseName: "Engineering Physics",
    faculty: "Dr. Sneha Nair",
    division: "Div-B (ECE)",
    room: "LAB-201",
  },
  {
    id: "slot_4",
    day: "Wednesday",
    period: 1,
    time: "09:00 – 10:15",
    courseCode: "CS301",
    courseName: "Database Systems Lab",
    faculty: "Prof. Priya Sharma",
    division: "Div-A (CSE)",
    room: "LAB-201",
  },
  {
    id: "slot_5",
    day: "Thursday",
    period: 4,
    time: "01:45 – 03:00",
    courseCode: "MA201",
    courseName: "Discrete Mathematics",
    faculty: "Dr. Rohan Verma",
    division: "Div-B (ECE)",
    room: "LH-101",
  },
  {
    id: "slot_6",
    day: "Friday",
    period: 2,
    time: "10:15 – 11:30",
    courseCode: "CS301",
    courseName: "Database Systems",
    faculty: "Prof. Priya Sharma",
    division: "Div-A (CSE)",
    room: "LH-101",
  },
];

const DAYS: Array<"Monday" | "Tuesday" | "Wednesday" | "Thursday" | "Friday"> = [
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
];

const PERIOD_TIMES = [
  { period: 1, label: "Period 1 (09:00 – 10:15)" },
  { period: 2, label: "Period 2 (10:15 – 11:30)" },
  { period: 3, label: "Period 3 (11:30 – 12:45)" },
  { period: 4, label: "Period 4 (01:45 – 03:00)" },
  { period: 5, label: "Period 5 (03:00 – 04:15)" },
];

export default function TimetablePage() {
  const [schedule, setSchedule] = useState<TimetableSlotItem[]>(INITIAL_SCHEDULE);
  const [isSolving, setIsSolving] = useState(false);
  const [approvalRequested, setApprovalRequested] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState<TimetableSlotItem | null>(null);

  const handleSolve = () => {
    setIsSolving(true);
    setTimeout(() => {
      setIsSolving(false);
      // Simulated conflict-free schedule update
      setSchedule((prev) => [
        ...prev,
        {
          id: "slot_auto_" + Math.random().toString(36).substring(2, 6),
          day: "Wednesday",
          period: 3,
          time: "11:30 – 12:45",
          courseCode: "AI101",
          courseName: "Intro to Neural Systems",
          faculty: "Dr. Vikram Joshi",
          division: "Div-A (CSE)",
          room: "LH-102",
        },
      ]);
    }, 1200);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* ── Header ────────────────────────────────────────────────────────── */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <Link
            href="/workflows"
            className="flex h-9 w-9 items-center justify-center rounded-lg border transition-colors hover:bg-[var(--color-surface-sunken)]"
            style={{
              borderColor: "var(--color-border)",
              color: "var(--color-ink)",
            }}
          >
            <ArrowLeft size={16} />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-heading text-xl font-bold text-[var(--color-ink)]">
                Timetable Generation & Faculty Matrix
              </h1>
              <Badge variant="outline" className="text-xs">
                WF5 Solver
              </Badge>
            </div>
            <p className="mt-0.5 text-xs text-[var(--color-ink-muted)]">
              Automated conflict-free scheduling under room capacity and faculty availability constraints
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleSolve}
            disabled={isSolving}
            className="flex items-center gap-2 rounded-xl border px-3.5 py-2 text-xs font-semibold text-[var(--color-ink)] hover:bg-[var(--color-surface-sunken)] transition-colors cursor-pointer"
            style={{ borderColor: "var(--color-border)" }}
          >
            <Sparkles size={14} className={isSolving ? "animate-spin" : "text-[var(--color-ai-accent)]"} />
            <span>{isSolving ? "Solving Constraints…" : "Auto-Solve Timetable"}</span>
          </button>

          <button
            onClick={() => setApprovalRequested(true)}
            className="flex items-center gap-2 rounded-xl px-4 py-2 text-xs font-semibold text-white shadow-sm transition-all hover:opacity-95 active:scale-95 cursor-pointer"
            style={{ backgroundColor: "var(--color-primary)" }}
          >
            <Send size={14} />
            <span>Publish via Approval Policy</span>
          </button>
        </div>
      </div>

      {/* ── Banner: Approval Dispatched ────────────────────────────────────── */}
      {approvalRequested && (
        <div
          className="flex items-center justify-between rounded-xl p-4 border transition-all animate-fadeIn"
          style={{
            backgroundColor: "var(--color-status-done-bg)",
            borderColor: "var(--color-status-done-border)",
          }}
        >
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[var(--color-status-done)] text-white">
              <CheckCircle2 size={16} />
            </div>
            <div>
              <p className="text-sm font-medium text-[var(--color-ink)]">
                Timetable schedule submitted to Policy Engine! Dual-Approval request #appr_tt_01 generated.
              </p>
              <p className="text-xs text-[var(--color-ink-muted)]">
                Requires authorization from Academic Dean and Department Heads prior to student release.
              </p>
            </div>
          </div>
          <Link
            href="/approvals"
            className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold text-white"
            style={{ backgroundColor: "var(--color-status-done)" }}
          >
            <span>View Approval Inbox</span>
          </Link>
        </div>
      )}

      {/* ── Metric Strip ──────────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="rounded-xl border bg-[var(--color-surface)] p-4" style={{ borderColor: "var(--color-border-subtle)" }}>
          <div className="flex items-center gap-2 text-[var(--color-primary)]">
            <Calendar size={16} />
            <span className="text-xs font-medium uppercase tracking-wider text-[var(--color-ink-faint)]">
              Scheduled Sessions
            </span>
          </div>
          <p className="mt-2 text-2xl font-bold font-heading text-[var(--color-ink)]">
            {schedule.length} Slots
          </p>
          <p className="mt-1 text-xs text-[var(--color-status-done)]">100% capacity assigned</p>
        </div>

        <div className="rounded-xl border bg-[var(--color-surface)] p-4" style={{ borderColor: "var(--color-border-subtle)" }}>
          <div className="flex items-center gap-2 text-[var(--color-status-done)]">
            <CheckCircle2 size={16} />
            <span className="text-xs font-medium uppercase tracking-wider text-[var(--color-ink-faint)]">
              Clash Detection
            </span>
          </div>
          <p className="mt-2 text-2xl font-bold font-heading text-[var(--color-status-done)]">
            0 Conflicts
          </p>
          <p className="mt-1 text-xs text-[var(--color-ink-muted)]">Room and faculty validated</p>
        </div>

        <div className="rounded-xl border bg-[var(--color-surface)] p-4" style={{ borderColor: "var(--color-border-subtle)" }}>
          <div className="flex items-center gap-2 text-[var(--color-ai-accent)]">
            <Building2 size={16} />
            <span className="text-xs font-medium uppercase tracking-wider text-[var(--color-ink-faint)]">
              Room Utilization
            </span>
          </div>
          <p className="mt-2 text-2xl font-bold font-heading text-[var(--color-ink)]">
            84.5%
          </p>
          <p className="mt-1 text-xs text-[var(--color-ink-muted)]">Peak utilization: 10:15 – 12:45</p>
        </div>

        <div className="rounded-xl border bg-[var(--color-surface)] p-4" style={{ borderColor: "var(--color-border-subtle)" }}>
          <div className="flex items-center gap-2 text-[var(--color-ink)]">
            <Users size={16} />
            <span className="text-xs font-medium uppercase tracking-wider text-[var(--color-ink-faint)]">
              Faculty Workload
            </span>
          </div>
          <p className="mt-2 text-2xl font-bold font-heading text-[var(--color-ink)]">
            Balanced
          </p>
          <p className="mt-1 text-xs text-[var(--color-ink-muted)]">Max 3 periods/day per professor</p>
        </div>
      </div>

      {/* ── Main Timetable Matrix Grid (Monday–Friday) ─────────────────────── */}
      <div
        className="rounded-2xl border bg-[var(--color-surface)] shadow-sm overflow-hidden"
        style={{ borderColor: "var(--color-border-subtle)" }}
      >
        <div className="border-b px-6 py-4 flex items-center justify-between" style={{ borderColor: "var(--color-border-subtle)" }}>
          <div>
            <h2 className="font-heading text-base font-semibold text-[var(--color-ink)]">
              Weekly Schedule Grid
            </h2>
            <p className="text-xs text-[var(--color-ink-muted)] mt-0.5">
              Click any schedule slot to inspect room capacity, enrolled division, and faculty assignment
            </p>
          </div>
          <span className="font-mono text-xs text-[var(--color-ink-faint)]">
            Term: Fall 2026
          </span>
        </div>

        <div className="overflow-x-auto">
          <div className="min-w-[800px]">
            {/* Days Header */}
            <div
              className="grid grid-cols-6 border-b text-xs font-semibold uppercase tracking-wider text-[var(--color-ink-faint)] bg-[var(--color-surface-sunken)]"
              style={{ borderColor: "var(--color-border-subtle)" }}
            >
              <div className="p-3 text-center border-r" style={{ borderColor: "var(--color-border-subtle)" }}>
                Time Slot
              </div>
              {DAYS.map((d) => (
                <div key={d} className="p-3 text-center border-r last:border-r-0" style={{ borderColor: "var(--color-border-subtle)" }}>
                  {d}
                </div>
              ))}
            </div>

            {/* Period Rows */}
            {PERIOD_TIMES.map((pt) => (
              <div
                key={pt.period}
                className="grid grid-cols-6 border-b last:border-b-0 min-h-[96px]"
                style={{ borderColor: "var(--color-border-subtle)" }}
              >
                {/* Period Label */}
                <div
                  className="p-3 border-r flex flex-col justify-center items-center text-center bg-[var(--color-surface-sunken)]"
                  style={{ borderColor: "var(--color-border-subtle)" }}
                >
                  <span className="font-mono text-xs font-bold text-[var(--color-ink)]">
                    Period {pt.period}
                  </span>
                  <span className="text-[10px] text-[var(--color-ink-faint)] mt-1">
                    {pt.label.split("(")[1]?.replace(")", "")}
                  </span>
                </div>

                {/* Day Columns */}
                {DAYS.map((day) => {
                  const match = schedule.find((s) => s.day === day && s.period === pt.period);

                  return (
                    <div
                      key={day + pt.period}
                      className="p-2 border-r last:border-r-0 transition-colors hover:bg-[var(--color-surface-sunken)] relative"
                      style={{ borderColor: "var(--color-border-subtle)" }}
                    >
                      {match ? (
                        <div
                          onClick={() => setSelectedSlot(match)}
                          className="h-full rounded-xl border p-2.5 bg-[var(--color-surface)] shadow-xs hover:border-[var(--color-primary)] cursor-pointer transition-all flex flex-col justify-between"
                          style={{ borderColor: "var(--color-border)" }}
                        >
                          <div>
                            <div className="flex items-center justify-between">
                              <span className="font-mono text-xs font-bold text-[var(--color-primary)]">
                                {match.courseCode}
                              </span>
                              <span className="font-mono text-[10px] rounded px-1.5 py-0.5 bg-[var(--color-surface-sunken)] text-[var(--color-ink-muted)]">
                                {match.room}
                              </span>
                            </div>
                            <p className="mt-1 text-xs font-semibold text-[var(--color-ink)] line-clamp-1">
                              {match.courseName}
                            </p>
                          </div>

                          <div className="mt-2 flex items-center justify-between text-[10px] text-[var(--color-ink-muted)]">
                            <span className="truncate max-w-[85px]">{match.faculty.split(" ")[1]}</span>
                            <span className="font-semibold text-[var(--color-ink-faint)]">
                              {match.division.split(" ")[0]}
                            </span>
                          </div>
                        </div>
                      ) : (
                        <div className="h-full flex items-center justify-center text-[11px] text-[var(--color-ink-disabled)]">
                          —
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Slot Detail Modal ─────────────────────────────────────────────── */}
      {selectedSlot && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <div
            className="w-full max-w-md rounded-2xl border bg-[var(--color-surface)] p-6 shadow-2xl space-y-4 animate-fadeIn"
            style={{ borderColor: "var(--color-border-strong)" }}
          >
            <div className="flex items-center justify-between border-b pb-3" style={{ borderColor: "var(--color-border-subtle)" }}>
              <h3 className="font-heading text-base font-bold text-[var(--color-ink)]">
                {selectedSlot.courseCode}: {selectedSlot.courseName}
              </h3>
              <Badge variant="outline" className="font-mono text-xs">
                {selectedSlot.day} P{selectedSlot.period}
              </Badge>
            </div>

            <div className="space-y-3 text-xs">
              <div className="rounded-xl p-3 border space-y-2" style={{ backgroundColor: "var(--color-surface-sunken)", borderColor: "var(--color-border-subtle)" }}>
                <div className="flex items-center justify-between">
                  <span className="text-[var(--color-ink-muted)]">Scheduled Time:</span>
                  <span className="font-mono text-[var(--color-ink)] font-semibold">{selectedSlot.time}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-[var(--color-ink-muted)]">Classroom:</span>
                  <span className="font-semibold text-[var(--color-ink)]">{selectedSlot.room} (Capacity: 60)</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-[var(--color-ink-muted)]">Faculty Instructor:</span>
                  <span className="font-semibold text-[var(--color-primary)]">{selectedSlot.faculty}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-[var(--color-ink-muted)]">Enrolled Student Cohort:</span>
                  <span className="font-mono text-[var(--color-ink)]">{selectedSlot.division}</span>
                </div>
              </div>

              <div className="flex items-center gap-2 text-xs text-[var(--color-status-done)]">
                <CheckCircle2 size={14} />
                <span>Zero scheduling clashes detected against faculty or division calendars.</span>
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-3 border-t" style={{ borderColor: "var(--color-border-subtle)" }}>
              <button
                onClick={() => setSelectedSlot(null)}
                className="rounded-lg px-4 py-1.5 text-xs font-semibold text-white shadow-xs"
                style={{ backgroundColor: "var(--color-primary)" }}
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
