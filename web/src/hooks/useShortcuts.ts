import { useEffect } from "react";
import type { NavigateFunction } from "react-router";
import { useUI } from "@/stores/ui";
export function useShortcuts({
  navigate,
  ui,
  desktop,
}: {
  navigate: NavigateFunction;
  ui: ReturnType<typeof useUI.getState>;
  desktop: boolean;
}) {
  useEffect(() => {
    const listener = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        ui.set({ command: true });
      }
      if ((e.metaKey || e.ctrlKey) && e.key === ",") {
        e.preventDefault();
        ui.set({
          settings: true,
          sidebar: false,
          panel: false,
          command: false,
        });
      }
      if (
        (e.metaKey || e.ctrlKey) &&
        e.shiftKey &&
        e.key.toLowerCase() === "o"
      ) {
        e.preventDefault();
        ui.set({
          command: false,
          settings: false,
          panel: false,
          sidebar: false,
        });
        navigate("/");
      }
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "b") {
        e.preventDefault();
        ui.set(
          desktop ? { collapsed: !ui.collapsed } : { sidebar: !ui.sidebar },
        );
      }
      if (
        (e.metaKey || e.ctrlKey) &&
        e.shiftKey &&
        (e.key === ">" || e.code === "Period")
      ) {
        e.preventDefault();
        ui.set({ panel: !ui.panel });
      }
      if ((e.metaKey || e.ctrlKey) && e.key === "/") {
        e.preventDefault();
        ui.set({ settings: true, settingsPane: "Shortcuts", command: false });
      }
    };
    window.addEventListener("keydown", listener);
    return () => window.removeEventListener("keydown", listener);
  }, [navigate, ui, desktop]);
}
