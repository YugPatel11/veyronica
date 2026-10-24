/**
 * NEXUS Design System — Component Library
 *
 * EPIC-02: All base, data, status, layout, and feedback components.
 * Import from "@/components/ui" for tree-shakable access.
 */

// ── Base Components (§10.1) ──────────────────────────────────────────────────
export { Button, buttonVariants } from "./button";
export type { ButtonProps } from "./button";

export { Badge, badgeVariants } from "./badge";
export type { BadgeProps } from "./badge";

export { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter, cardVariants } from "./card";
export type { CardProps } from "./card";

export { Input } from "./input";
export type { InputProps } from "./input";

export { Textarea } from "./textarea";
export type { TextareaProps } from "./textarea";

export { Select } from "./select";
export type { SelectProps } from "./select";

export { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider } from "./tooltip";

export { Dialog, DialogPortal, DialogOverlay, DialogTrigger, DialogClose, DialogContent, DialogHeader, DialogFooter, DialogTitle, DialogDescription } from "./dialog";

export { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuLabel, DropdownMenuGroup, DropdownMenuSub } from "./dropdown-menu";

export { Tabs, TabsList, TabsTrigger, TabsContent } from "./tabs";

export { Separator } from "./separator";

export { Avatar } from "./avatar";

export { Toggle } from "./toggle";

export { Sheet } from "./sheet";

// ── Data Components (§10.2) ──────────────────────────────────────────────────
export { StatCard } from "./stat-card";

export { ProgressBar } from "./progress-bar";

export { Timeline } from "./timeline";
export type { TimelineEntry, TimelineProps } from "./timeline";

export { DataTable } from "./data-table";
export type { Column, DataTableProps } from "./data-table";

// ── Status Components (§10.3) ────────────────────────────────────────────────
export { StatusBadge } from "./status-badge";
export type { Status, StatusBadgeProps } from "./status-badge";

export { RiskBadge } from "./risk-badge";
export type { RiskLevel, RiskBadgeProps } from "./risk-badge";

export { ConfidenceIndicator } from "./confidence-indicator";
export type { ConfidenceIndicatorProps } from "./confidence-indicator";

// ── Layout Components (§10.4) ────────────────────────────────────────────────
export { PageHeader, SectionHeader } from "./page-header";

// ── Feedback Components (§10.5) ──────────────────────────────────────────────
export { Toaster, toast } from "./toast";

export { Skeleton, SkeletonCard, SkeletonTable } from "./skeleton";

export { EmptyState } from "./empty-state";

export { ErrorBoundary } from "./error-boundary";
