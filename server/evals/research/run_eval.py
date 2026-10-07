"""Isolated 8A Research evaluation against the unchanged 8-0 recorded corpus."""

import argparse
import asyncio
import dataclasses
import hashlib
import json
import math
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from time import monotonic

import httpx

SERVER = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SERVER))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from regrade import cases, facts  # noqa: E402

from app.config import Settings  # noqa: E402
from app.main import create_app  # noqa: E402
from app.providers.base import ToolCall  # noqa: E402
from app.runs.research import PROMPT, arguments  # noqa: E402
from app.search.citations import cited  # noqa: E402
from app.search.fixtures import Fixtures  # noqa: E402
from app.search.providers import Providers  # noqa: E402

ROOT = SERVER.parent
OUT = ROOT / "artifacts/phase-8/8a/eval"
CORPUS = ROOT / "artifacts/phase-8/gate/web-fixtures"


async def evaluate(args):
    OUT.mkdir(parents=True, exist_ok=True)
    hashes = {
        str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
        for folder in (SERVER / "app", ROOT / "server/evals/research")
        for p in folder.rglob("*")
        if p.is_file() and p.suffix in {".py", ".json", ".yaml"}
    }
    (OUT / "inputs.json").write_text(json.dumps(hashes, indent=2) + "\n")
    rows = cases()
    original_search = Providers.search
    results = []
    with tempfile.TemporaryDirectory(prefix="workbench-research-eval-") as directory:
        app = create_app(Settings(data_dir=Path(directory), research=True, dev=True))
        async with (
            app.router.lifespan_context(app),
            httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://localhost", timeout=None
            ) as client,
        ):
            conn = (
                await client.post("/api/connections", json={"base_url": "http://127.0.0.1:11434"})
            ).json()["id"]
            model = next(
                m for m in (await client.get("/api/models")).json() if m["model_id"] == args.model
            )
            await client.patch(
                "/api/settings",
                json={
                    "auto_title": False,
                    "web.provider_order": ["ollama", "searxng", "exa", "ddgs"],
                },
            )
            adapter = await app.state.registry.adapter(conn)
            original_payload = adapter.payload
            original_stream = adapter.stream
            for case in rows:
                fixture_dir = CORPUS / case["id"] / "0"
                saved = json.loads((fixture_dir / "run.json").read_text())["web"]
                fixture = Fixtures(fixture_dir)
                batches = []
                for q in saved.get("queries", []):
                    for provider in ("ollama", "searxng", "exa", "ddgs"):
                        try:
                            batch = fixture.search(provider, q, saved.get("freshness", "any"))
                        except (ValueError, FileNotFoundError):
                            continue
                        if batch:
                            batches.append(batch)
                            break

                async def frozen(self, queries, freshness, found=batches):
                    return found, []

                Providers.search = frozen
                app.state.research.fixtures = fixture
                captures = []
                events = []

                def payload(req, saved=captures):
                    body = original_payload(req)
                    saved.append(body)
                    return body

                async def stream(req, saved=events):
                    collected = []
                    async for event in original_stream(req):
                        collected.append(
                            {"type": type(event).__name__, **dataclasses.asdict(event)}
                        )
                        yield event
                    saved.append(collected)

                adapter.payload, adapter.stream = payload, stream
                chat = (
                    await client.post(
                        "/api/chats", json={"connection_id": conn, "model_id": args.model}
                    )
                ).json()
                clock = monotonic()
                reply = await client.post(
                    "/api/chats/" + chat["id"] + "/messages",
                    json={"content": case["turns"][0]["user"], "research": True},
                )
                if reply.status_code != 202:
                    raise RuntimeError(reply.text)
                run = app.state.runs.runs[reply.json()["run_id"]]
                await run.task
                elapsed = (monotonic() - clock) * 1000
                detail = (await client.get("/api/chats/" + chat["id"])).json()
                sources = detail["sources"].get(run.message.id, [])
                valid = []
                for batch in events:
                    for event in batch:
                        if event["type"] == "ToolCall":
                            try:
                                arguments(ToolCall(event["id"], event["name"], event["arguments"]))
                                valid.append(True)
                            except (ValueError, TypeError):
                                valid.append(False)
                info = run.message.research
                assert info is not None
                exceeded = (
                    info.steps > 8 or info.searches > 4 or info.pages > 8 or len(captures) > 9
                )
                citations = cited(run.message.content)
                result = {
                    "id": case["id"],
                    "required_facts": facts(run.message.content, case),
                    "citations_valid": bool(citations) and citations <= {s["n"] for s in sources},
                    "minimum_citations": len(citations) >= case["expect"]["min_citations"],
                    "status": run.message.status,
                    "error": run.message.error.model_dump() if run.message.error else None,
                    "message": run.message.model_dump(),
                    "sources": sources,
                    "reads": detail["reads"].get(run.message.id, []),
                    "calls": len(captures),
                    "tool_calls": len(valid),
                    "valid_tool_calls": sum(valid),
                    "host_refused_tool_calls": info.invalid_calls,
                    "budget_exceeded": exceeded,
                    "total_ms": elapsed,
                    "captured_requests": captures,
                    "provider_events": events,
                }
                results.append(result)
                (OUT / (case["id"] + ".json")).write_text(
                    json.dumps(result, indent=2, ensure_ascii=False) + "\n"
                )
                print(
                    case["id"],
                    "FACT PASS" if result["required_facts"] else "FACT MISS",
                    info.steps,
                    "steps",
                    round(elapsed / 1000, 1),
                    "s",
                    flush=True,
                )
            adapter.payload, adapter.stream = original_payload, original_stream
    Providers.search = original_search
    times = sorted(r["total_ms"] / 1000 for r in results)
    complete = sum(r["required_facts"] for r in results)
    metrics = {
        "required_facts_cases": complete,
        "total_cases": len(results),
        "factual_completeness": complete / len(results),
        "baseline_factual_completeness": 10 / 15,
        "gain_percentage_points": 100 * (complete / len(results) - 10 / 15),
        "fact_target": complete >= 13,
        "citations_valid": all(r["citations_valid"] for r in results),
        "min_citations": all(r["minimum_citations"] for r in results),
        "schema_valid_tool_fraction": sum(r["valid_tool_calls"] for r in results)
        / max(1, sum(r["tool_calls"] for r in results)),
        "valid_tool_fraction": max(
            0,
            1
            - sum(r["host_refused_tool_calls"] for r in results)
            / max(1, sum(r["tool_calls"] for r in results)),
        ),
        "validity_definition": (
            "Native schema plus host policy acceptance; ordinary page availability "
            "failures are retained but are not invalid calls. Earlier reports use "
            "schema-only validity; see tool-validity-adjudication.json."
        ),
        "budgets_exceeded": any(r["budget_exceeded"] for r in results),
        "max_model_calls": max(r["calls"] for r in results),
        "median_seconds": times[len(times) // 2],
        "p90_seconds": times[math.ceil(0.9 * len(times)) - 1],
        "manual_claim_and_citation_review": (
            "pending; regex/numeric validity are not semantic support certification"
        ),
    }
    report = {
        "recorded_at": datetime.now(UTC).isoformat(),
        "model": model,
        "mode": "offline frozen corpus, real native tool loop",
        "corpus": (
            "Same per-case 8-0 search results/pages; query-independent replay "
            "like the saved Search baseline"
        ),
        "prompt_sha256": hashlib.sha256(PROMPT.encode()).hexdigest(),
        "grading_revision": 2,
        "sampling_overrides": {},
        "metrics": metrics,
        "results": results,
    }
    (OUT / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(metrics, indent=2), flush=True)
    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument(
        "--live", action="store_true", help="Live Research eval is an 8B release gate."
    )
    parser.add_argument("--model", default="qwen3:30b-a3b-workbench-32k")
    config = parser.parse_args()
    if config.live:
        parser.error("8A uses the frozen 8-0 corpus; live qualification is separately gated at 8B.")
    result = asyncio.run(evaluate(config))
    passed = (
        result["fact_target"]
        and result["citations_valid"]
        and result["min_citations"]
        and result["valid_tool_fraction"] >= 0.95
        and not result["budgets_exceeded"]
        and result["max_model_calls"] <= 9
        and result["median_seconds"] <= 90
        and result["p90_seconds"] <= 200
    )
    sys.exit(0 if passed else 1)
