import { resolvedTheme, type ThemePreference } from "./theme";
import { paletteById, paletteIcons, type PaletteId } from "./palettes";

/** The mode a palette will actually show. Midnight has no light mode. */
export function resolvedAppearance(
  theme: ThemePreference,
  palette: PaletteId,
  systemDark: boolean,
): "light" | "dark" {
  const modes = paletteById(palette).modes;
  const wanted = resolvedTheme(theme, systemDark);
  return modes.includes(wanted) ? wanted : modes[0];
}

/** Radius that covers the whole viewport from the reveal point. */
export function revealGeometry(
  width: number,
  height: number,
  point?: { x: number; y: number } | null,
) {
  const x = Math.round(point?.x ?? width / 2);
  const y = Math.round(point?.y ?? height / 2);
  const r = Math.ceil(
    Math.hypot(Math.max(x, width - x), Math.max(y, height - y)),
  );
  return { x, y, r };
}

let origin: { x: number; y: number } | null = null;
let tracking = false;
let revision = 0;
let active: ViewTransition | undefined;
/** Remember the last tap so a theme change spreads from the control you touched. */
export function trackRevealOrigin() {
  if (tracking || typeof document === "undefined") return;
  tracking = true;
  document.addEventListener(
    "pointerdown",
    (event) => {
      origin = { x: event.clientX, y: event.clientY };
    },
    { capture: true, passive: true },
  );
  document.addEventListener("keydown", () => {
    origin = null;
  });
}

function setHref(selector: string, href: string) {
  document.querySelectorAll<HTMLLinkElement>(selector).forEach((link) => {
    if (link.getAttribute("href") !== href) link.setAttribute("href", href);
  });
}

/** Browser chrome follows the palette: theme-color, tab icon, Home Screen icon, manifest. */
export function syncChrome(palette: PaletteId) {
  const bg = getComputedStyle(document.documentElement)
    .getPropertyValue("--bg")
    .trim();
  document
    .querySelectorAll<HTMLMetaElement>('meta[name="theme-color"]')
    .forEach((meta) => {
      meta.content = bg;
    });
  const icons = paletteIcons(palette);
  setHref('link[rel="icon"]', icons.svg);
  setHref('link[rel="apple-touch-icon"]', icons.touch);
  setHref('link[rel="manifest"]', icons.manifest);
}

/**
 * Apply theme + palette to <html>. With `animate`, the change runs inside a
 * view transition: a circle from the last tap for most palettes, a crossfade
 * for Mono. Callers pass animate=false for the first paint and reduced motion.
 */
export function applyAppearance({
  theme,
  palette,
  systemDark,
  animate,
}: {
  theme: ThemePreference;
  palette: PaletteId;
  systemDark: boolean;
  animate: boolean;
}) {
  const root = document.documentElement;
  const current = ++revision;
  active?.skipTransition();
  active = undefined;
  delete root.dataset.themeReveal;
  const mode = resolvedAppearance(theme, palette, systemDark);
  const update = () => {
    // Skipping a snapshot does not cancel its delayed update callback.
    if (current !== revision) return;
    root.dataset.theme = mode;
    root.dataset.palette = palette;
    syncChrome(palette);
  };
  const changed =
    root.dataset.theme !== mode || root.dataset.palette !== palette;
  if (!changed || !animate || !document.startViewTransition) {
    origin = null;
    update();
    return;
  }
  if (paletteById(palette).reveal === "circle") {
    const { x, y, r } = revealGeometry(innerWidth, innerHeight, origin);
    root.style.setProperty("--reveal-x", `${x}px`);
    root.style.setProperty("--reveal-y", `${y}px`);
    root.style.setProperty("--reveal-r", `${r}px`);
    root.dataset.themeReveal = "circle";
  }
  origin = null;
  const transition = document.startViewTransition(update);
  active = transition;
  void transition.ready.catch(() => {});
  void transition.finished
    .catch(() => {})
    .finally(() => {
      if (current !== revision) return;
      active = undefined;
      delete root.dataset.themeReveal;
    });
}
