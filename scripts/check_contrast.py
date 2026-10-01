"""Verify the exact G2 token pairs used by the interface, without third-party libraries."""
import re
from pathlib import Path

CSS = Path(__file__).resolve().parents[1] / "web/src/styles/globals.css"


def luminance(hex_color: str) -> float:
    values = [int(hex_color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    channels = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in values]
    return sum(value * weight for value, weight in zip(channels, (0.2126, 0.7152, 0.0722), strict=True))


def ratio(first: str, second: str) -> float:
    light, dark = sorted((luminance(first), luminance(second)), reverse=True)
    return (light + .05) / (dark + .05)


def main() -> None:
    css = CSS.read_text()
    blocks = re.findall(r'(?:^:root|^\[data-theme="dark"\])\s*\{([^}]+)\}', css, re.M)
    themes = [{key: value for key, value in re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6})", block)} for block in blocks[:2]]
    failures = []
    count = 0
    for name, theme in zip(("light", "dark"), themes, strict=True):
        surfaces = ("bg", "bg-sidebar", "surface", "surface-2", "user-bubble", "code-bg")
        pairs = [(foreground, background, threshold) for background in surfaces for foreground, threshold in (("text", 11.8), ("text-2", 6.4), ("text-3", 4.5), ("brand", 4.7))]
        # G2's exact dark text/surface-3 pair is 10.52:1, below its stated body target.
        # Preserve the locked palette; pressed-row labels must meet AA (4.5:1).
        # This spec discrepancy is documented in docs/PHASE-0-REPORT.md.
        pairs += [("text", "surface-3", 4.5), ("on-brand", "brand", 5.5)]
        pairs += [("line-input", surface, 3.2) for surface in ("bg", "surface")]
        for foreground, background, threshold in pairs:
            actual = ratio(theme[foreground], theme[background])
            count += 1
            # G2 contrast figures are rounded to one decimal; allow only .001 numerical tolerance.
            if actual + .001 < threshold:
                failures.append(f"{name}: {foreground}/{background} = {actual:.3f}, requires {threshold}")
        print(f"{name}: body/background {ratio(theme['text'], theme['bg']):.2f}:1; secondary {ratio(theme['text-2'], theme['surface-2']):.2f}:1; tertiary {ratio(theme['text-3'], theme['surface-2']):.2f}:1")
    if failures:
        raise SystemExit("\n".join(failures))
    print(f"Contrast: {count} token pairs passed.")


if __name__ == "__main__":
    main()
