"""Verify the exact G2 token pairs used by the interface, without third-party libraries.

TH1 adds palettes (web/src/styles/palettes.css). Every palette is checked in each mode it
offers, with the cascade the browser applies: base tokens, then the palette's light block,
then its dark block in dark mode. Cobalt's palette blocks must match the base tokens.
"""
import re
from pathlib import Path

STYLES = Path(__file__).resolve().parents[1] / "web/src/styles"
CSS = STYLES / "globals.css"
PALETTES = STYLES / "palettes.css"


def luminance(hex_color: str) -> float:
    values = [int(hex_color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    channels = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in values]
    return sum(value * weight for value, weight in zip(channels, (0.2126, 0.7152, 0.0722), strict=True))


def ratio(first: str, second: str) -> float:
    light, dark = sorted((luminance(first), luminance(second)), reverse=True)
    return (light + .05) / (dark + .05)


def tokens(block: str) -> dict[str, str]:
    return {key: value for key, value in re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6})", block)}


def pairs() -> list[tuple[str, str, float]]:
    surfaces = ("bg", "bg-sidebar", "surface", "surface-2", "user-bubble", "code-bg")
    result = [(foreground, background, threshold) for background in surfaces for foreground, threshold in (("text", 11.8), ("text-2", 6.4), ("text-3", 4.5), ("brand", 4.7))]
    # G2's exact dark text/surface-3 pair is 10.52:1, below its stated body target.
    # Preserve the locked palette; pressed-row labels must meet AA (4.5:1).
    # This spec discrepancy is documented in docs/PHASE-0-REPORT.md.
    result += [("text", "surface-3", 4.5), ("on-brand", "brand", 5.5), ("brand", "brand-soft", 4.5), ("text-2", "brand-soft", 4.5)]
    result += [("line-input", surface, 3.2) for surface in ("bg", "surface")]
    result += [("on-brand", "danger", 4.5)]
    result += [(foreground, background, 4.5) for foreground in ("danger", "warning") for background in ("bg", "surface", "surface-2")]
    result += [("cat-" + cat, bg, 3) for cat in ("input", "ai", "knowledge", "media", "logic", "review", "output") for bg in ("cat-" + cat + "-tint", "surface")]
    result += [("text", "note-" + tone, 4.5) for tone in ("neutral", "amber", "rose", "teal")]
    # TH1: the signature fill carries an icon or a knob, and citations stay readable.
    result += [("on-brand-fill", "brand-fill", 4.5), ("cite-text", "cite-bg", 7)]
    return result


def check(name: str, theme: dict[str, str], failures: list[str]) -> int:
    count = 0
    for foreground, background, threshold in pairs():
        actual = ratio(theme[foreground], theme[background])
        count += 1
        # G2 contrast figures are rounded to one decimal; allow only .001 numerical tolerance.
        if actual + .001 < threshold:
            failures.append(f"{name}: {foreground}/{background} = {actual:.3f}, requires {threshold}")
    return count


def palette_blocks(css: str) -> dict[str, dict[str, dict[str, str]]]:
    found: dict[str, dict[str, dict[str, str]]] = {}
    for palette, dark, block in re.findall(r'^\[data-palette="([\w-]+)"\](\[data-theme="dark"\])?\s*\{([^}]+)\}', css, re.M):
        values = tokens(block)
        if values:
            found.setdefault(palette, {})["dark" if dark else "light"] = values
    return found


def main() -> None:
    css = CSS.read_text()
    blocks = re.findall(r'(?:^:root|^\[data-theme="dark"\])\s*\{([^}]+)\}', css, re.M)
    themes = [tokens(block) for block in blocks[:2]]
    failures: list[str] = []
    count = 0
    for name, theme in zip(("light", "dark"), themes, strict=True):
        count += check(name, theme, failures)
        print(f"{name}: body/background {ratio(theme['text'], theme['bg']):.2f}:1; secondary {ratio(theme['text-2'], theme['surface-2']):.2f}:1; tertiary {ratio(theme['text-3'], theme['surface-2']):.2f}:1")
    palettes = palette_blocks(PALETTES.read_text())
    for palette, modes in sorted(palettes.items()):
        if "light" in modes and "dark" in modes and set(modes["light"]) != set(modes["dark"]):
            failures.append(f"{palette}: light and dark blocks must set the same tokens")
        if palette == "cobalt":
            for mode, base in zip(("light", "dark"), themes, strict=True):
                drift = sorted(key for key, value in modes[mode].items() if base.get(key, "").lower() != value.lower())
                if drift:
                    failures.append(f"cobalt/{mode}: palettes.css differs from globals.css for {', '.join(drift)}")
        # A palette with a single block (Midnight) is dark only; lib/appearance.ts forces dark.
        offered = ("light", "dark") if "dark" in modes else ("dark",)
        for mode in offered:
            theme = {**themes[0]} if mode == "light" else {**themes[0], **themes[1]}
            theme.update(modes["light"])
            theme.update(modes.get("dark", {}) if mode == "dark" else {})
            count += check(f"{palette}/{mode}", theme, failures)
    if failures:
        raise SystemExit("\n".join(failures))
    print(f"Contrast: {count} token pairs passed ({len(palettes)} palettes).")


if __name__ == "__main__":
    main()
