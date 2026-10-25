import { create } from "zustand";
import { readTheme, type ThemePreference } from "@/lib/theme";
import { readPalette, type PaletteId } from "@/lib/palettes";
import type { GreetingMode } from "@/lib/greetings";
function readGreeting(): GreetingMode {
  try {
    const value = localStorage.getItem("workbench-greeting");
    return value === "surprise" || value === "english" ? value : "languages";
  } catch {
    return "languages";
  }
}
function readStatusWords(): "playful" | "plain" {
  try {
    return localStorage.getItem("workbench-status-words") === "plain"
      ? "plain"
      : "playful";
  } catch {
    return "playful";
  }
}
type UI = {
  theme: ThemePreference;
  palette: PaletteId;
  greeting: GreetingMode;
  sidebar: boolean;
  collapsed: boolean;
  collapsedBeforeStudio?: boolean;
  panel: boolean;
  settings: boolean;
  settingsPane: string;
  command: boolean;
  choosePreset: boolean;
  answerFont: "serif" | "sans";
  textSize: "S" | "M" | "L";
  reduceMotion: "system" | "always";
  statusWords: "playful" | "plain";
  name: string;
  set: (patch: Partial<Omit<UI, "set">>) => void;
};
export const useUI = create<UI>((set) => ({
  theme: readTheme(),
  palette: readPalette(),
  greeting: readGreeting(),
  sidebar: false,
  collapsed: false,
  panel: false,
  settings: false,
  settingsPane: "Appearance",
  command: false,
  choosePreset: false,
  answerFont: "serif",
  textSize: "M",
  reduceMotion: "system",
  statusWords: readStatusWords(),
  name: "",
  set: (patch) => {
    if (patch.greeting) {
      try {
        localStorage.setItem("workbench-greeting", patch.greeting);
      } catch {
        /* The control still works when browser storage is unavailable. */
      }
    }
    if (patch.statusWords) {
      try {
        localStorage.setItem("workbench-status-words", patch.statusWords);
      } catch {
        /* The control still works when browser storage is unavailable. */
      }
    }
    set({
      ...(patch.sidebar ? { panel: false } : {}),
      ...(patch.panel ? { sidebar: false } : {}),
      ...(patch.settings || patch.command
        ? { sidebar: false, panel: false }
        : {}),
      ...patch,
    });
  },
}));
