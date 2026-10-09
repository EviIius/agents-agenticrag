"""Reconstruct retained page selection without network or inference."""

import hashlib
import json
import re
import sys
from pathlib import Path

SERVER = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SERVER))
from app.search.chunk import chunk  # noqa: E402
from app.search.extract import extract  # noqa: E402
from app.search.fixtures import Fixtures  # noqa: E402
from app.search.rank import rank, select  # noqa: E402
from evals.reliability.table_selection import prioritize_tables  # noqa: E402

REPO = SERVER.parent


def main() -> None:
    path = (
        SERVER
        / "evals/web/reports/2026-10-09-123938-qwen3-8-27b-atelier-eval-32k-offline-keyword.json"
    )
    report = json.loads(path.read_text())
    definitions = json.loads((SERVER / "evals/web/cases.yaml").read_text())
    case = next(c for c in report["results"] if c["id"] == "nba-all-losses")
    turn = case["turns"][0]
    fixture = Fixtures(SERVER / "evals/web/fixtures/phase2-final-corpus/nba-all-losses/0")
    # Same fetched page set; the n-order is the retained selected-source order.
    # This is an explicit counterfactual, not an exact full pipeline replay.
    urls = [s["url"] for s in turn["sources"]]
    passages = []
    raw_hashes = {}
    for url in urls:
        raw = fixture.page(url)
        assert raw
        raw_hashes[url] = hashlib.sha256(raw.data).hexdigest()
        passages.extend(chunk(url, extract(raw).text))
    ranked = rank(passages, " ".join(turn["message"]["web"]["queries"]), urls)
    before = select(ranked, 1500, 6)
    after = select(prioritize_tables(ranked, turn["question"]), 1500, 6)
    expected = next(c for c in definitions if c["id"] == "nba-all-losses")["expect"]["must_include"]

    def describe(groups):
        text = "\n".join(p.text for group in groups for p in group)
        return {
            "required_names_present": sum(bool(re.search(x, text, re.I)) for x in expected),
            "required_names_total": len(expected),
            "sources": len(groups),
            "passages": [[p.model_dump() for p in group] for group in groups],
        }

    out = {
        "source_report": str(path.relative_to(REPO)),
        "source_report_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "raw_page_sha256": raw_hashes,
        "selector_sha256": hashlib.sha256(
            Path(__file__).with_name("table_selection.py").read_bytes()
        ).hexdigest(),
        "budget": 1500,
        "maximum": 6,
        "before": describe(before),
        "after": describe(after),
        "limitations": (
            "Same fetched pages, selected-source n-order used as rank prior. "
            "No predicate filtering, model answer or qualification claim. "
            "Presence does not mean every row satisfies the request."
        ),
    }
    output = REPO / "artifacts/reliability/table-selection-probe.json"
    with output.open("x") as file:
        json.dump(out, file, indent=2)
        file.write("\n")
    print({k: {n: v for n, v in out[k].items() if n != "passages"} for k in ("before", "after")})


if __name__ == "__main__":
    main()
