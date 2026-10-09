"""Separate parser regrades and old-selection host replay; no inference."""

import hashlib
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

SERVER = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SERVER))
from app.providers.base import ChatRequest, ProviderMessage  # noqa: E402
from evals.library import run_eval as library  # noqa: E402
from evals.reliability.evidence_contract_v11 import build, catalog, render  # noqa: E402
from evals.reliability.run_contract_v11 import verify  # noqa: E402

REPO = SERVER.parent
FOLDER = REPO / "artifacts/reliability/evidence-v11"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    verify()
    original_path = SERVER / "evals/library/reports/2026-10-09-151353-full.json"
    original = json.loads(original_path.read_text())
    cases = {c["id"]: c for c in json.loads((SERVER / "evals/library/cases.yaml").read_text())}
    replay_path = REPO / "artifacts/reliability/evidence-v10/host-replay.json"
    replay = iter(
        r for r in json.loads(replay_path.read_text())["results"] if r["suite"] == "library"
    )
    old_file = FOLDER / "before/citation_binding.py"
    spec = importlib.util.spec_from_file_location("retained_old_binding", old_file)
    assert spec and spec.loader
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    updated_binding = library.claim_units
    results = []
    for case in original["results"]:
        turns = []
        for turn in case["turns"]:
            retained = next(replay)
            assert retained["question"] == turn["question"]
            item: dict[str, Any] = {"question": turn["question"]}
            for label, answer in (
                ("original", turn["raw_answer"]),
                ("v10_host", retained["after"]["content"]),
            ):
                library.claim_units = old.claim_units
                before = library.grade(cases[case["id"]], answer, turn["sources"], answer)
                library.claim_units = updated_binding
                after = library.grade(cases[case["id"]], answer, turn["sources"], answer)
                assert before["facts"] == after["facts"], "Parser must not change fact presence"
                item[label] = {"before": before, "after": after, "answer": answer}
            turns.append(item)
        results.append({"id": case["id"], "kind": case["kind"], "turns": turns})
    assert next(replay, None) is None
    library.claim_units = updated_binding
    answerable = [r for r in results if r["kind"] != "absent"]
    totals = {
        label: {
            stage: sum(
                r["turns"][-1][label][stage]["facts_all"]
                and r["turns"][-1][label][stage]["citation_support"]
                for r in answerable
            )
            for stage in ("before", "after")
        }
        for label in ("original", "v10_host")
    }
    output = {
        "scope": (
            "Parser-only regrade of identical retained answers; "
            "no new inference or semantic qualification."
        ),
        "qualification": False,
        "answerable": len(answerable),
        "totals": totals,
        "hashes": {
            str(p.relative_to(REPO)): digest(p)
            for p in (
                original_path,
                replay_path,
                old_file,
                SERVER / "evals/library/citation_binding.py",
                SERVER / "evals/library/run_eval.py",
                SERVER / "evals/library/cases.yaml",
            )
        },
        "results": results,
    }
    with (FOLDER / "parser-regrade.json").open("x") as file:
        json.dump(output, file, indent=2)
        file.write("\n")
    print("Parser-only final-turn fact/citation totals:", totals, flush=True)
    outputs = []
    for suite in ("web", "library"):
        path = (
            REPO
            / "artifacts/reliability/evidence-v5"
            / ("baseline-" + suite + "-streams.jsonl-selections.jsonl")
        )
        for index, line in enumerate(path.read_text().splitlines()):
            retained = json.loads(line)
            question = json.loads(retained["payload"]["messages"][-1]["content"])["question"]
            sources = list(retained["source_snapshots"].values())
            available = catalog(sources, question)
            assert available.units == retained["unit_catalog"], "Original catalogue changed"
            raw = "".join(
                e["value"]["text"] for e in retained["raw_events"] if e["type"] == "TextDelta"
            )
            selection = json.loads(raw)
            units = {u["id"]: u for values in available.units.values() for u in values}
            converted = {
                "coverage": selection["coverage"],
                "selections": [
                    {
                        "id": identifier,
                        "columns": list(range(len(units[identifier]["header"])))
                        if units[identifier]["kind"] == "row"
                        else [],
                    }
                    for identifiers in selection["selections"].values()
                    for identifier in identifiers
                ],
            }
            after = render(json.dumps(converted), available)
            request = ChatRequest(
                "unused", [ProviderMessage("system", "Original"), ProviderMessage("user", question)]
            )
            build(request, sources)
            outputs.append(
                {
                    "suite": suite,
                    "index": index,
                    "question": question,
                    "source_path": str(path.relative_to(REPO)),
                    "source_sha256": digest(path),
                    "converted_same_fields": converted,
                    "before": retained["outcome"],
                    "after": after,
                    "old_payload_characters": len(retained["payload"]["messages"][-1]["content"]),
                    "new_payload_characters": len(request.messages[-1].content),
                }
            )
    output = {
        "scope": (
            "Unchanged v5 selections converted to v11 syntax, with every original "
            "column retained. Zero new inference; not a test of new column choices."
        ),
        "qualification": False,
        "results": outputs,
        "statuses": {
            suite: dict(Counter(r["after"]["status"] for r in outputs if r["suite"] == suite))
            for suite in ("web", "library")
        },
    }
    with (FOLDER / "host-replay.json").open("x") as file:
        json.dump(output, file, indent=2)
        file.write("\n")
    print("Host-only status totals:", output["statuses"], flush=True)
    verify()


if __name__ == "__main__":
    main()
