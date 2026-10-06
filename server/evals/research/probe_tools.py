"""8-0 native Ollama protocol probe; no product changes or tool execution."""

import asyncio
import hashlib
import json
from pathlib import Path
from time import monotonic
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUT = ROOT / "artifacts/phase-8/gate"


def validate(call: Any, schemas: dict[str, Any]) -> tuple[bool, str]:
    if not isinstance(call, dict) or not isinstance(call.get("function"), dict):
        return False, "missing_function"
    function = call["function"]
    name = function.get("name")
    if not isinstance(name, str) or name not in schemas:
        return False, "unknown_tool"
    arguments = function.get("arguments")
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except (TypeError, ValueError):
            return False, "invalid_json"
    if not isinstance(arguments, dict):
        return False, "arguments_not_object"
    schema = schemas[name]
    if set(schema.get("required", [])) - arguments.keys():
        return False, "missing_required"
    if set(arguments) - schema["properties"].keys():
        return False, "extra_argument"
    for key, value in arguments.items():
        rule = schema["properties"][key]
        if not isinstance(value, str):
            return False, "argument_type"
        if not value.strip() or len(value) > rule.get("maxLength", 100000):
            return False, "argument_length"
        if "enum" in rule and value not in rule["enum"]:
            return False, "argument_enum"
    return True, "valid"


async def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cases = json.loads((HERE / "probe_cases.json").read_text())
    tools = json.loads((HERE / "tools.json").read_text())
    assert len(cases) == 40 and len({c["id"] for c in cases}) == 40
    models = json.loads((OUT / "model-inventory.json").read_text())
    urls = json.loads((OUT / "runtime-endpoints.json").read_text())
    assert urls == ["http://127.0.0.1:11434"]
    eligible = [m for m in models if m["tools"] and m["chat_capable"]]
    # Default first is an execution order, not a capability inference.
    async with httpx.AsyncClient(timeout=30) as app:
        bootstrap = (await app.get("http://127.0.0.1:8787/api/bootstrap")).json()
        default = bootstrap["settings"].get("default_model_id")
    eligible.sort(key=lambda m: m["model_id"] != default)
    schemas = {t["function"]["name"]: t["function"]["parameters"] for t in tools}
    report: dict[str, Any] = {
        "threshold": 0.95,
        "prompts_per_model": 40,
        "cases_sha256": hashlib.sha256((HERE / "probe_cases.json").read_bytes()).hexdigest(),
        "tools_sha256": hashlib.sha256((HERE / "tools.json").read_bytes()).hexdigest(),
        "daily_model_candidate": default,
        "criterion": (
            "A prompt succeeds only if at least one native call is emitted and every call "
            "has a known name and schema-valid arguments. Missing calls count as failures. "
            "No prose parsing, repairs or retries."
        ),
        "models": [],
        "excluded": [
            {"model_id": m["model_id"], "reason": "runtime reports no chat completion capability"}
            for m in models
            if m["tools"] and not m["chat_capable"]
        ],
    }
    async with httpx.AsyncClient(timeout=httpx.Timeout(120, connect=10)) as client:
        for ordinal, model in enumerate(eligible):
            folder = OUT / "provider-fixtures" / str(ordinal)
            folder.mkdir(parents=True, exist_ok=True)
            rows = []
            for case in cases:
                payload = {
                    "model": model["model_id"],
                    "stream": True,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "Use the supplied native tools when requested. "
                                "Do not simulate calls in text. This is an isolated protocol "
                                "test with synthetic inputs."
                            ),
                        },
                        *case["messages"],
                    ],
                    "tools": tools,
                    "options": {**model["params_defaults"], "num_ctx": model["context_length"]},
                }
                (folder / (case["id"] + ".request.json")).write_text(
                    json.dumps(payload, indent=2) + "\n"
                )
                calls = []
                completed = False
                failure = None
                started = monotonic()
                try:
                    async with asyncio.timeout(120):
                        async with client.stream(
                            "POST", urls[0] + "/api/chat", json=payload
                        ) as response:
                            with (folder / (case["id"] + ".ndjson")).open("w") as wire:
                                async for line in response.aiter_lines():
                                    if not line:
                                        continue
                                    wire.write(line + "\n")
                                    chunk = json.loads(line)
                                    if chunk.get("error"):
                                        failure = "runtime_error"
                                    calls.extend(chunk.get("message", {}).get("tool_calls", []))
                                    completed |= bool(chunk.get("done"))
                            response.raise_for_status()
                except (TimeoutError, httpx.HTTPError, ValueError) as exc:
                    failure = type(exc).__name__
                judgments = [validate(c, schemas) for c in calls]
                valid = completed and not failure and bool(calls) and all(v for v, _ in judgments)
                names = [c.get("function", {}).get("name") for c in calls if isinstance(c, dict)]
                rows.append(
                    {
                        "id": case["id"],
                        "valid": valid,
                        "done": completed,
                        "failure": failure,
                        "calls": calls,
                        "validation": judgments,
                        "requested_tool": case["expected_tool"],
                        "requested_tool_called": case["expected_tool"] in names,
                        "elapsed_ms": (monotonic() - started) * 1000,
                    }
                )
                print(model["model_id"], case["id"], "PASS" if valid else "FAIL", flush=True)
            fraction = sum(r["valid"] for r in rows) / 40
            item = {
                "model_id": model["model_id"],
                "fixture_folder": str(folder.relative_to(ROOT)),
                "valid_prompts": sum(r["valid"] for r in rows),
                "fraction": fraction,
                "emitted_calls": sum(len(r["calls"]) for r in rows),
                "requested_tool_prompts": sum(r["requested_tool_called"] for r in rows),
                "passes": fraction >= 0.95,
                "cases": rows,
            }
            report["models"].append(item)
            (OUT / "tool-probe.json").write_text(json.dumps(report, indent=2) + "\n")
    report["daily_model_passes"] = any(
        m["model_id"] == default and m["passes"] for m in report["models"]
    )
    (OUT / "tool-probe.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    asyncio.run(main())
