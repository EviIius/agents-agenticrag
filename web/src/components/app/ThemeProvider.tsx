import { useEffect, useInsertionEffect, useRef, type ReactNode } from "react";
import { useUI } from "@/stores/ui";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { resolvedTheme } from "@/lib/theme";
export function ThemeProvider({ children }: { children: ReactNode }) {
  const reduced = useReducedMotion();
  const applied = useRef(false);
  const { theme, answerFont, textSize, reduceMotion } = useUI();
  useEffect(() => {
    const media = matchMedia("(prefers-color-scheme: dark)");
    const apply = () => {
      const resolved = resolvedTheme(theme, media.matches);
      const update = () => {
        document.documentElement.dataset.theme = resolved;
        const bg = getComputedStyle(document.documentElement)
          .getPropertyValue("--bg")
          .trim();
        document
          .querySelectorAll<HTMLMetaElement>('meta[name="theme-color"]')
          .forEach((meta) => {
            meta.content = bg;
          });
      };
      if (
        applied.current &&
        document.documentElement.dataset.theme !== resolved &&
        !reduced &&
        document.startViewTransition
      ) {
        const transition = document.startViewTransition(update);
        void transition.finished.catch(() => {});
      } else update();
      applied.current = true;
    };
    apply();
    try {
      localStorage.setItem("workbench-theme", theme);
    } catch {
      /* Storage may be unavailable. */
    }
    media.addEventListener("change", apply);
    return () => media.removeEventListener("change", apply);
  }, [theme, reduced]);
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
