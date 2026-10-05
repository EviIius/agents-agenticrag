import { create } from "zustand";
import { readTheme, type ThemePreference } from "@/lib/theme";
type UI = {
  theme: ThemePreference;
  sidebar: boolean;
  collapsed: boolean;
  panel: boolean;
  settings: boolean;
  settingsPane: string;
  command: boolean;
  choosePreset: boolean;
  answerFont: "serif" | "sans";
  textSize: "S" | "M" | "L";
  reduceMotion: "system" | "always";
  name: string;
  set: (patch: Partial<Omit<UI, "set">>) => void;
};
export const useUI = create<UI>((set) => ({
  theme: readTheme(),
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
  name: "",
  set: (patch) =>
    set({
      ...(patch.sidebar ? { panel: false } : {}),
      ...(patch.panel ? { sidebar: false } : {}),
      ...(patch.settings || patch.command
        ? { sidebar: false, panel: false }
        : {}),
      ...patch,
    }),
}));
