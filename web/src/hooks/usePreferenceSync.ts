import { useEffect, useRef } from "react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { useUI } from "@/stores/ui";

/** Appearance is stored on the Mac so it follows the user between devices. */
export function usePreferenceSync(settings?: Record<string, unknown>) {
  const hydrated = useRef(false);
  useEffect(() => {
    if (!settings || hydrated.current) return;
    hydrated.current = true;
    const patch: Parameters<ReturnType<typeof useUI.getState>["set"]>[0] = {};
    const theme = settings["appearance.theme"];
    if (theme === "light" || theme === "dark" || theme === "system")
      patch.theme = theme;
    const font = settings["appearance.font"];
    if (font === "serif" || font === "sans") patch.answerFont = font;
    const size = settings["appearance.size"];
    if (size === "S" || size === "M" || size === "L") patch.textSize = size;
    const motion = settings["appearance.reduce_motion"];
    if (motion === "system" || motion === "always") patch.reduceMotion = motion;
    if (typeof settings.user_name === "string") patch.name = settings.user_name;
    useUI.getState().set(patch);
  }, [settings]);
  useEffect(() => {
    const preferences = (state: ReturnType<typeof useUI.getState>) => ({
      "appearance.theme": state.theme,
      "appearance.font": state.answerFont,
      "appearance.size": state.textSize,
      "appearance.reduce_motion": state.reduceMotion,
      user_name: state.name,
    });
    let timer: ReturnType<typeof setTimeout> | undefined;
    const unsubscribe = useUI.subscribe((state, previous) => {
      if (!hydrated.current) return;
      const values = preferences(state);
      if (JSON.stringify(values) === JSON.stringify(preferences(previous)))
        return;
      clearTimeout(timer);
      timer = setTimeout(() => {
        void api("/settings", values, "PATCH").catch(() =>
          toast("Couldn't save preferences. Try again."),
        );
      }, 300);
    });
    return () => {
      clearTimeout(timer);
      unsubscribe();
    };
  }, []);
}
