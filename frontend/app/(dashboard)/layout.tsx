"use client";

import { type ReactNode } from "react";
import { AppShell } from "@/components/shell";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return <AppShell>{children}</AppShell>;
}
