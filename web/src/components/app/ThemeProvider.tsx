import { useEffect, useInsertionEffect, useRef, type ReactNode } from "react";
import { useUI } from "@/stores/ui";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { applyAppearance, trackRevealOrigin } from "@/lib/appearance";
import { PALETTE_STORAGE_KEY } from "@/lib/palettes";
export function ThemeProvider({ children }: { children: ReactNode }) {
  const reduced = useReducedMotion();
  const applied = useRef(false);
  const { theme, palette, answerFont, textSize, reduceMotion } = useUI();
  useEffect(() => {
    trackRevealOrigin();
    const media = matchMedia("(prefers-color-scheme: dark)");
    const apply = () => {
      applyAppearance({
        theme,
        palette,
        systemDark: media.matches,
        animate: applied.current && !reduced,
      });
      applied.current = true;
    };
    apply();
    try {
      localStorage.setItem("workbench-theme", theme);
      localStorage.setItem(PALETTE_STORAGE_KEY, palette);
    } catch {
      /* Storage may be unavailable. */
    }
    media.addEventListener("change", apply);
    return () => media.removeEventListener("change", apply);
  }, [theme, palette, reduced]);
  // Apply motion CSS before Radix layout effects decide whether an exit is animated.
  // A passive effect cancels that exit afterward, leaving Presence waiting forever.
  useInsertionEffect(() => {
    Object.assign(document.documentElement.dataset, {
      answerFont,
      textSize,
      reduceMotion,
    });
  }, [answerFont, textSize, reduceMotion]);
  useEffect(() => {
    const viewport = window.visualViewport;
    const resize = () => {
      document.documentElement.toggleAttribute(
        "data-compact-viewport",
        (viewport?.height ?? window.innerHeight) < 480,
      );
      document.documentElement.style.setProperty(
        "--viewport-h",
        `${viewport?.height ?? window.innerHeight}px`,
      );
      document.documentElement.style.setProperty(
        "--viewport-top",
        `${viewport?.offsetTop ?? 0}px`,
      );
      document.documentElement.style.setProperty(
        "--viewport-bottom",
        `${Math.max(0, window.innerHeight - (viewport?.height ?? window.innerHeight) - (viewport?.offsetTop ?? 0))}px`,
      );
    };
    resize();
    viewport?.addEventListener("resize", resize);
    viewport?.addEventListener("scroll", resize);
    window.addEventListener("resize", resize);
    return () => {
      viewport?.removeEventListener("resize", resize);
      viewport?.removeEventListener("scroll", resize);
      window.removeEventListener("resize", resize);
    };
  }, []);
  return children;
}
