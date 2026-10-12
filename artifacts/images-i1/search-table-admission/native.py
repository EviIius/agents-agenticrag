"""Six declared children maximum; original Search calls, isolated admission hook."""

import argparse
import asyncio
import hashlib
import json
import re
import subprocess
import sys
from contextvars import ContextVar
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path
from time import monotonic
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "server"))
MODEL = "qwen3:30b-a3b-instruct-2507-q4_K_M"
NOW = datetime(2026, 10, 12, 12, tzinfo=ZoneInfo("America/New_York"))
IMAGE_HOME = Path.home() / ".local/share/workbench/image-worker/product"
QUESTION = ContextVar("original_question", default="")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    path = OUT / name
    with path.open("x") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def frozen():
    document = json.loads((OUT / "manifest.json").read_text())
    for name, expected in document["files"].items():
        assert digest(ROOT / name) == expected, name


async def activity():
    import httpx

    async with httpx.AsyncClient(timeout=10, trust_env=False) as client:
        runs = await client.get("http://127.0.0.1:8787/api/runs/active")
        audio = await client.get("http://127.0.0.1:8787/api/transcription/audio-storage")
        runs.raise_for_status()
        audio.raise_for_status()
        if runs.json() or audio.json()["active_files"]:
            raise RuntimeError("Human inference/transcription active; experiment stopped.")


async def preflight():
    import httpx

    await activity()
    async with httpx.AsyncClient(timeout=15, trust_env=False) as client:
        version = await client.get("http://127.0.0.1:11434/api/version")
        tags = await client.get("http://127.0.0.1:11434/api/tags")
        show = await client.post("http://127.0.0.1:11434/api/show", json={"model": MODEL})
        for response in (version, tags, show):
            response.raise_for_status()
        assert version.json()["version"] == "0.35.0"
        model = next(m for m in tags.json()["models"] if m["name"] == MODEL)
        # Only the approved public model's metadata, never app chat/document data.
        result = {
            "version": version.json(),
            "model": model,
            "show": show.json(),
            "show_is_metadata_not_inference": True,
            "data_dir": "disposable workbench-eval-* only",
        }
    return result


def evaluation_args():
    return argparse.Namespace(
        model=MODEL,
        url="http://127.0.0.1:11434",
        temperature=None,
        live=False,
        record=False,
        case="nba-all-losses",
        cases_file=str(ROOT / "server/evals/web/cases.yaml"),
        fixture_root=str(ROOT / "server/evals/web/fixtures/phase2-final-corpus"),
        providers="ollama,searxng,exa,ddgs",
        search_key_db="",
        replay_corpus=True,
        replay_plans=False,
        ranking="keyword",
        embedding="qwen3-embedding:0.6b",  # Disabled by keyword ranking.
        planner_trial="spec",
        answer_trial="spec",
        table_trial="spec",
        evidence_format="spec",
        ranking_query="spec",
        question_first=False,
        fill_trial="spec",
        filter_proof="",
    )


def observe_selection(folder, arm, ranked, budget, maximum, ratio, question):
    import admission

    before = admission.original_select(ranked, budget, maximum, ratio)
    after = (
        admission.select(ranked, budget, maximum, ratio, question=question)
        if arm == "candidate"
        else before
    )
    record = {
        "arm": arm,
        "question": question,
        "budget": budget,
        "maximum": maximum,
        "ratio": ratio,
        "before": [[p.model_dump() for p in group] for group in before],
        "after": [[p.model_dump() for p in group] for group in after],
        "before_cost": sum(admission.cost(p, ratio) for group in before for p in group),
        "after_cost": sum(admission.cost(p, ratio) for group in after for p in group),
    }
    assert record["after_cost"] <= budget
    with (folder / "admission.jsonl").open("a") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return after


def child(label, arm):
    frozen()
    assert [label, arm] in json.loads((OUT / "execution.json").read_text())["order"]
    folder = OUT / label
    folder.mkdir(exist_ok=False)
    sys.path[:0] = [str(ROOT / "server"), str(ROOT / "server/evals/web")]
    import run_eval

    from app import main as app_main
    from app.db import messages
    from app.providers.ollama import Ollama
    from app.runs import context
    from app.search import pipeline, planner, prompt

    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return NOW.astimezone(tz) if tz else NOW

    class FixedDate(date):
        @classmethod
        def today(cls):
            return NOW.date()

    planner.datetime = context.datetime = FixedDateTime
    prompt.date = FixedDate
    prompts = json.loads((OUT / "prompts.json").read_text())
    assert planner.PROMPT == prompts["planner"] and prompt.PROMPT == prompts["answer"]
    original_schema = planner.schema
    expected_schema = None

    def bound_schema(latest):
        nonlocal expected_schema
        expected_schema = original_schema(latest)
        return expected_schema

    planner.schema = bound_schema
    original_plan = planner.plan

    async def checked_plan(*args, **kwargs):
        result, fallback = await original_plan(*args, **kwargs)
        if fallback:
            # Do not let a native planner failure silently consume an answer call.
            raise RuntimeError("Native planner fallback; bounded comparison stops.")
        return result, fallback

    planner.plan = checked_plan
    original_call = pipeline.Pipeline.__call__

    async def question_bound(self, run, request, ctx, force):
        assert self.manager.data_dir.name.startswith("workbench-eval-")
        history = context.path(
            await messages.list_messages(self.store, run.message.chat_id), run.message.parent_id
        )
        token = QUESTION.set(history[-1].content)
        try:
            await original_call(self, run, request, ctx, force)
        finally:
            QUESTION.reset(token)

    pipeline.Pipeline.__call__ = question_bound

    def selected(ranked, budget, maximum, ratio):
        assert QUESTION.get()
        return observe_selection(folder, arm, ranked, budget, maximum, ratio, QUESTION.get())

    pipeline.select = selected
    run_eval.HERE = folder
    original_app = app_main.create_app

    def configured(settings=None, **kwargs):
        assert settings is not None and settings.data_dir.name.startswith("workbench-eval-")
        settings.image_home = IMAGE_HOME
        return original_app(settings, **kwargs)

    run_eval.create_app = configured
    original_init, original_stream, original_load = Ollama.__init__, Ollama.stream, Ollama.load

    def initialize(self, *args, **kwargs):
        original_init(self, *args, **kwargs)

        async def wire(request):
            if request.method == "POST" and request.url.path == "/api/chat":
                body = request.content.decode()
                with (folder / "wire.jsonl").open("a") as handle:
                    handle.write(
                        json.dumps(
                            {"body": body, "sha256": hashlib.sha256(request.content).hexdigest()}
                        )
                        + "\n"
                    )

        self.client.event_hooks["request"].append(wire)

    async def captured_stream(self, request):
        await activity()
        entry = {
            "arm": arm,
            "capacity_enabled": self.capacity is not None,
            "payload": self.payload(request),
            "events": [],
            "error": None,
        }
        clock = monotonic()
        stream = None
        try:
            assert self.capacity is not None
            assert request.model_id == MODEL and request.context_length == 16384
            if request.json_schema is not None:
                assert expected_schema is not None and request.json_schema == expected_schema
                assert request.params == {"temperature": 0.2, "max_tokens": 256}
                assert request.reasoning == "off"
            else:
                assert request.params == {} and request.reasoning is None
            assert "tools" not in entry["payload"]
            stream = original_stream(self, request)
            async for event in stream:
                entry["events"].append({"type": type(event).__name__, "value": asdict(event)})
                if type(event).__name__ == "ToolCall":
                    raise RuntimeError("Unexpected native tool call; comparison stops.")
                yield event
        except BaseException as exc:
            entry["error"] = type(exc).__name__
            raise
        finally:
            if stream is not None:
                await stream.aclose()
            entry["seconds"] = monotonic() - clock
            with (folder / "trace.jsonl").open("a") as handle:
                handle.write(json.dumps(entry) + "\n")

    async def checked_load(self, *args, **kwargs):
        await activity()
        await original_load(self, *args, **kwargs)

    async def no_ejection(self, model):
        print("Final evaluator unload skipped; no human model ejection.", flush=True)

    Ollama.__init__, Ollama.stream, Ollama.load, Ollama.unload = (
        initialize,
        captured_stream,
        checked_load,
        no_ejection,
    )
    asyncio.run(run_eval.evaluate(evaluation_args()))


def protocol(folder, document):
    from app.schemas import Passage
    from app.search.selection import bind_references

    traces = [json.loads(line) for line in (folder / "trace.jsonl").read_text().splitlines()]
    wires = [
        json.loads(json.loads(line)["body"])
        for line in (folder / "wire.jsonl").read_text().splitlines()
    ]
    planners = [row for row in traces if row["payload"].get("format") is not None]
    answers = [row for row in traces if row["payload"].get("format") is None]
    warm = [row for row in wires if not row.get("messages")]
    expected = {
        "utility": {"temperature": 0.2, "num_predict": 256, "num_ctx": 16384},
        "answer": {"num_ctx": 16384},
    }
    selections = (
        [json.loads(line) for line in (folder / "admission.jsonl").read_text().splitlines()]
        if (folder / "admission.jsonl").exists()
        else []
    )
    sources = document["results"][0]["turns"][0]["sources"]
    selected_texts = [
        [
            bind_references(
                Passage(**p).model_copy(
                    update={
                        "text": re.sub(
                            r"</(?:source|search_results)\s*>", "", p["text"], flags=re.I
                        )
                    }
                ),
                n,
            ).model_dump()
            for p in group
        ]
        for n, group in enumerate(selections[0]["after"] if selections else [], 1)
    ]
    streamed = [row for row in wires if row.get("messages")]
    checks = {
        "one_planner_one_answer": len(planners) == len(answers) == 1,
        "one_warm_load_only": len(warm) == 1 and len(wires) == 3,
        "calls_healthy": all(
            row["error"] is None
            and row["capacity_enabled"]
            and any(e["type"] == "Usage" for e in row["events"])
            and any(
                e["type"] == "Finish" and e["value"]["reason"] != "error" for e in row["events"]
            )
            for row in traces
        ),
        "unchanged_wire": all(row.get("model") == MODEL and "tools" not in row for row in wires),
        "sampling_context": all(
            row["payload"]["options"] == expected["utility" if row in planners else "answer"]
            for row in traces
        ),
        "report_original_case": [r["id"] for r in document["results"]] == ["nba-all-losses"],
        "source_admission_observed": (folder / "admission.jsonl").exists(),
        "original_source_text_reaches_answer": len(selections) == 1
        and [s["passages"] for s in sources] == selected_texts,
        "wire_matches_instrumented_request": [row["payload"] for row in traces] == streamed,
        "no_planner_fallback": document["results"][0]["turns"][0]["web"].get("plan_fallback")
        is False,
        "no_tool_events": all(e["type"] != "ToolCall" for row in traces for e in row["events"]),
    }
    return checks


def run_next():
    frozen()
    assert "473 passed" in (OUT / "make-e2e.log").read_text()
    assert "3 skipped" in (OUT / "make-e2e.log").read_text()
    assert "508 passed" in (OUT / "make-check.log").read_text()
    declaration = json.loads((OUT / "execution.json").read_text())
    index = OUT / "ordered-results.json"
    state = json.loads(index.read_text()) if index.exists() else {"runs": [], "stop": None}
    assert not state["stop"], "Stopped candidates cannot retry."
    for run in state["runs"]:
        review = json.loads((OUT / (run["label"] + "-review.json")).read_text())
        assert review["report_sha256"] == run["report_sha256"]
        assert review["protocol_verified"] is True
        if run["arm"] == "candidate":
            assert review["passed"] is True, "Manual candidate failure ends inference."
    position = len(state["runs"])
    assert position < len(declaration["order"]), "All six declared children completed."
    label, arm = declaration["order"][position]
    metadata = asyncio.run(preflight())
    write(label + "-preflight.json", metadata)
    with (OUT / (label + ".log")).open("x") as handle:
        result = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--child", label, "--arm", arm],
            cwd=ROOT,
            stdout=handle,
            stderr=subprocess.STDOUT,
            timeout=900,
        )
    reports = list((OUT / label / "reports").glob("*.json"))
    entry = {"label": label, "arm": arm, "returncode": result.returncode}
    if len(reports) != 1 or result.returncode not in (0, 1):
        state["stop"] = {"label": label, "reason": "child/protocol failure"}
    else:
        document = json.loads(reports[0].read_text())
        checks = protocol(OUT / label, document)
        entry.update(
            report=str(reports[0].relative_to(ROOT)),
            report_sha256=digest(reports[0]),
            metrics=document["metrics"],
            protocol=checks,
        )
        if not all(checks.values()):
            state["stop"] = {"label": label, "reason": "protocol failure", "checks": checks}
        elif arm == "candidate" and not document["results"][0]["passed"]:
            state["stop"] = {"label": label, "reason": "candidate mandatory automatic failure"}
    state["runs"].append(entry)
    state["unexecuted"] = declaration["order"][len(state["runs"]) :]
    index.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(entry, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--child")
    parser.add_argument("--arm", choices=["baseline", "candidate"])
    parser.add_argument("--next", action="store_true")
    args = parser.parse_args()
    if args.child:
        child(args.child, args.arm)
    elif args.next:
        run_next()
    else:
        parser.error("Use --next; each child requires retained manual review before advancing.")
