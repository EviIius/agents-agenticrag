"""Held-out planner decisions, original and frozen trial; no answer/judge call."""

import argparse
import asyncio
import hashlib
import importlib.util
import inspect
import json
import sys
from pathlib import Path

SERVER = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SERVER))
from app.providers.base import ProviderMessage  # noqa: E402
from app.providers.ollama import Ollama  # noqa: E402

REPO = SERVER.parent


async def main(model: str, version: str, repeat: int) -> None:
    path = (
        REPO / "artifacts/reliability/baseline/server/app/search/planner.py"
        if version == "original"
        else SERVER / "evals/reliability/trials" / version / "app/search/planner.py"
    )
    name = "app.search._repair_probe"
    if version != "original":
        import app.runs

        app.runs.__path__.insert(0, str(SERVER / "evals/reliability/trials" / version / "app/runs"))
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    data = (REPO / "docs/reliability/planner-cases.json").read_bytes()
    cases = json.loads(data)["cases"]
    suffix = "" if repeat == 1 else f"-r{repeat}"
    output = (
        REPO / "artifacts/reliability" / f"planner-{version}-{model.split(':')[0]}{suffix}.json"
    )
    if output.exists():
        raise RuntimeError("Never overwrite an original probe")
    records = []
    report = {
        "model": model,
        "version": version,
        "repeat": repeat,
        "cases_sha256": hashlib.sha256(data).hexdigest(),
        "module_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "results": records,
    }
    adapter = Ollama("isolated", "http://127.0.0.1:11434")
    actual = next(m for m in await adapter.list_models() if m.model_id == model)
    assert actual.context_limit == 32768
    report["model_metadata"] = actual.model_dump()
    original = adapter.complete_json
    captured = {}

    async def capture(request):
        captured["payload"] = adapter.payload(request)
        value = await original(request)
        captured["raw"] = value
        return value

    adapter.complete_json = capture
    try:
        for case in cases:
            captured = {}
            extras = (
                {"supplied_text": case["supplied_text"]}
                if "supplied_text" in inspect.signature(module.plan).parameters
                else {}
            )
            plan, fallback = await module.plan(
                adapter,
                model,
                case["latest"],
                [ProviderMessage(m["role"], m["content"]) for m in case["history"]],
                bool(actual.loaded),
                32768,
                **extras,
            )
            result = {
                "id": case["id"],
                "case": case,
                "plan": plan.model_dump(),
                "fallback": fallback,
                "decision_pass": plan.search == case["expect_search"] and not fallback,
                **captured,
            }
            records.append(result)
            output.write_text(json.dumps(report, indent=2) + "\n")
            print(case["id"], result["decision_pass"], plan.model_dump(), flush=True)
    finally:
        output.write_text(json.dumps(report, indent=2) + "\n")
        await adapter.client.aclose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--repeat", type=int, choices=(1, 2, 3), default=1)
    args = parser.parse_args()
    asyncio.run(main(args.model, args.version, args.repeat))
