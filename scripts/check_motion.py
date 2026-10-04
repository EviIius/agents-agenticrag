"""Keep first-party motion in one stylesheet and reject dead utility classes."""

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEAD = re.compile(
    r"(?<![\w-])(?:animate-(?:in|out)|(?:fade|zoom)-(?:in|out)(?:-\d+)?|slide-(?:in-from|out-to)-[\w-]+|transition-all)(?![\w-])"
)
ALLOWED = {"opacity", "transform", "height", "width", "stroke-dasharray"}


def violations(source: Path, allow_globals: bool = False) -> list[str]:
    errors = []
    motion = source / "styles/motion.css"
    for path in sorted(source.rglob("*")):
        if path.suffix not in {".tsx", ".ts", ".css"}:
            continue
        text = path.read_text()
        relative = path.relative_to(source)
        for match in DEAD.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            errors.append(f"{relative}:{line}: dead utility {match.group()}")
        for match in re.finditer(r"@keyframes\s+([\w-]+)\s*\{", text):
            name = match.group(1)
            if path != motion and not (allow_globals and relative == Path("styles/globals.css")):
                errors.append(f"{relative}: keyframe {name} outside motion.css")
            start, depth, end = match.end(), 1, match.end()
            while end < len(text) and depth:
                depth += (text[end] == "{") - (text[end] == "}")
                end += 1
            block = text[start : end - 1]
            for prop in re.findall(r"([\w-]+)\s*:", block):
                if prop not in ALLOWED:
                    errors.append(f"{relative}: {name} animates forbidden {prop}")
            outside = text[: match.start()] + text[end:]
            if not re.search(r"\b" + re.escape(name) + r"\b", outside):
                errors.append(f"{relative}: unused keyframe {name}")
        if re.search(r"will-change\s*:", text):
            errors.append(f"{relative}: static will-change")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args()
    errors = violations(ROOT / "web/src", args.report_only)
    print("\n".join(errors) or "Motion guard: all first-party motion rules pass.")
    if errors and not args.report_only:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
