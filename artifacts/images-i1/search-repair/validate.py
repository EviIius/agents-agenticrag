"""Validate fixture extraction and experiment declarations without inference."""

import ast
import asyncio
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "server")]
import httpx  # noqa: E402

from app.providers.ollama import Ollama  # noqa: E402
from app.search.chunk import chunk  # noqa: E402
from app.search.extract import extract  # noqa: E402
from app.search.fixtures import Fixtures  # noqa: E402


async def preflight():
    async with httpx.AsyncClient(timeout=15, trust_env=False) as client:
        health = await client.get("http://127.0.0.1:8787/api/health")
        runs = await client.get("http://127.0.0.1:8787/api/runs/active")
        audio = await client.get("http://127.0.0.1:8787/api/transcription/audio-storage")
        runtime = await client.get("http://127.0.0.1:11434/api/version")
        for response in (health, runs, audio, runtime):
            response.raise_for_status()
        assert not runs.json() and not audio.json()["active_files"]
        assert runtime.json()["version"] == "0.35.0"
    adapter = Ollama("synthetic-preflight", "http://127.0.0.1:11434")
    try:
        models = await adapter.list_models()
        model = next(m for m in models if m.model_id == "qwen3:30b-a3b-instruct-2507-q4_K_M")
        assert model.chat_capable and model.context_length == 16384
        return {
            "live_health": True,
            "human_inference_active": False,
            "human_transcription_active": False,
            "runtime": runtime.json(),
            "selected_runtime_metadata": model.model_dump(),
            "model_calls": 0,
        }
    finally:
        await adapter.close()


def main():
    cases = json.loads((OUT / "cases.json").read_text())
    assert len(cases) == 24 and sum(c["split"] == "held_out" for c in cases) == 8
    assert len({c["turns"][0]["user"] for c in cases}) == 24
    rows = []
    for case in cases:
        for name in ("must_include", "must_not_match"):
            for pattern in case["expect"].get(name, []):
                re.compile(pattern, re.I)
        fixture = Fixtures(OUT / "fixtures" / case["id"] / "0")
        results = fixture.search("ddgs", "any synthetic query", "any")
        assert len(results) == 1
        page = extract(fixture.page(results[0].url))
        passages = chunk(page.url, page.text)
        if case.get("attack_marker"):
            assert any(case["attack_marker"] in passage.text for passage in passages)
        if case["expect"]["search"] and not case.get("rubric"):
            assert all(re.search(p, page.text, re.I) for p in case["expect"]["must_include"])
        rows.append(
            {
                "case": case["id"],
                "split": case["split"],
                "readable_chars": len(page.text),
                "extracted_text_sha256": hashlib.sha256(page.text.encode()).hexdigest(),
                "passages": len(passages),
                "attack_retained": bool(case.get("attack_marker")),
            }
        )
    for name in ("prepare.py", "experiment.py", "validate.py"):
        ast.parse((OUT / name).read_text())
    (OUT / "input-validation.json").write_text(
        json.dumps({"passed": True, "cases": rows}, indent=2) + "\n"
    )
    (OUT / "preflight.json").write_text(json.dumps(asyncio.run(preflight()), indent=2) + "\n")
    print(
        "Validated 24 extracted synthetic fixtures, regexes, held-out split and runtime metadata; "
        "no inference."
    )


if __name__ == "__main__":
    main()
