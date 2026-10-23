import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NEXUS — Agentic Workflow Intelligence",
  description:
    "AI-powered workflow automation platform with policy-driven approvals, tamper-evident audit, and impact analytics.",
  robots: { index: false, follow: false }, // Private platform — no indexing
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-canvas text-ink antialiased">
        <a href="#main-content" className="skip-link">
          Skip to main content
        </a>
        {children}
      </body>
    </html>
  );
}
