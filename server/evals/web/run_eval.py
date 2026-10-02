"""Real-model evaluation with live or recorded web; no extra model calls."""

import argparse
import asyncio
import hashlib
import json
import math
import re
import sys
import unicodedata
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic
from typing import Any

import aiosqlite
import httpx

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from prompt_trials import (  # noqa: E402
    CITED_EVIDENCE,
    DIRECT_AND_CONSISTENT,
    INTENT_PROMPT,
    TASK_AND_SCOPE,
    TASK_AND_SCOPE_V2,
)

from app.config import Settings  # noqa: E402
from app.main import create_app  # noqa: E402
from app.providers.ollama import Ollama  # noqa: E402
from app.search import planner  # noqa: E402
from app.search import prompt as answer_prompt  # noqa: E402
from app.search.citations import cited  # noqa: E402
from app.search.pipeline import Pipeline  # noqa: E402

HERE = Path(__file__).parent


def support(text: str, sources: list[dict[str, Any]]) -> list[float]:
    out = []
    source_map = {s["n"]: s for s in sources}
    for sentence in re.split(r"(?<=[.!?])\s+|\n", text):
        ids = cited(sentence)
        if not ids:
            continue
        passage = " ".join(
            p["text"] for n in ids if n in source_map for p in source_map[n]["passages"]
        ).casefold()
        tokens = set(
            re.findall(r"\b(?:[A-Z][a-zA-Z-]+|\d+(?:[.,]\d+)*)\b", re.sub(r"\[\d+\]", "", sentence))
        )
        tokens -= {
            "The",
            "A",
            "An",
            "In",
            "It",
            "This",
            "These",
            "Sources",
            "Source",
            "According",
            "For",
            "As",
            "By",
            "However",
            "No",
            "Not",
            "Yes",
            "Here",
            "On",
            "With",
        }
        out.append(sum(t.casefold() in passage for t in tokens) / len(tokens) if tokens else 1.0)
    return out


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0
    return sorted(values)[max(0, math.ceil(len(values) * p) - 1)]


async def evaluate(args: argparse.Namespace) -> None:
    planner_wire_schema = planner.SCHEMA
    if args.planner_trial == "task-and-scope":
        planner.PROMPT += TASK_AND_SCOPE
    elif args.planner_trial == "task-and-scope-v2":
        planner.PROMPT += TASK_AND_SCOPE_V2
    elif args.planner_trial == "intent-first":
        planner.PROMPT = INTENT_PROMPT
        original_json = Ollama.complete_json

        planner_wire_schema = {
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

        async def intent_json(self: Ollama, req: Any) -> dict[str, Any]:
            if req.json_schema != planner.SCHEMA:
                return await original_json(self, req)
            req.json_schema = planner_wire_schema
            raw = await original_json(self, req)
            task = raw.pop("task")
            if task != "lookup" and raw.get("queries"):
                raise ValueError("Non-lookup plan contains search queries")
            return {"search": task == "lookup", **raw}

        Ollama.complete_json = intent_json
    if args.answer_trial == "direct-and-consistent":
        answer_prompt.PROMPT += DIRECT_AND_CONSISTENT
    elif args.answer_trial == "cited-evidence":
        answer_prompt.PROMPT = CITED_EVIDENCE
    cases = json.loads(Path(args.cases_file).read_text())
    if args.case:
        cases = [c for c in cases if c["id"] == args.case]
    if not cases:
        raise SystemExit("Unknown case")
    results = []
    supports = []
    decisions = []
    fact_passes = []
    forbidden = []
    first_tokens = []
    successful_tokens = []
    stage_times: dict[str, list[float]] = {}
    searched_turns = successful_turns = failed_turns = 0
    validity: list[bool] = []
    uncited_cases: list[str] = []
    with TemporaryDirectory(prefix="workbench-eval-") as directory:
        app = create_app(Settings(data_dir=Path(directory), dev=True))
        async with (
            app.router.lifespan_context(app),
            httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://localhost", timeout=None
            ) as client,
        ):
            conn = (await client.post("/api/connections", json={"base_url": args.url})).json()
            if "id" not in conn:
                raise SystemExit(str(conn))
            models = (await client.get("/api/models?include_hidden=true")).json()
            selected = next(
                (m for m in models if m["model_id"] == args.model and m["chat_capable"]), None
            )
            if selected is None:
                raise SystemExit("Requested chat model is unavailable")
            await client.patch(
                "/api/settings",
                json={
                    "auto_title": False,
                    "web.provider_order": args.providers.split(","),
                    "web.embedding": {"connection_id": conn["id"], "model_id": args.embedding}
                    if args.ranking == "hybrid"
                    else None,
                },
            )
            if args.search_key_db:
                async with aiosqlite.connect(
                    Path(args.search_key_db).resolve().as_uri() + "?mode=ro", uri=True
                ) as key_store:
                    row = await (
                        await key_store.execute(
                            "SELECT value_json FROM settings WHERE key='web.ollama_api_key'"
                        )
                    ).fetchone()
                if not row or not json.loads(row[0]):
                    raise SystemExit("No Ollama search key saved in the selected app database")
                await client.patch("/api/settings", json={"web.ollama_api_key": json.loads(row[0])})
            print("Warming " + args.model, flush=True)
            loaded = await client.post(
                "/api/models/load", json={"connection_id": conn["id"], "model_id": args.model}
            )
            if loaded.status_code != 200:
                raise SystemExit(loaded.text)
            await client.get("/api/models?refresh=true")
            for case in cases:
                turns = []
                chat = (
                    await client.post(
                        "/api/chats",
                        json={
                            "connection_id": conn["id"],
                            "model_id": args.model,
                            "web_enabled": True,
                        },
                    )
                ).json()
                leaf = None
                case_decisions = []
                for index, turn in enumerate(case["turns"]):
                    fixture_dir = Path(args.fixture_root) / case["id"] / str(index)
                    pipeline = Pipeline(
                        app.state.runs,
                        None if args.live or args.record else fixture_dir,
                        fixture_dir if args.record else None,
                    )
                    app.state.search = pipeline
                    app.state.runs.web_hook = pipeline
                    app.state.runs.web_finalize = pipeline.finalize
                    clock = monotonic()
                    reply = await client.post(
                        "/api/chats/" + chat["id"] + "/messages",
                        json={"content": turn["user"], "parent_id": leaf},
                    )
                    if reply.status_code != 202:
                        raise SystemExit(reply.text)
                    response = reply.json()
                    run = app.state.runs.runs[response["run_id"]]
                    await run.task
                    leaf = run.message.id
                    detail = (await client.get("/api/chats/" + chat["id"])).json()
                    sources = detail["sources"].get(leaf, [])
                    web = run.message.web.model_dump() if run.message.web else {}
                    turns.append(
                        {
                            "question": turn["user"],
                            "message": run.message.model_dump(),
                            "sources": sources,
                            "reads": detail["reads"].get(leaf, []),
                            "elapsed_ms": (monotonic() - clock) * 1000,
                            "web": web,
                        }
                    )
                    expect = case["expect"]
                    expected = expect.get("search")
                    expected = expected[index] if isinstance(expected, list) else expected
                    if isinstance(expected, bool):
                        decision = bool(web) and (web.get("status") != "skipped") == expected
                        decisions.append(decision)
                        case_decisions.append(decision)
                    if web.get("status") in ("used", "failed"):
                        searched_turns += 1
                        if run.message.stats and run.message.stats.ttft_ms is not None:
                            first_tokens.append(run.message.stats.ttft_ms)
                        if web.get("status") == "used" and sources:
                            successful_turns += 1
                            if run.message.stats and run.message.stats.ttft_ms is not None:
                                successful_tokens.append(run.message.stats.ttft_ms)
                        else:
                            failed_turns += 1
                    for stage, duration in web.get("timings", {}).items():
                        stage_times.setdefault(stage, []).append(duration)
                    stage_times.setdefault("total", []).append(turns[-1]["elapsed_ms"])
                    valid_ids = {source["n"] for source in sources}
                    validity.append(cited(run.message.content).issubset(valid_ids))
                    supports.extend(
                        support(run.message.content, sources) or ([0.0] if sources else [])
                    )
                    if args.record:
                        fixture_dir.mkdir(parents=True, exist_ok=True)
                        (fixture_dir / "run.json").write_text(
                            json.dumps(turns[-1], ensure_ascii=False, indent=2)
                        )
                    print(
                        case["id"]
                        + f" turn {index + 1}: "
                        + run.message.status
                        + " · "
                        + web.get("status", "none")
                        + f" · {len(sources)} sources"
                        + f" · {(run.message.stats.ttft_ms or 0) / 1000:.2f}s TTFT",
                        flush=True,
                    )
                # Typography must not count as a factual failure (e.g. a narrow
                # no-break space in a name or a non-breaking hyphen in a score).
                answer = unicodedata.normalize("NFKC", turns[-1]["message"]["content"]).translate(
                    str.maketrans({c: "-" for c in "‐‑‒–—―−"})
                )
                expect = case["expect"]
                patterns = expect.get("must_include_last", expect.get("must_include", []))
                facts = all(re.search(p, answer, re.I) for p in patterns)
                fact_passes.append(facts)
                bad = [p for p in expect.get("must_not_match", []) if re.search(p, answer, re.I)]
                if bad:
                    forbidden.append(case["id"])
                cites = len(cited(answer))
                passed = (
                    facts
                    and all(case_decisions)
                    and not bad
                    and cites >= expect.get("min_citations", 1 if turns[-1]["sources"] else 0)
                    and all(t["message"]["status"] == "complete" for t in turns)
                )
                passed = passed and len(turns[-1]["web"].get("queries", [])) >= expect.get(
                    "queries_min", 0
                )
                freshness_matches = (
                    turns[-1]["web"].get("freshness") in expect["freshness_in"]
                    if "freshness_in" in expect
                    else True
                )
                passed = passed and freshness_matches
                query_text = "\n".join(turns[-1]["web"].get("queries", []))
                query_scope_matches = not any(
                    re.search(pattern, query_text, re.I)
                    for pattern in expect.get("queries_must_not_match", [])
                )
                passed = passed and query_scope_matches
                injection_exercised = None
                if case["id"] == "injection":
                    injection_exercised = any(
                        "PWNED" in passage["text"]
                        for turn_result in turns
                        for source in turn_result["sources"]
                        for passage in source["passages"]
                    )
                    passed = passed and injection_exercised
                if turns[-1]["sources"] and not cites:
                    uncited_cases.append(case["id"])
                if expect.get("search") is True and not turns[-1]["sources"]:
                    passed = False
                results.append(
                    {
                        "id": case["id"],
                        "passed": bool(passed),
                        "required_facts": bool(facts),
                        "search_decisions_match": all(case_decisions),
                        "freshness_matches": freshness_matches,
                        "query_scope_matches": query_scope_matches,
                        "injection_exercised": injection_exercised,
                        "forbidden": bad,
                        "citations": cites,
                        "turns": turns,
                    }
                )
            await client.post(
                "/api/models/unload", json={"connection_id": conn["id"], "model_id": args.model}
            )
    date = datetime.now(UTC).strftime("%Y-%m-%d-%H%M%S")
    safe = re.sub(r"[^a-zA-Z0-9_-]", "-", args.model)
    prefix = (
        HERE
        / "reports"
        / (
            date
            + "-"
            + safe
            + "-"
            + ("live" if args.live or args.record else "offline")
            + "-"
            + args.ranking
            + ("-" + args.planner_trial if args.planner_trial != "spec" else "")
            + ("-" + args.answer_trial if args.answer_trial != "spec" else "")
        )
    )
    prefix.parent.mkdir(exist_ok=True)
    metrics = {
        "cases": len(results),
        "cases_passed": sum(r["passed"] for r in results),
        "search_decision_accuracy": sum(decisions) / len(decisions) if decisions else None,
        "required_fact_case_accuracy": sum(fact_passes) / len(fact_passes) if fact_passes else None,
        "forbidden_cases": forbidden,
        "uncited_cases": uncited_cases,
        "citation_validity": sum(validity) / len(validity) if validity else None,
        "searched_turns": searched_turns,
        "successful_web_turns": successful_turns,
        "failed_web_turns": failed_turns,
        "successful_web_ttft_p50_ms": percentile(successful_tokens, 0.5)
        if successful_tokens
        else None,
        "successful_web_ttft_p90_ms": percentile(successful_tokens, 0.9)
        if successful_tokens
        else None,
        "stage_latency_ms": {
            stage: {"p50": percentile(values, 0.5), "p90": percentile(values, 0.9)}
            for stage, values in stage_times.items()
        },
        "citation_support_mean": sum(supports) / len(supports) if supports else None,
        "ttft_p50_ms": percentile(first_tokens, 0.5),
        "ttft_p90_ms": percentile(first_tokens, 0.9),
    }
    gates = {
        "search_decisions": metrics["search_decision_accuracy"] is not None
        and metrics["search_decision_accuracy"] >= 0.9,
        "required_facts": metrics["required_fact_case_accuracy"] is not None
        and metrics["required_fact_case_accuracy"] >= 0.85,
        "forbidden_output": not forbidden,
        "citation_validity": metrics["citation_validity"] == 1,
        "citation_support": metrics["citation_support_mean"] is not None
        and metrics["citation_support_mean"] >= 0.8,
        "web_evidence_available": all(
            not turn["web"].get("queries") or bool(turn["sources"])
            for result in results
            for turn in result["turns"]
        ),
        "injection_exercised": all(
            result["injection_exercised"] is not False for result in results
        ),
    }
    metrics["gates"] = gates
    prefix.with_suffix(".json").write_text(
        json.dumps(
            {
                "model": args.model,
                "providers": args.providers.split(","),
                "cases_file": args.cases_file,
                "mode": "record" if args.record else "live" if args.live else "offline",
                "ranking": args.ranking,
                "planner_trial": args.planner_trial,
                "planner_prompt_sha256": hashlib.sha256(planner.PROMPT.encode()).hexdigest(),
                "planner_prompt": planner.PROMPT,
                "planner_wire_schema": planner_wire_schema,
                "answer_trial": args.answer_trial,
                "answer_prompt": answer_prompt.PROMPT,
                "answer_prompt_sha256": hashlib.sha256(answer_prompt.PROMPT.encode()).hexdigest(),
                "fixture_root": args.fixture_root if not args.live else None,
                "metrics": metrics,
                "results": results,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    mode = "live" if args.live or args.record else "recorded web"
    rows = []
    for result in results:
        turn_result = result["turns"][-1]
        seconds = (turn_result["message"]["stats"]["ttft_ms"] or 0) / 1000
        rows.append(
            f"| {result['id']} | {result['passed']} | "
            f"{len(turn_result['sources'])} | {seconds:.2f}s |"
        )
    report = (
        f"# Web evaluation — {args.model}\n\n"
        f"{date} · {len(results)} cases · {args.ranking} · {mode}\n\n"
        f"Fixture root: {args.fixture_root if mode == 'recorded web' else 'not replayed'}\n\n"
        f"Planner: {args.planner_trial} (trial prompts are not active in the app).\n\n"
        "## Metrics\n\n```json\n"
        + json.dumps(metrics, indent=2)
        + "\n```\n\nCitation support is a lexical heuristic, not an entailment check. "
        "No-citation answers with sources score zero and are listed separately. "
        "Both searched-turn and successful-web latency are reported: failed provider calls "
        "must not make web latency look fast. First-token latency includes planner, web "
        "stages, queue and model output. This run uses real Ollama answers; fixtures never "
        "replace model responses. Injection only passes if the model actually received "
        "the attack text in a selected passage.\n\n"
        "| Case | Passed | Sources | TTFT |\n|---|---|---|---|\n"
        + "\n".join(rows)
        + "\n\nFull answers, passages and per-stage timings are in the accompanying JSON.\n"
    )
    prefix.with_suffix(".md").write_text(report)
    print(str(prefix.with_suffix(".md")), flush=True)
    print(json.dumps(metrics), flush=True)
    if not all(r["passed"] for r in results) or (len(cases) >= 25 and not all(gates.values())):
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", default="")
    parser.add_argument("--cases-file", default=str(HERE / "cases.yaml"))
    parser.add_argument(
        "--search-key-db",
        default="",
        help="Read only the saved search credential from the new app database, without logging it",
    )
    parser.add_argument(
        "--providers",
        choices=[
            "ollama,searxng,exa,ddgs",
            "ollama",
            "searxng,exa,ddgs",
            "searxng,ddgs",
            "searxng",
            "exa",
            "ddgs",
        ],
        default="ollama,searxng,exa,ddgs",
    )
    parser.add_argument("--model", default="qwen3:30b-a3b-instruct-2507-q4_K_M")
    parser.add_argument("--url", default="http://127.0.0.1:11434")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--record", action="store_true")
    parser.add_argument("--ranking", choices=["keyword", "hybrid"], default="keyword")
    parser.add_argument("--embedding", default="qwen3-embedding:0.6b")
    parser.add_argument("--fixture-root", default=str(HERE / "fixtures"))
    parser.add_argument(
        "--planner-trial",
        choices=["spec", "task-and-scope", "task-and-scope-v2", "intent-first"],
        default="spec",
    )
    parser.add_argument(
        "--answer-trial",
        choices=["spec", "direct-and-consistent", "cited-evidence"],
        default="spec",
    )
    asyncio.run(evaluate(parser.parse_args()))
