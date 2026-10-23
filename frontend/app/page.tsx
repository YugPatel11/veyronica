"use client";

import { useState, type FormEvent } from "react";
import { Eye, EyeOff, Loader2 } from "lucide-react";

/**
 * Login page — matches design/screens/login.png
 *
 * Centred card on oat canvas with NEXUS serif wordmark.
 * Inputs: email + password with show/hide toggle.
 * Primary teal button. No hero images or illustrations.
 */
export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => null);
        const message =
          body?.error?.message ?? "Invalid email or password";
        setError(message);
        return;
      }

      const data = await res.json();
      // Store tokens (Phase 1 will use httpOnly cookies or secure storage)
      if (typeof window !== "undefined") {
        sessionStorage.setItem("nexus_access_token", data.access_token);
        sessionStorage.setItem("nexus_refresh_token", data.refresh_token);
      }

      // Redirect to dashboard
      window.location.href = "/overview";
    } catch {
      setError("Unable to connect to the server");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center p-4">
      <div
        className="w-full max-w-[400px] rounded-[var(--radius-lg)] bg-surface p-8 shadow-[var(--shadow-lg)]"
        style={{ border: "1px solid var(--color-border-subtle)" }}
      >
        {/* Wordmark */}
        <div className="mb-6 text-center">
          <h1
            className="font-heading text-[2rem] font-bold tracking-tight"
            style={{ color: "var(--color-primary)" }}
          >
            NEXUS
          </h1>
          <p className="mt-1 text-sm text-ink-muted">
            Agentic Workflow Intelligence
          </p>
        </div>

        {/* Separator */}
        <div
          className="mb-6 h-px w-full"
          style={{ backgroundColor: "var(--color-border)" }}
        />

        {/* Error message */}
        {error && (
          <div
            className="mb-4 rounded-[var(--radius-md)] px-4 py-3 text-sm"
            style={{
              backgroundColor: "var(--color-status-failed-bg)",
              color: "var(--color-status-failed)",
              border: "1px solid var(--color-status-failed)",
            }}
            role="alert"
          >
            {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Email */}
          <div>
            <label
              htmlFor="email"
              className="mb-1.5 block text-sm font-medium text-ink"
            >
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              autoComplete="email"
              placeholder="name@institution.edu"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={isLoading}
              className="block w-full rounded-[var(--radius-md)] bg-surface-raised px-3 py-2.5 text-sm text-ink placeholder:text-ink-disabled transition-colors duration-100"
              style={{
                border: "1px solid var(--color-border)",
                outline: "none",
              }}
              onFocus={(e) => {
                e.currentTarget.style.borderColor = "var(--color-primary)";
                e.currentTarget.style.boxShadow =
                  "0 0 0 3px var(--color-primary-subtle)";
              }}
              onBlur={(e) => {
                e.currentTarget.style.borderColor = "var(--color-border)";
                e.currentTarget.style.boxShadow = "none";
              }}
            />
          </div>

          {/* Password */}
          <div>
            <label
              htmlFor="password"
              className="mb-1.5 block text-sm font-medium text-ink"
            >
              Password
            </label>
            <div className="relative">
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                required
                minLength={8}
                autoComplete="current-password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoading}
                className="block w-full rounded-[var(--radius-md)] bg-surface-raised px-3 py-2.5 pr-10 text-sm text-ink placeholder:text-ink-disabled transition-colors duration-100"
                style={{
                  border: "1px solid var(--color-border)",
                  outline: "none",
                }}
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = "var(--color-primary)";
                  e.currentTarget.style.boxShadow =
                    "0 0 0 3px var(--color-primary-subtle)";
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = "var(--color-border)";
                  e.currentTarget.style.boxShadow = "none";
                }}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-ink-muted hover:text-ink transition-colors"
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? (
                  <EyeOff size={18} strokeWidth={1.75} />
                ) : (
                  <Eye size={18} strokeWidth={1.75} />
                )}
              </button>
            </div>
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={isLoading}
            className="flex w-full items-center justify-center gap-2 rounded-[var(--radius-md)] px-4 py-2.5 text-sm font-semibold text-white transition-colors duration-100 disabled:opacity-60"
            style={{
              backgroundColor: isLoading
                ? "var(--color-primary-hover)"
                : "var(--color-primary)",
            }}
            onMouseEnter={(e) => {
              if (!isLoading)
                e.currentTarget.style.backgroundColor =
                  "var(--color-primary-hover)";
            }}
            onMouseLeave={(e) => {
              if (!isLoading)
                e.currentTarget.style.backgroundColor =
                  "var(--color-primary)";
            }}
          >
            {isLoading && (
              <Loader2 size={16} className="animate-spin" />
            )}
            {isLoading ? "Signing in…" : "Sign in"}
          </button>
        </form>

        {/* Forgot password link */}
        <p className="mt-4 text-center">
          <a
            href="#"
            className="text-sm transition-colors duration-100"
            style={{ color: "var(--color-primary)" }}
            onMouseEnter={(e) => {
              e.currentTarget.style.color = "var(--color-primary-hover)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.color = "var(--color-primary)";
            }}
          >
            Forgot password?
          </a>
        </p>

        {/* Version */}
        <p className="mt-6 text-center text-xs text-ink-disabled">
          v0.1.0 · Secured with MFA
        </p>
      </div>
    </main>
  );
}
