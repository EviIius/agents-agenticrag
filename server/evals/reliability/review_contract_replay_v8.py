"""Separate grading diagnostics for host replay; never alter a retained model report."""

import hashlib
import json
import sys
from pathlib import Path

SERVER = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SERVER))
from evals.library.run_eval import grade  # noqa: E402

REPO = SERVER.parent
FOLDER = REPO / "artifacts/reliability/evidence-v8"
ORIGINAL = SERVER / "evals/library/reports/2026-10-09-151353-full.json"


def main() -> None:
    original_bytes = ORIGINAL.read_bytes()
    original = json.loads(original_bytes)
    replay = json.loads((FOLDER / "host-replay.json").read_text())
    library = iter(r for r in replay["results"] if r["suite"] == "library")
    cases = {
        case["id"]: case for case in json.loads((SERVER / "evals/library/cases.yaml").read_text())
    }
    results = []
    for result in original["results"]:
        updates = []
        for turn in result["turns"]:
            retained = next(library)
            assert retained["question"] == turn["question"], "Replay turn order changed"
            assert retained["before"]["content"] == turn["raw_answer"], "Original answer changed"
            after = retained["after"]["content"]
            updated = grade(cases[result["id"]], after, turn["sources"], after)
            updates.append({"question": turn["question"], "after_content": after, "grade": updated})
        results.append(
            {
                "id": result["id"],
                "kind": result["kind"],
                "original_grade": result["grade"],
                "replay_turns": updates,
            }
        )
    assert next(library, None) is None, "Extra replay turns"
    assert ORIGINAL.read_bytes() == original_bytes
    answerable = [r for r in results if r["kind"] != "absent"]
    passed = sum(
        r["replay_turns"][-1]["grade"]["facts_all"]
        and r["replay_turns"][-1]["grade"]["citation_support"]
        for r in answerable
    )
    output = {
        "scope": (
            "Host-only formatting diagnostic of unchanged selections; "
            "not new inference or a semantic review."
        ),
        "qualification": False,
        "original_report": str(ORIGINAL.relative_to(REPO)),
        "original_sha256": hashlib.sha256(original_bytes).hexdigest(),
        "replay_sha256": hashlib.sha256((FOLDER / "host-replay.json").read_bytes()).hexdigest(),
        "grader_hashes": {
            str(p.relative_to(REPO)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (
                SERVER / "evals/library/run_eval.py",
                SERVER / "evals/library/citation_binding.py",
                SERVER / "evals/library/cases.yaml",
            )
        },
        "originals_unchanged": True,
        "answerable_cases": len(answerable),
        "final_turn_fact_and_citation_passes": passed,
        "results": results,
    }
    with (FOLDER / "library-rendering-diagnostic.json").open("x") as file:
        json.dump(output, file, indent=2)
        file.write("\n")
    print(
        passed,
        "/",
        len(answerable),
        "final-turn facts/citations after host replay; release gates remain failed",
    )


if __name__ == "__main__":
    main()
