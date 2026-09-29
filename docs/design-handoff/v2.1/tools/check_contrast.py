"""Check WCAG contrast for every theme x accent x contrast combination.

Usage:
    python docs/design-handoff/v2.1/tools/check_contrast.py src/agenticrag/ui/tokens.css [tokens-themes.css]

With one argument (after tokens-themes.css has been merged into tokens.css) it reads both sets from
that file. Exits 1 if any pair fails. Safe to call from a pytest test.
"""
from __future__ import annotations

import itertools
import re
import sys
from pathlib import Path

GROUNDS = ["--bg", "--sidebar", "--surface", "--surface-raised"]
TEXT = ["--ink", "--ink-secondary", "--ink-muted", "--primary-text", "--evidence", "--success", "--warning", "--danger"]
THEMES = ["dark", "light", "midnight", "paper"]
ACCENTS = ["cobalt", "amber", "graphite"]


def luminance(hex_value: str) -> float:
    value = hex_value.lstrip("#")
    channels = [int(value[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def ratio(a: str, b: str) -> float:
    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def blocks(css: str) -> list[tuple[str, dict[str, str]]]:
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    out = []
    for selector, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        values = dict(re.findall(r"(--[\w-]+):\s*(#[0-9A-Fa-f]{6})\b", body))
        if values:
            out.append((" ".join(selector.split()), values))
    return out


def tokens_for(all_blocks, theme: str, accent: str, more_contrast: bool) -> dict[str, str]:
    result: dict[str, str] = {}
    for selector, values in all_blocks:
        parts = [part.strip() for part in re.split(r",(?![^()]*\))", selector)]
        for part in parts:
            if "data-accent" in part or "data-contrast" in part:
                continue
            if part == ":root" and theme == "dark" or f'[data-theme="{theme}"]' == part:
                result.update(values)
    for selector, values in all_blocks:
        if f'"{theme}"' not in selector:
            continue
        if accent != "cobalt" and f'[data-accent="{accent}"]' in selector:
            result.update(values)
        if more_contrast and '[data-contrast="more"]' in selector:
            result.update(values)
    return result


def main(paths: list[str]) -> int:
    css = "\n".join(Path(p).read_text(encoding="utf-8") for p in paths)
    all_blocks = blocks(css)
    failures = []
    for theme, accent, more in itertools.product(THEMES, ACCENTS, (False, True)):
        t = tokens_for(all_blocks, theme, accent, more)
        label = f"{theme}/{accent}/{'more' if more else 'normal'}"
        missing = [k for k in GROUNDS + TEXT + ["--primary", "--primary-ink", "--focus"] if k not in t]
        if missing:
            failures.append(f"{label}: missing {missing}")
            continue
        for fg in TEXT:
            worst = min(ratio(t[fg], t[g]) for g in GROUNDS)
            if worst < 4.5:
                failures.append(f"{label}: {fg} {worst:.2f} < 4.5")
        if ratio(t["--primary-ink"], t["--primary"]) < 4.5:
            failures.append(f"{label}: --primary-ink on --primary {ratio(t['--primary-ink'], t['--primary']):.2f} < 4.5")
        for key in ("--primary", "--focus"):
            worst = min(ratio(t[key], t[g]) for g in GROUNDS)
            if worst < 3.0:
                failures.append(f"{label}: {key} vs surfaces {worst:.2f} < 3.0")
    if ratio("#FFFFFF", "#C93A31") < 4.5:
        failures.append("white on --danger-fill < 4.5")
    print(f"Checked {len(THEMES) * len(ACCENTS) * 2} combinations.")
    print("\n".join(failures) if failures else "All pass.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or ["src/agenticrag/ui/tokens.css"]))
