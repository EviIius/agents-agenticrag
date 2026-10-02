"""Real planner-only before/after checks using recorded conversation context."""

import asyncio
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from prompt_trials import INTENT_PROMPT, TASK_FIRST  # noqa: E402

from app.providers.base import ChatRequest, ProviderMessage  # noqa: E402
from app.providers.ollama import Ollama  # noqa: E402
from app.search import planner  # noqa: E402


class IntentTrial(Ollama):
    intent_trial = False

    async def complete_json(self, req: ChatRequest) -> dict:
        if not self.intent_trial:
            return await super().complete_json(req)
        req.json_schema = {
            **planner.SCHEMA,
            "required": ["task", "queries", "freshness"],
            "properties": {
                "task": {
                    "type": "string",
                    "enum": ["lookup", "transform", "creative", "calculate", "conversation"],
                },
                "queries": planner.SCHEMA["properties"]["queries"],
                "freshness": planner.SCHEMA["properties"]["freshness"],
            },
        }
        raw = await super().complete_json(req)
        task = raw.pop("task")
        if task != "lookup" and raw.get("queries"):
            raise ValueError("Non-lookup plan contains search queries")
        return {"search": task == "lookup", **raw}


async def main() -> None:
    cases = json.loads((Path(__file__).parent / "cases.yaml").read_text())
    original = planner.PROMPT
    model_id = "qwen3:30b-a3b-instruct-2507-q4_K_M"
    adapter = IntentTrial("planner-eval", "http://127.0.0.1:11434")
    models = await adapter.list_models()
    model = next(m for m in models if m.model_id == model_id)
    reports = []
    try:
        for name, prompt in [
            ("spec", original),
            ("task-first", TASK_FIRST),
            ("intent-first", INTENT_PROMPT),
        ]:
            adapter.intent_trial = name == "intent-first"
            planner.PROMPT = prompt
            rows = []
            for case in cases:
                history = []
                for index, turn in enumerate(case["turns"]):
                    result, fallback = await planner.plan(
                        adapter, model_id, turn["user"], history, True, model.context_length
                    )
                    expect = case["expect"]
                    expected = expect.get("search")
                    expected = expected[index] if isinstance(expected, list) else expected
                    decision = result.search == expected if isinstance(expected, bool) else None
                    scope = not any(
                        re.search(p, "\n".join(result.queries), re.I)
                        for p in expect.get("queries_must_not_match", [])
                    )
                    freshness = result.freshness in expect.get("freshness_in", [result.freshness])
                    rows.append(
                        {
                            "id": case["id"],
                            "turn": index,
                            "plan": result.model_dump(),
                            "fallback": fallback,
                            "decision_correct": decision,
                            "scope_correct": scope,
                            "freshness_correct": freshness,
                        }
                    )
                    history.append(ProviderMessage("user", turn["user"]))
                    if index + 1 < len(case["turns"]):
                        file = (
                            Path(__file__).parent
                            / "fixtures/2026-10-01-searxng"
                            / case["id"]
                            / str(index)
                            / "run.json"
                        )
                        history.append(
                            ProviderMessage(
                                "assistant", json.loads(file.read_text())["message"]["content"]
                            )
                        )
            decisions = [r["decision_correct"] for r in rows if r["decision_correct"] is not None]
            reports.append(
                {
                    "variant": name,
                    "prompt": prompt,
                    "decision_accuracy": sum(decisions) / len(decisions),
                    "scope_failures": [r["id"] for r in rows if not r["scope_correct"]],
                    "freshness_failures": [r["id"] for r in rows if not r["freshness_correct"]],
                    "rows": rows,
                }
            )
            print(
                json.dumps({k: v for k, v in reports[-1].items() if k not in ("rows", "prompt")}),
                flush=True,
            )
    finally:
        planner.PROMPT = original
        await adapter.close()
    file = (
        Path(__file__).parent
        / "reports"
        / (datetime.now(UTC).strftime("%Y-%m-%d-%H%M%S") + "-planner-task-first.json")
    )
    file.write_text(
        json.dumps(
            {
                "model": model_id,
                "real_runtime": True,
                "planner_only": True,
                "recorded_history": "2026-10-01-searxng",
                "reports": reports,
            },
            indent=2,
        )
    )
    print(file)


if __name__ == "__main__":
    asyncio.run(main())
