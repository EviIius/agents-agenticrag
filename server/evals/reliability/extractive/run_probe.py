"""One isolated answer per retained input, no planner/judge/retry or deployment."""

import argparse
import asyncio
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from time import monotonic

SERVER = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(SERVER))
from app.providers.base import ChatRequest, ProviderMessage, TextDelta  # noqa: E402
from app.providers.ollama import Ollama  # noqa: E402
from evals.models.run_comparison import get, verify_inputs  # noqa: E402
from evals.reliability.extractive.contract import PROMPT, schema, validate  # noqa: E402

REPO = SERVER.parent
FOLDER = REPO / "artifacts/reliability/extractive-v2"


async def main(model: str) -> None:
    manifest = json.loads((FOLDER / "manifest.json").read_text())
    for relative, expected in manifest["files"].items():
        if hashlib.sha256((REPO / relative).read_bytes()).hexdigest() != expected:
            raise RuntimeError("Frozen extractive probe changed")
    verify_inputs()
    output = FOLDER / (model.split(":")[0] + ".json")
    if output.exists():
        raise RuntimeError("Never overwrite or retry a retained probe")
    cases = json.loads((FOLDER / "inputs.json").read_text())
    results = []
    report = {
        "model": model,
        "started_utc": datetime.now(UTC).isoformat(),
        "manifest_sha256": hashlib.sha256((FOLDER / "manifest.json").read_bytes()).hexdigest(),
        "results": results,
        "limitation": "Exact provenance only; relevance and coverage require manual review.",
    }
    adapter = Ollama("isolated", "http://127.0.0.1:11434")
    try:
        actual = next(m for m in await adapter.list_models() if m.model_id == model)
        assert actual.context_limit == 32768
        report["metadata"] = actual.model_dump()
        for case in cases:
            if get("http://127.0.0.1:8787/api/runs/active"):
                raise RuntimeError("Human inference active; stop the probe")
            if get("http://127.0.0.1:8787/api/transcription/audio-storage")["active_files"]:
                raise RuntimeError("Human transcription active; stop the probe")
            data = json.dumps(case, ensure_ascii=False).replace("<", r"\u003c")
            request = ChatRequest(
                model,
                [ProviderMessage("system", PROMPT), ProviderMessage("user", data)],
                context_length=32768,
                json_schema=schema([s["n"] for s in case["sources"]]),
            )
            payload = adapter.payload(request)
            assert payload["options"] == {"num_ctx": 32768}
            started = monotonic()
            text = ""
            async with asyncio.timeout(600):
                async for event in adapter.stream(request):
                    if isinstance(event, TextDelta):
                        text += event.text
            result = {
                "id": case["id"],
                "payload": payload,
                "raw": text,
                "elapsed_ms": (monotonic() - started) * 1000,
            }
            try:
                result["accepted_excerpts"] = validate(text, case["sources"])
                result["exact_provenance_pass"] = True
            except (ValueError, TypeError) as exc:
                result["exact_provenance_pass"] = False
                result["rejection"] = str(exc)
            results.append(result)
            output.write_text(json.dumps(report, indent=2) + "\n")
            print(case["id"], result["exact_provenance_pass"], flush=True)
    finally:
        report["finished_utc"] = datetime.now(UTC).isoformat()
        output.write_text(json.dumps(report, indent=2) + "\n")
        await adapter.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    asyncio.run(main(parser.parse_args().model))
