"""Freeze one candidate/order and unchanged source/corpus before inference."""

import json
import subprocess
import sys
from pathlib import Path

import native

ROOT, OUT = native.ROOT, native.OUT
sys.path.insert(0, str(ROOT / "server"))
from app.search import planner, prompt


def tracked(*paths):
    return (
        subprocess.check_output(["git", "ls-files", "-z", "--", *paths], cwd=ROOT)
        .decode()
        .split("\0")[:-1]
    )


def main():
    cases = json.loads((ROOT / "server/evals/web/cases.yaml").read_text())
    case = next(c for c in cases if c["id"] == "nba-all-losses")
    native.write(
        "execution.json",
        {
            "approval": "Jake: Run the bounded answer comparison, 12 October 2026",
            "order": [
                ["pair1-baseline", "baseline"],
                ["pair1-candidate", "candidate"],
                ["pair2-candidate", "candidate"],
                ["pair2-baseline", "baseline"],
                ["pair3-baseline", "baseline"],
                ["pair3-candidate", "candidate"],
            ],
            "maximum": {"planners": 6, "answers": 6, "empty_message_warm_loads": 6},
            "model": native.MODEL,
            "context": 16384,
            "answer_params": {},
            "utility_params": {"temperature": 0.2, "max_tokens": 256},
            "utility_reasoning": "off",
            "answer_reasoning": "unset",
            "date": native.NOW.isoformat(),
            "case": case,
            "scope": "Current Search vs isolated original-table admission; "
            "one original question only",
            "stopping": "First candidate mandatory/support/citation failure "
            "or any protocol failure",
            "manual_review": "Every executed answer; candidate must pass before another child",
            "general_qualification": False,
            "deployment": False,
        },
    )
    native.write(
        "prompts.json",
        {
            "planner": planner.PROMPT,
            "answer": prompt.PROMPT,
            "request_bound_schema": planner.schema(case["turns"][0]["user"]),
        },
    )
    names = tracked("server/app", "server/evals/web", "server/pyproject.toml", "server/uv.lock")
    names += [str(p.relative_to(ROOT)) for p in OUT.glob("*.py")]
    names += [
        str((OUT / name).relative_to(ROOT))
        for name in ("execution.json", "prompts.json", "comparison.json")
    ]
    names += ["docs/SEARCH-TABLE-ANSWER-PROBE-PLAN.md", "docs/SEARCH-TABLE-ADMISSION-PLAN.md"]
    installed = Path.home() / ".local/share/workbench/app/server"
    matches = {}
    for name in [
        "app/search/planner.py",
        "app/search/prompt.py",
        "app/search/pipeline.py",
        "app/search/rank.py",
        "app/search/selection.py",
        "app/runs/context.py",
    ]:
        current, actual = native.digest(ROOT / "server" / name), native.digest(installed / name)
        assert current == actual, name
        matches[name] = current
    native.write(
        "manifest.json",
        {
            "base": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip(),
            "files": {name: native.digest(ROOT / name) for name in sorted(set(names))},
            "installed_search_and_context_source_matches": matches,
            "historical_reports_and_cases_unchanged": True,
            "no_inference_in_freezing": True,
        },
    )
    native.frozen()
    print(f"Frozen {len(set(names))} source/input files; installed Search/context identical")


if __name__ == "__main__":
    main()
