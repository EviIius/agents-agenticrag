"""Validate fixed cases/extraction/hashes and runtime metadata without inference."""

import asyncio
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "server")]
from app.search.chunk import chunk  # noqa: E402
from app.search.extract import extract  # noqa: E402
from app.search.fixtures import Fixtures  # noqa: E402


def main():
    previous = OUT.parent / "search-repair-v2"
    spec = importlib.util.spec_from_file_location("previous_preflight", previous / "validate.py")
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    original = json.loads((OUT / "cases.json").read_text())
    additional = json.loads((OUT / "supplemental-cases.json").read_text())
    assert (OUT / "cases.json").read_bytes() == (previous / "cases.json").read_bytes()
    assert len(original) == 24 and len(additional) == 9
    assert sum(c["split"] == "held_out" for c in original) == 8
    assert sum(c["split"] == "held_out" for c in additional) == 4
    combined = json.loads((OUT / "boundary-cases.json").read_text())
    assert combined == original + additional
    rows = []
    for case in combined:
        fixture = Fixtures(OUT / "fixtures" / case["id"] / "0")
        results = fixture.search("ddgs", "any synthetic query", "any")
        page = extract(fixture.page(results[0].url))
        passages = chunk(page.url, page.text)
        for name in ("must_include", "must_not_match"):
            for pattern in case["expect"].get(name, []):
                re.compile(pattern, re.I)
        if case.get("attack_marker"):
            assert any(case["attack_marker"] in p.text for p in passages)
        rows.append(
            {
                "case": case["id"],
                "split": case["split"],
                "extracted_chars": len(page.text),
                "extracted_sha256": hashlib.sha256(page.text.encode()).hexdigest(),
                "passages": len(passages),
                "attack": bool(case.get("attack_marker")),
            }
        )
    declaration = json.loads((OUT / "execution.json").read_text())
    assert len(declaration["order"]) == 72 and declaration["boundary_end"] == 66
    (OUT / "input-validation.json").write_text(
        json.dumps({"passed": True, "cases": rows, "real_model_calls": 0}, indent=2) + "\n"
    )
    (OUT / "preflight.json").write_text(
        json.dumps(asyncio.run(helper.preflight()), indent=2) + "\n"
    )
    print("33 fixed synthetic cases/fixtures and runtime metadata verified; no inference.")


if __name__ == "__main__":
    main()
