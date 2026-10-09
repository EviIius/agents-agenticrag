"""Re-render retained model selections; no inference, retrieval or qualification claim."""

import hashlib
import json
import sys
from pathlib import Path

SERVER = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SERVER))
from evals.reliability.evidence_contract_v8 import catalog, render  # noqa: E402

REPO = SERVER.parent
FOLDER = REPO / "artifacts/reliability/evidence-v8"


def main() -> None:
    manifest = json.loads((FOLDER / "manifest.json").read_text())
    for name, expected in manifest["files"].items():
        if hashlib.sha256((REPO / name).read_bytes()).hexdigest() != expected:
            raise RuntimeError("Frozen host replay changed")
    result = {
        "scope": "Host-only replay of unchanged v5 raw selections; zero new model calls.",
        "qualification": False,
        "results": [],
    }
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
            assert available.units == retained["unit_catalog"], "Evidence units changed"
            raw = "".join(
                e["value"]["text"] for e in retained["raw_events"] if e["type"] == "TextDelta"
            )
            after = render(raw, available)
            result["results"].append(
                {
                    "suite": suite,
                    "index": index,
                    "question": question,
                    "input_path": str(path.relative_to(REPO)),
                    "input_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "before": retained["outcome"],
                    "after": after,
                }
            )
    with (FOLDER / "host-replay.json").open("x") as output:
        json.dump(result, output, indent=2, ensure_ascii=False)
        output.write("\n")
    print(len(result["results"]), "retained selections replayed; not a new model evaluation")


if __name__ == "__main__":
    main()
