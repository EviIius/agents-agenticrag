#!/usr/bin/env python3
"""Fail when a built stylesheet ships -webkit-backdrop-filter without backdrop-filter.

Vite's minifier merges the two declarations and keeps only the last one, so a
rule written `backdrop-filter: …; -webkit-backdrop-filter: …;` reaches the
browser with the prefixed line only, which Chrome ignores.

Usage: python3 scripts/check_glass_css.py server/app/static/assets
       python3 scripts/check_glass_css.py --source web/src
"""

import argparse
import pathlib
import re

RULE = re.compile(r"([^{}]+)\{([^{}]*)\}")
COMMENTS = re.compile(r"/\*.*?\*/", re.S)
DECLARATION = re.compile(r"^(-webkit-backdrop-filter|backdrop-filter)\s*:")


def problems(css: str, *, source: bool = False) -> list[str]:
    found = []
    for selector, body in RULE.findall(COMMENTS.sub("", css)):
        names = [
            match.group(1)
            for declaration in body.split(";")
            if (match := DECLARATION.match(declaration.strip()))
        ]
        if "-webkit-backdrop-filter" not in names:
            continue
        label = selector.strip()[:160]
        if "backdrop-filter" not in names:
            found.append(f"{label}: prefixed backdrop-filter without standard declaration")
        elif source and names[-1] == "-webkit-backdrop-filter":
            found.append(f"{label}: standard backdrop-filter must follow the prefixed declaration")
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=pathlib.Path,
                        default=pathlib.Path(__file__).resolve().parents[1] / "server/app/static/assets")
    parser.add_argument("--source", action="store_true", help="also reject unsafe declaration order")
    args = parser.parse_args()
    root = args.root
    files = sorted(root.rglob("*.css") if args.source else root.glob("*.css"))
    if not files:
        print(f"check_glass_css: no .css files under {root}; run vite build first")
        return 2
    bad = [(str(f.relative_to(root)), s) for f in files
           for s in problems(f.read_text(), source=args.source)]
    for name, selector in bad:
        print(f"{name}: {selector}")
    if bad:
        print(f"check_glass_css: {len(bad)} rule(s) would lose their blur in Chrome")
        return 1
    print(f"check_glass_css: {len(files)} stylesheet(s) OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
