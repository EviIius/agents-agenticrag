export type ThemePreference = "system" | "light" | "dark";
export function resolvedTheme(
  preference: ThemePreference,
  systemDark: boolean,
): "light" | "dark" {
  return preference === "system" ? (systemDark ? "dark" : "light") : preference;
}
export function readTheme(): ThemePreference {
  try {
    const value = localStorage.getItem("workbench-theme");
    return value === "light" || value === "dark" ? value : "system";
  } catch {
    return "system";
  }
}
