"""Approved synthetic everyday comparison through the existing chat pipeline."""

import argparse
import asyncio
import hashlib
import json
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from app.config import Settings  # noqa: E402
from app.main import create_app  # noqa: E402
from app.providers.base import ReasoningDelta, TextDelta  # noqa: E402
from app.runs import context  # noqa: E402

REPO = ROOT.parent
CASES = REPO / "docs/model-comparison/everyday-cases.json"
OUTPUT = REPO / "artifacts/model-comparison"


def format_check(identifier: str, text: str) -> bool | None:
    """Only check the explicitly requested smoke JSON; all facts need review."""
    if identifier != "E05":
        return None
    try:
        value = json.loads(text)
    except ValueError:
        return False
    return (
        isinstance(value, dict)
        and set(value) == {"item", "quantity", "confirmed"}
        and isinstance(value["item"], str)
        and value["item"].casefold() == "notebooks"
        and type(value["quantity"]) in (int, float)
        and value["quantity"] == 4
        and value["confirmed"] is True
    )


async def evaluate(args: argparse.Namespace) -> None:
    document = CASES.read_bytes()
    cases = json.loads(document)["cases"]
    if args.case:
        cases = [c for c in cases if c["id"] == args.case]
    if not cases:
        raise ValueError("Unknown case")
    output = Path(args.output)
    if output.exists():
        raise ValueError("Never overwrite a previous trial")
    output.parent.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    report: dict[str, Any] = {
        "started_utc": datetime.now(UTC).isoformat(),
        "synthetic_only": True,
        "model": args.model,
        "label": args.label,
        "context_length": 32768,
        "cases_sha256": hashlib.sha256(document).hexdigest(),
        "source_hashes": {
            str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (ROOT / "app").rglob("*.py")
        },
        "effective_context_module": {
            "path": context.__file__,
            "sha256": hashlib.sha256(Path(context.__file__).read_bytes()).hexdigest(),
        },
        "new_sampling_values": {},
        "results": results,
        "manual_review_required": True,
        "limitations": (
            "Timings observed in the existing adapter stream; no polling or model judge. "
            "Ordinary chat paths with empty temporary preferences; actual params/payloads "
            "retained. First visible text differs from first reasoning delta. "
            "No overall accuracy pass is automatic."
        ),
    }
    logging.disable(logging.CRITICAL)
    try:
        with TemporaryDirectory(prefix="atelier-everyday-") as directory:
            app = create_app(Settings(data_dir=Path(directory), dev=True))
            async with (
                app.router.lifespan_context(app),
                httpx.AsyncClient(
                    transport=httpx.ASGITransport(app=app),
                    base_url="http://localhost",
                    timeout=None,
                ) as client,
            ):
                connection = await client.post("/api/connections", json={"base_url": args.url})
                connection.raise_for_status()
                conn = connection.json()["id"]
                response = await client.patch("/api/settings", json={"auto_title": False})
                response.raise_for_status()
                adapter = await app.state.registry.adapter(conn)
                models = await adapter.list_models()
                model = next(m for m in models if m.model_id == args.model)
                assert model.chat_capable and model.context_limit == 32768, model
                report["runtime_model_metadata"] = model.model_dump()
                observed: dict[str, Any] = {}
                original = adapter.stream

                async def capture(request: Any):
                    payload = adapter.payload(request)
                    assert payload.get("options") == {"num_ctx": 32768}, payload
                    observed["payload"] = payload
                    async for event in original(request):
                        clock = monotonic()
                        if isinstance(event, (TextDelta, ReasoningDelta)):
                            observed.setdefault("first_delta_ms", (clock - case_start) * 1000)
                        if isinstance(event, TextDelta):
                            observed.setdefault(
                                "first_visible_text_ms", (clock - case_start) * 1000
                            )
                        yield event

                adapter.stream = capture
                for case in cases:
                    observed = {}
                    created = await client.post(
                        "/api/chats", json={"connection_id": conn, "model_id": args.model}
                    )
                    created.raise_for_status()
                    chat = created.json()["id"]
                    case_start = monotonic()
                    submitted = await client.post(
                        f"/api/chats/{chat}/messages", json={"content": case["prompt"]}
                    )
                    submitted.raise_for_status()
                    run = app.state.runs.runs[submitted.json()["run_id"]]
                    try:
                        async with asyncio.timeout(600):
                            await run.task
                    except TimeoutError as exc:
                        await app.state.runs.cancel(run.id)
                        raise RuntimeError(
                            "Everyday case exceeded the isolated 600-second wall budget"
                        ) from exc
                    result = {
                        "id": case["id"],
                        "prompt": case["prompt"],
                        "manual_checks": case["manual_checks"],
                        "message": run.message.model_dump(),
                        "observed": observed,
                        "explicit_json_format": format_check(case["id"], run.message.content),
                    }
                    results.append(result)
                    output.write_text(json.dumps(report, indent=2) + "\n")
                    print(
                        json.dumps(
                            {
                                "id": case["id"],
                                "status": run.message.status,
                                "first_visible_text_ms": observed.get("first_visible_text_ms"),
                                "json_format": result["explicit_json_format"],
                            }
                        ),
                        flush=True,
                    )
                    if run.message.status != "complete":
                        raise RuntimeError("Protocol/completion failure; retained outcome")
                    if args.case == "E05" and result["explicit_json_format"] is False:
                        raise RuntimeError("Smoke JSON failure; no further smoke calls")
    except BaseException as exc:
        report["execution_error"] = str(exc)
        raise
    finally:
        report["finished_utc"] = datetime.now(UTC).isoformat()
        output.write_text(json.dumps(report, indent=2) + "\n")
        logging.disable(logging.NOTSET)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--url", default="http://127.0.0.1:11434")
    parser.add_argument("--case", default="")
    parser.add_argument("--label", required=True)
    parser.add_argument("--output", required=True)
    asyncio.run(evaluate(parser.parse_args()))
