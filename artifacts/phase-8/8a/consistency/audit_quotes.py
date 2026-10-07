"""Offline excerpt-location aid, not a semantic grader or qualification gate."""

import json
import re
import sys
from pathlib import Path


def wording(text):
    # Preserve names, punctuation, case, values, underscores and HTML placeholders.
    return " ".join(text.replace("**", "").replace("`", "").replace(r"\|", "|").split())


def audit(directory):
    rows = []
    for path in sorted(directory.glob("*.json")):
        if path.name in {"inputs.json", "report.json"}:
            continue
        result = json.loads(path.read_text())
        sources = {s["n"]: s for s in result["sources"]}
        for line_number, line in enumerate(result["message"]["content"].splitlines(), 1):
            match = re.fullmatch(
                r"\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*((?:\[\d+\]\s*)+)\|\s*", line
            )
            if not match:
                continue
            part, quote, labels = match.groups()
            if (quote[:1], quote[-1:]) in {(chr(34), chr(34)), ("“", "”")}:
                quote = quote[1:-1]
            cited = [int(n) for n in re.findall(r"\[(\d+)\]", labels)]
            located = []
            for number in cited:
                source = sources.get(number)
                if source is None:
                    continue
                candidates = [source["title"]]
                candidates.extend(p["text"] for p in source["passages"])
                candidates.extend(p["heading"] for p in source["passages"] if p["heading"])
                if quote and any(wording(quote) in wording(text) for text in candidates):
                    located.append(number)
            rows.append(
                {
                    "case": result["id"],
                    "line": line_number,
                    "part": part,
                    "excerpt": quote,
                    "cited": cited,
                    "located_in_cited_source": located,
                    "needs_literal_review": not located,
                }
            )
    return {
        "scope": "Offline aid for three-column evidence tables; no model calls or answer edits.",
        "normalization": "Whitespace, backticks, bold markers and escaped table pipes only.",
        "limits": (
            "Literal location cannot establish subject binding, qualifications, completeness "
            "or every citation's semantic support. Unparsed/missing rows and all assertions "
            "still require manual review. A match is not a semantic pass."
        ),
        "rows_examined": len(rows),
        "needs_literal_review": sum(r["needs_literal_review"] for r in rows),
        "rows": rows,
    }


if __name__ == "__main__":
    destination = Path(sys.argv[2])
    if destination.exists():
        raise SystemExit("Use a new output file; retain earlier audits.")
    destination.write_text(json.dumps(audit(Path(sys.argv[1])), indent=2) + "\n")
