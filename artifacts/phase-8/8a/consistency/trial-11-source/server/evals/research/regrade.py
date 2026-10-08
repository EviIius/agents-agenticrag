"""Deterministic grading revision; retained baseline answers, no model calls."""

import hashlib
import json
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts/phase-8/8a"


def cases() -> list[dict]:
    rows = json.loads((HERE / "cases.yaml").read_text())
    row = next(c for c in rows if c["id"] == "python-environment-threads")
    # Same portability fact, stated through the documented hardcoded-path mechanism.
    # Recreation and the separate sqlite thread requirements remain independently required.
    row["expect"]["must_include"][0] += (
        r"|(?i:hardcoded\s+path[^.!?\n]{0,100}(?:original|virtual environment|directory|location))"
    )
    return rows


def facts(answer: str, case: dict) -> bool:
    answer = unicodedata.normalize("NFKC", answer).translate(
        str.maketrans({c: "-" for c in "‐‑‒–—―−"})
    )
    return all(re.search(pattern, answer) for pattern in case["expect"]["must_include"])


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    revised = cases()
    (OUT / "cases-grading-v2.json").write_text(json.dumps(revised, indent=2) + "\n")
    result = {
        "revision": 2,
        "model_calls": 0,
        "changes": {
            "python-environment-threads": (
                "Accept equivalent hardcoded path dependence. "
                "All remaining fact requirements unchanged."
            ),
            "linux-link-lifetime": (
                "No change: live omits all/last descriptor qualifier; replay includes it."
            ),
        },
        "reports": [],
    }
    for mode in ("baseline-record", "baseline-replay"):
        file = next((ROOT / "artifacts/phase-8/gate" / mode / "reports").glob("*.json"))
        report = json.loads(file.read_text())
        judgments = [
            {
                "id": c["id"],
                "original": r["required_facts"],
                "revised": facts(r["turns"][-1]["message"]["content"], c),
            }
            for c, r in zip(revised, report["results"], strict=True)
        ]
        result["reports"].append(
            {
                "source": str(file.relative_to(ROOT)),
                "sha256": hashlib.sha256(file.read_bytes()).hexdigest(),
                "judgments": judgments,
                "complete": sum(j["revised"] for j in judgments),
                "total": len(judgments),
            }
        )
    result["candidate_minimum_complete"] = 13
    result["candidate_basis"] = (
        "10/15 baseline; at least 80% and 15 percentage points requires 13/15 (86.67%). "
        "Regex screening is separate from unsupported-claim/citation review."
    )
    (OUT / "baseline-regrade.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
