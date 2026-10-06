"""Verify saved native streams and derive per-tool statistics, without inference."""

import hashlib
import json
from collections import Counter
from statistics import median

from probe_tools import HERE, OUT, ROOT, validate


def main() -> None:
    report = json.loads((OUT / "tool-probe.json").read_text())
    tools = json.loads((HERE / "tools.json").read_text())
    cases_by_id = {case["id"]: case for case in json.loads((HERE / "probe_cases.json").read_text())}
    inventory = {
        model["model_id"]: model for model in json.loads((OUT / "model-inventory.json").read_text())
    }
    schemas = {t["function"]["name"]: t["function"]["parameters"] for t in tools}
    for filename, field in [("tools.json", "tools_sha256"), ("probe_cases.json", "cases_sha256")]:
        assert hashlib.sha256((HERE / filename).read_bytes()).hexdigest() == report[field]
    models = []
    shapes: Counter[str] = Counter()
    for model in report["models"]:
        folder = ROOT / model["fixture_folder"]
        assert len(model["cases"]) == 40
        for case in model["cases"]:
            request = json.loads((folder / (case["id"] + ".request.json")).read_text())
            assert request["model"] == model["model_id"] and request["stream"] is True
            assert request["tools"] == tools
            assert request["messages"][1:] == cases_by_id[case["id"]]["messages"]
            runtime = inventory[model["model_id"]]
            assert request["options"] == {
                **runtime["params_defaults"],
                "num_ctx": runtime["context_length"],
            }
            chunks = [
                json.loads(line)
                for line in (folder / (case["id"] + ".ndjson")).read_text().splitlines()
            ]
            calls = [
                call for chunk in chunks for call in chunk.get("message", {}).get("tool_calls", [])
            ]
            assert calls == case["calls"]
            assert any(chunk.get("done") for chunk in chunks) == case["done"]
            judgments = [validate(call, schemas) for call in calls]
            expected = (
                case["done"]
                and not case["failure"]
                and bool(calls)
                and all(v for v, _ in judgments)
            )
            assert bool(expected) == case["valid"]
            for call in calls:
                function = call["function"]
                shapes[type(function["arguments"]).__name__] += 1
                shapes["nested_index" if "index" in function else "no_nested_index"] += 1
                shapes["call_id" if "id" in call else "no_call_id"] += 1
        groups = {}
        for tool in schemas:
            cases = [c for c in model["cases"] if c["requested_tool"] == tool]
            groups[tool] = {"valid": sum(c["valid"] for c in cases), "total": len(cases)}
        times = sorted(c["elapsed_ms"] for c in model["cases"])
        models.append(
            {
                "model_id": model["model_id"],
                "valid": model["valid_prompts"],
                "total": 40,
                "passes": model["passes"],
                "requested_tool": model["requested_tool_prompts"],
                "by_tool": groups,
                "median_ms": median(times),
                "p90_ms": times[35],
            }
        )
    result = {
        "threshold": report["threshold"],
        "daily_model": report["daily_model_candidate"],
        "daily_model_passes": report["daily_model_passes"],
        "models": models,
        "wire_shapes": dict(shapes),
        "raw_streams_verified": sum(len(m["cases"]) for m in report["models"]),
        "repairs_or_retries": 0,
        "scope": (
            "Strict schema/protocol success only; no tools executed and no agent accuracy measured."
        ),
    }
    (OUT / "tool-probe-summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
