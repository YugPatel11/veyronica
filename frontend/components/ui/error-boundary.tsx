"use client";

import * as React from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";
import { Button } from "./button";

/**
 * ErrorBoundary — EPIC-02-T08
 *
 * Catches component crashes, shows friendly error + retry button.
 */

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorId: string;
}

export class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null, errorId: "" };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    const errorId = `err_${Date.now().toString(36)}`;
    return { hasError: true, error, errorId };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("[ErrorBoundary]", error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null, errorId: "" });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
          <div className="rounded-full bg-[var(--color-status-failed-bg)] p-4">
            <AlertTriangle
              size={48}
              strokeWidth={1.25}
              className="text-[var(--color-status-failed)]"
            />
          </div>
          <h3 className="mt-4 font-heading text-lg font-semibold text-[var(--color-ink)]">
            Something went wrong
          </h3>
          <p className="mt-1.5 max-w-sm text-sm text-[var(--color-ink-muted)]">
            An unexpected error occurred. Please try again or contact support if
            the problem persists.
          </p>
          <p className="mt-2 font-mono text-[11px] text-[var(--color-ink-disabled)]">
            Error ID: {this.state.errorId}
          </p>
          <Button
            variant="outline"
            size="md"
            onClick={this.handleRetry}
            className="mt-5"
          >
            <RefreshCw size={16} />
            Try again
          </Button>
        </div>
      );
    }

    return this.props.children;
  }
}
