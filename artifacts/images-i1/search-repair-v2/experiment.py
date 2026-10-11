"""One frozen prompt candidate, separate boundaries, unchanged full benchmark."""

import argparse
import asyncio
import hashlib
import json
import subprocess
import sys
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path
from time import monotonic
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
MODEL = "qwen3:30b-a3b-instruct-2507-q4_K_M"
NOW = datetime(2026, 10, 11, 12, tzinfo=ZoneInfo("America/New_York"))
IMAGE_HOME = Path.home() / ".local/share/workbench/image-worker/product"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def child(label, arm, case_id):
    frozen()
    sys.path[:0] = [str(ROOT / "server"), str(ROOT / "server/evals/web")]
    import httpx
    import run_eval

    from app import main as app_main
    from app.providers.ollama import Ollama
    from app.runs import context
    from app.search import planner, prompt

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
    assert planner.PROMPT == prompts["baseline"]["planner"]
    assert prompt.PROMPT == prompts["baseline"]["answer"]
    planner.PROMPT = prompts[arm]["planner"]
    prompt.PROMPT = prompts[arm]["answer"]
    original_schema = planner.schema
    expected_schema = None

    def bound_schema(latest):
        nonlocal expected_schema
        expected_schema = original_schema(latest)
        return expected_schema

    planner.schema = bound_schema  # Observe the unchanged request-specific schema.
    selected = None
    if case_id:
        selected = next(
            c for c in json.loads((OUT / "cases.json").read_text()) if c["id"] == case_id
        )
    folder = OUT / label
    folder.mkdir(exist_ok=False)
    run_eval.HERE = folder  # Report destination only; explicit case/corpus arguments below.
    original_app = app_main.create_app
    holder = {}

    def configured(settings=None, **kwargs):
        assert settings is not None
        settings.image_home = IMAGE_HOME
        app = original_app(settings, **kwargs)
        holder["app"] = app
        return app

    # run_eval imported the function before this patch.
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
            "capacity_enabled": True,
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
            else:
                assert request.params == {}
            assert "tools" not in entry["payload"]
            stream = original_stream(self, request)
            async for event in stream:
                entry["events"].append({"type": type(event).__name__, "value": asdict(event)})
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
        print("Repair trial: final evaluator unload skipped; no human model ejection.", flush=True)

    Ollama.__init__, Ollama.stream, Ollama.load, Ollama.unload = (
        initialize,
        captured_stream,
        checked_load,
        no_ejection,
    )
    original_post = httpx.AsyncClient.post
    seeded = False

    async def seeded_post(self, url, *args, **kwargs):
        nonlocal seeded
        if (
            selected
            and selected.get("seed_history")
            and not seeded
            and str(url).startswith("/api/chats/")
            and str(url).endswith("/messages")
        ):
            chat_id = str(url).split("/")[3]
            app = holder["app"]
            assert app.state.config.data_dir.name.startswith("workbench-eval-")
            parent = None
            for index, message in enumerate(selected["seed_history"]):
                identifier = "seed-" + selected["id"] + "-" + str(index)
                await app.state.store.execute(
                    "INSERT INTO messages(id,chat_id,parent_id,role,content,created_at,updated_at) "
                    "VALUES (?,?,?,?,?,?,?)",
                    (
                        identifier,
                        chat_id,
                        parent,
                        message["role"],
                        message["content"],
                        NOW.isoformat(),
                        NOW.isoformat(),
                    ),
                )
                parent = identifier
            kwargs["json"] = {**kwargs["json"], "parent_id": parent}
            seeded = True
        return await original_post(self, url, *args, **kwargs)

    httpx.AsyncClient.post = seeded_post
    (folder / "instrumentation.json").write_text(
        json.dumps(
            {
                "arm": arm,
                "source": "ba51370 product tree",
                "case": case_id or "original full suite",
                "clock": NOW.isoformat(),
                "capacity_enabled": True,
                "image_calls": 0,
                "prompt_hashes": {
                    k: hashlib.sha256(v.encode()).hexdigest() for k, v in prompts[arm].items()
                },
                "sampling_edit": False,
                "schema_edit": False,
                "seeded_history": bool(selected and selected.get("seed_history")),
                "seed_note": "Fixed synthetic context; not a claimed tested model answer.",
                "report_destination_only": str(folder.relative_to(ROOT)),
                "final_unload_skipped": True,
            },
            indent=2,
        )
        + "\n"
    )
    args = argparse.Namespace(
        model=MODEL,
        url="http://127.0.0.1:11434",
        temperature=None,
        live=False,
        record=False,
        case=case_id,
        cases_file=str(OUT / "cases.json")
        if case_id
        else str(ROOT / "server/evals/web/cases.yaml"),
        fixture_root=str(OUT / "fixtures")
        if case_id
        else str(ROOT / "server/evals/web/fixtures/phase2-final-corpus"),
        providers="ddgs" if case_id else "ollama,searxng,exa,ddgs",
        search_key_db="",
        replay_corpus=not bool(case_id),
        replay_plans=False,
        ranking="keyword",
        embedding="qwen3-embedding:0.6b",
        planner_trial="spec",
        answer_trial="spec",
        table_trial="spec",
        evidence_format="spec",
        ranking_query="spec",
        question_first=False,
        fill_trial="spec",
        filter_proof="",
    )
    asyncio.run(run_eval.evaluate(args))


def protocol_verified(folder, document):
    """A swallowed instrumentation error must stop before interpreting scores."""
    traces = [json.loads(line) for line in (folder / "trace.jsonl").read_text().splitlines()]
    wires = [
        json.loads(json.loads(line)["body"])
        for line in (folder / "wire.jsonl").read_text().splitlines()
    ]
    turns = sum(len(result["turns"]) for result in document["results"])
    planners = [row for row in traces if row["payload"].get("format") is not None]
    answers = [row for row in traces if row["payload"].get("format") is None]
    return (
        len(planners) == len(answers) == turns
        and sum(row.get("format") is not None for row in wires) == turns
        and sum(row.get("stream") is True and row.get("format") is None for row in wires) == turns
        and all(
            row["error"] is None
            and row["capacity_enabled"]
            and any(event["type"] == "Usage" for event in row["events"])
            and any(
                event["type"] == "Finish" and event["value"]["reason"] != "error"
                for event in row["events"]
            )
            for row in traces
        )
    )


def g9(candidate, baseline):
    checks = {}
    for name in (
        "search_decision_accuracy",
        "required_fact_case_accuracy",
        "citation_validity",
        "citation_support_mean",
        "successful_web_turns",
    ):
        checks[name] = (
            candidate[name] is not None
            and baseline[name] is not None
            and candidate[name] >= baseline[name]
        )
    for name in ("failed_web_turns", "successful_web_ttft_p50_ms", "successful_web_ttft_p90_ms"):
        checks[name] = (
            candidate[name] is not None
            and baseline[name] is not None
            and candidate[name] <= baseline[name]
        )
    for stage, metrics in baseline["stage_latency_ms"].items():
        for percentile, value in metrics.items():
            actual = candidate["stage_latency_ms"].get(stage, {}).get(percentile)
            checks[stage + "." + percentile] = actual is not None and actual <= value
    return checks


def orchestrate(phase):
    frozen()
    declaration = json.loads((OUT / "execution.json").read_text())
    index = OUT / "ordered-results.json"
    if phase == "boundary":
        if index.exists():
            raise RuntimeError("This candidate has retained results; no automatic retry.")
        result = {"declared_order": declaration["order"], "runs": [], "stop": None}
        start, end = 0, 48
    else:
        pair = int(phase[-1])
        start, end = 48 + 2 * (pair - 1), 48 + 2 * pair
        result = json.loads(index.read_text())
        assert not result["stop"] and len(result["runs"]) == start
        previous = "boundary" if pair == 1 else "full-" + str(pair - 1)
        review = json.loads((OUT / ("review-" + previous + ".json")).read_text())
        assert review["passed"] is True
        expected = {
            r["report"]: r["report_sha256"] for r in result["runs"] if r["arm"] == "candidate"
        }
        assert review["candidate_reports_reviewed"] == expected
    for label, arm, case_id in declaration["order"][start:end]:
        asyncio.run(activity())
        with (OUT / (label + ".log")).open("x") as handle:
            process = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).resolve()),
                    "--child",
                    label,
                    "--arm",
                    arm,
                    "--case-id",
                    case_id,
                ],
                cwd=ROOT,
                stdout=handle,
                stderr=subprocess.STDOUT,
                timeout=900,
            )
        reports = list((OUT / label / "reports").glob("*.json"))
        if len(reports) != 1 or process.returncode not in (0, 1):
            result["stop"] = {
                "label": label,
                "reason": "protocol/harness failure",
                "exit_code": process.returncode,
            }
            index.write_text(json.dumps(result, indent=2) + "\n")
            raise RuntimeError("No valid retained evaluator report: " + label)
        report = reports[0]
        document = json.loads(report.read_text())
        if not protocol_verified(OUT / label, document):
            result["stop"] = {
                "label": label,
                "reason": "protocol/harness failure",
                "retained_report": str(report.relative_to(ROOT)),
            }
            index.write_text(json.dumps(result, indent=2) + "\n")
            raise RuntimeError("Missing/failed planner or answer trace: " + label)
        prompts = json.loads((OUT / "prompts.json").read_text())[arm]
        for kind in ("planner", "answer"):
            assert (
                document[kind + "_prompt_sha256"]
                == hashlib.sha256(prompts[kind].encode()).hexdigest()
            )
        passed = all(r["passed"] for r in document["results"])
        exposure = None
        if case_id:
            case = next(
                c for c in json.loads((OUT / "cases.json").read_text()) if c["id"] == case_id
            )
            if case.get("attack_marker"):
                exposure = any(
                    case["attack_marker"] in passage["text"]
                    for r in document["results"]
                    for turn in r["turns"]
                    for source in turn["sources"]
                    for passage in source["passages"]
                )
                passed = passed and exposure
        else:
            passed = passed and document["metrics"]["gates"]["injection_exercised"] is True
        entry = {
            "label": label,
            "arm": arm,
            "case": case_id or "original full suite",
            "exit_code": process.returncode,
            "report": str(report.relative_to(ROOT)),
            "report_sha256": digest(report),
            "metrics": document["metrics"],
            "mandatory_checks_pass": passed,
            "attack_exposed": exposure,
        }
        result["runs"].append(entry)
        if arm == "candidate" and not passed:
            result["stop"] = {"label": label, "reason": "mandatory candidate failure"}
        if arm == "candidate" and not case_id and passed:
            historical = json.loads((ROOT / declaration["historical_report"]).read_text())
            entry["historical_g9"] = g9(document["metrics"], historical["metrics"])
            if not all(entry["historical_g9"].values()):
                result["stop"] = {"label": label, "reason": "historical G9 aggregate failure"}
        if not case_id and label.startswith("full-pair-"):
            partner = next(
                (
                    r
                    for r in result["runs"][:-1]
                    if r["label"].rsplit("-", 1)[0] == label.rsplit("-", 1)[0]
                ),
                None,
            )
            if partner:
                c = entry if arm == "candidate" else partner
                b = entry if arm == "baseline" else partner
                entry["matched_g9"] = g9(c["metrics"], b["metrics"])
                if not all(entry["matched_g9"].values()):
                    result["stop"] = {"label": label, "reason": "matched G9 aggregate failure"}
        index.write_text(json.dumps(result, indent=2) + "\n")
        print(
            json.dumps(
                {
                    "label": label,
                    "passed": passed,
                    "cases_passed": document["metrics"]["cases_passed"],
                    "stop": result["stop"],
                }
            ),
            flush=True,
        )
        frozen()
        if result["stop"]:
            print(
                "Stopped at declared gate; later runs not executed. No production prompt edit.",
                flush=True,
            )
            return
    result["completed_phase"] = phase
    result["manual_review_required"] = True
    index.write_text(json.dumps(result, indent=2) + "\n")
    print(
        "Phase complete; manual support review required before the next declared phase.", flush=True
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--child", default="")
    parser.add_argument("--arm", choices=["baseline", "candidate"])
    parser.add_argument("--case-id", default="")
    parser.add_argument(
        "--phase", choices=["boundary", "full-1", "full-2", "full-3"], default="boundary"
    )
    args = parser.parse_args()
    if args.child:
        child(args.child, args.arm, args.case_id)
    else:
        orchestrate(args.phase)
