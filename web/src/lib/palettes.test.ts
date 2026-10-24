import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { PALETTE_IDS, PALETTES, isPaletteId, paletteIcons } from "./palettes";
import { resolvedAppearance, revealGeometry } from "./appearance";

const css = readFileSync(
  new URL("../styles/palettes.css", import.meta.url),
  "utf8",
);
const init = readFileSync(
  new URL("../../public/theme-init.js", import.meta.url),
  "utf8",
);

describe("Palettes", () => {
  it("lists each palette once, in picker order, with a CSS block", () => {
    expect(PALETTES.map((p) => p.id)).toEqual([...PALETTE_IDS]);
    for (const id of PALETTE_IDS)
      expect(css).toContain(`[data-palette="${id}"] {`);
  });
  it("gives every dark-capable palette a dark block, and Midnight none", () => {
    for (const palette of PALETTES) {
      const dark = css.includes(
        `[data-palette="${palette.id}"][data-theme="dark"] {`,
      );
      expect(dark).toBe(palette.modes.includes("light"));
    }
  });
  it("keeps status word lists long enough to rotate without repeats", () => {
    for (const palette of PALETTES)
      if (palette.words) {
        expect(palette.words.length).toBeGreaterThanOrEqual(12);
        expect(new Set(palette.words).size).toBe(palette.words.length);
      }
  });
  it("keeps theme-init.js in step, so the first paint has the right palette", () => {
    for (const id of PALETTE_IDS) expect(init).toContain(`"${id}"`);
    for (const palette of PALETTES)
      if (!palette.modes.includes("light"))
        expect(init).toContain(`palette === "${palette.id}"`);
  });
  it("validates stored values", () => {
    expect(isPaletteId("lime")).toBe(true);
    expect(isPaletteId("neon")).toBe(false);
    expect(isPaletteId(null)).toBe(false);
  });
  it("keeps Cobalt's original icon paths", () => {
    expect(paletteIcons("cobalt").touch).toBe("/icons/apple-touch-icon.png");
    expect(paletteIcons("lime")).toEqual({
      svg: "/icons/lime/mark.svg",
      touch: "/icons/lime/apple-touch-icon.png",
      manifest: "/manifests/lime.webmanifest",
    });
  });
});

describe("Appearance", () => {
  it("forces Midnight to dark and otherwise follows the theme choice", () => {
    expect(resolvedAppearance("light", "midnight", false)).toBe("dark");
    expect(resolvedAppearance("system", "lime", true)).toBe("dark");
    expect(resolvedAppearance("system", "lime", false)).toBe("light");
    expect(resolvedAppearance("light", "paper", true)).toBe("light");
  });
  it("reveals from the tap with a radius that reaches the far corner", () => {
    expect(revealGeometry(400, 800, { x: 380, y: 40 })).toEqual({
      x: 380,
      y: 40,
      r: Math.ceil(Math.hypot(380, 760)),
    });
    expect(revealGeometry(400, 800)).toEqual({
      x: 200,
      y: 400,
      r: Math.ceil(Math.hypot(200, 400)),
    });
  });
});
