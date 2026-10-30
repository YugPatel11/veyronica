"use client";

import { useEffect } from "react";

interface KeyboardNavProps {
  onToggleCommandPalette: () => void;
  onToggleCopilot: () => void;
  onCloseAllModals: () => void;
}

export function useKeyboardNav({
  onToggleCommandPalette,
  onToggleCopilot,
  onCloseAllModals,
}: KeyboardNavProps) {
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      // Ctrl+K / Cmd+K: Command Palette
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        onToggleCommandPalette();
      }

      // Ctrl+J / Cmd+J: Copilot Sheet
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "j") {
        e.preventDefault();
        onToggleCopilot();
      }

      // Escape: Close open panels
      if (e.key === "Escape") {
        onCloseAllModals();
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onToggleCommandPalette, onToggleCopilot, onCloseAllModals]);
}

export function KeyboardNav(props: KeyboardNavProps) {
  useKeyboardNav(props);
  return null;
}
