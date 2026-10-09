"""Versioned citation regrades of retained answers; no inference or overwrites."""

import hashlib
import json
import sys
from pathlib import Path

SERVER = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SERVER))
from evals.library.run_eval import grade  # noqa: E402

REPO = SERVER.parent


def main() -> None:
    pairs = json.loads((REPO / "artifacts/model-comparison/pairs.json").read_text())
    cases = json.loads((SERVER / "evals/library/cases.yaml").read_text())
    by_id = {case["id"]: case for case in cases}
    records = []
    for entry in pairs["results"]:
        if entry["suite"] != "library" or entry.get("setup_invalid") or not entry["reports"]:
            continue
        source = REPO / entry["reports"][0]
        original_bytes = source.read_bytes()
        original = json.loads(original_bytes)
        changed = []
        new_support = []
        for result in original["results"]:
            if "grade" not in result:
                continue
            turn = result["turns"][-1]
            updated = grade(
                by_id[result["id"]],
                turn["message"]["content"],
                turn["sources"],
                turn["raw_answer"],
            )
            if result["kind"] != "absent":
                new_support.append(updated["citation_support"])
            if updated != result["grade"]:
                changed.append(
                    {"id": result["id"], "original": result["grade"], "regrade": updated}
                )
        assert source.read_bytes() == original_bytes
        records.append(
            {
                "label": entry["label"],
                "original_report": entry["reports"][0],
                "original_sha256": hashlib.sha256(original_bytes).hexdigest(),
                "original_support": original["metrics"]["citation_support"],
                "regraded_support": sum(new_support) / len(new_support),
                "changes": changed,
            }
        )
    output = REPO / "artifacts/reliability/library-regrades-v3.json"
    with output.open("x") as file:
        file.write(
            json.dumps(
                {
                    "grader": "Local post-period binding v3, no row/link citation leakage",
                    "grader_sha256": hashlib.sha256(
                        (SERVER / "evals/library/citation_binding.py").read_bytes()
                    ).hexdigest(),
                    "originals_unchanged": True,
                    "not_a_semantic_claim_review": True,
                    "records": records,
                },
                indent=2,
            )
            + "\n"
        )
    print(
        json.dumps(
            [{k: r[k] for k in ("label", "original_support", "regraded_support")} for r in records]
        )
    )


if __name__ == "__main__":
    main()
