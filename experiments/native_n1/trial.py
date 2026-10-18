"""Prepare / execute ONE task / review. N1 never imports into the live app."""

from __future__ import annotations

import argparse
import asyncio
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
from functools import partial
from pathlib import Path
from time import monotonic
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "server"))
sys.path.insert(0, str(Path(__file__).parent))

import httpx  # noqa: E402
from protocol import (  # noqa: E402
    MODEL,
    SCHEDULE,
    SCOPES,
    SYSTEM,
    CountedTransport,
    ExperimentalAgent,
    Fixtures,
    Ledger,
    Refused,
    write,
)

from app.capacity import Capacity  # noqa: E402
from app.db.core import Store, connect  # noqa: E402
from app.library.pipeline import Pipeline as LibraryPipeline  # noqa: E402
from app.providers.base import ChatRequest, ProviderMessage  # noqa: E402
from app.providers.ollama import Ollama  # noqa: E402
from app.providers.registry import Registry  # noqa: E402
from app.runs.context import Context  # noqa: E402
from app.runs.manager import Run, RunManager  # noqa: E402
from app.schemas import Message  # noqa: E402
from app.search import citations  # noqa: E402
from app.search.pipeline import Pipeline as SearchPipeline  # noqa: E402

OUT = ROOT / "artifacts/agent-loop/n1"
QA = Path.home() / ".local/share/workbench/qa/native-agent-n1-20261018"
SHARED = Path.home() / ".local/share/workbench/data/native.lock"
MAX_SECONDS = 180


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


async def metadata(path, body=None, *, app=False):
    base = "http://127.0.0.1:" + ("8787" if app else "11434")
    async with httpx.AsyncClient(timeout=2, trust_env=False) as client:
        response = await client.request("GET" if body is None else "POST", base + path, json=body)
        response.raise_for_status()
        return response.json()


async def sample():
    began = monotonic()
    raw = await asyncio.to_thread(
        subprocess.check_output, ["/usr/sbin/sysctl", "-n", "vm.swapusage"]
    )
    match = re.search(rb"used\s*=\s*([\d.]+)M", raw)
    if not match:
        raise Refused("Cannot measure swap")
    health = await metadata("/api/health", app=True)
    health_ms = (monotonic() - began) * 1000
    ps = await metadata("/api/ps")
    return {
        "swap_mib": float(match[1]),
        "health_ok": health.get("ok") is True,
        "health_ms": health_ms,
        "models": [
            {k: row.get(k) for k in ("name", "digest", "context_length", "size_vram")}
            for row in ps.get("models", [])
        ],
    }


def resource_check(value, baseline, digest=None):
    if not value["health_ok"] or value["health_ms"] > 2000:
        raise Refused("Live app health failed")
    if value["swap_mib"] > baseline:
        raise Refused("Observed host swap growth")
    if any(row["name"] != MODEL for row in value["models"]):
        raise Refused("Another model is resident; nothing unloaded")
    if any(
        digest and row.get("digest") != digest or row.get("context_length") not in (None, 0, 32768)
        for row in value["models"]
    ):
        raise Refused("Resident identity/context changed")
    if sum(row.get("size_vram") or 0 for row in value["models"]) > 48 * 1024**3:
        raise Refused("Reported model allocation exceeds host ceiling")


async def observed_model():
    adapter = Ollama("native-n1", "http://127.0.0.1:11434")
    try:
        model = next(m for m in await adapter.list_models() if m.model_id == MODEL)
        show = adapter.shows[MODEL][1]
        version = (await adapter.json("GET", "/api/version"))["version"]
    finally:
        await adapter.close()
    if not (
        model.digest
        and model.tools
        and model.chat_capable
        and model.context_length == model.context_limit == 32768
    ):
        raise Refused("Installed daily profile lacks required observed metadata")
    identity = {
        key: hashlib.sha256(json.dumps(show.get(key), sort_keys=True).encode()).hexdigest()
        for key in ("template", "system", "parameters", "capabilities", "model_info")
    }
    return model, version, identity


async def prepare():
    if (OUT / "frozen.json").exists() or (QA / "ledger.json").exists():
        raise Refused("Existing preparation/ledger cannot be reset")
    original = subprocess.check_output(
        ["git", "show", "4acc379f:experiments/hermes_h0/cases.json"], cwd=ROOT
    )
    assert original == (ROOT / "experiments/native_n1/cases-original.json").read_bytes()
    frozen = json.loads((ROOT / "artifacts/agent-loop/n0/executed-source.json").read_text())[
        "files"
    ]
    assert all(sha(ROOT / name) == value for name, value in frozen.items())
    model, version, identity = await observed_model()
    before = await sample()
    if before["models"]:
        raise Refused("Pretrial residency must be empty; nothing unloaded")
    resource_check(before, before["swap_mib"])
    for path in sorted((ROOT / "experiments/native_n1").glob("*")):
        if path.is_file():
            frozen[str(path.relative_to(ROOT))] = sha(path)
    frozen["docs/AGENT-LOOP-N1-PLAN.md"] = sha(ROOT / "docs/AGENT-LOOP-N1-PLAN.md")
    admission = {
        "stage": "N1-experiment-only",
        "model_id": MODEL,
        "digest": model.digest,
        "context_length": 32768,
        "runtime_version": version,
        "show_hashes": identity,
        "swap_baseline_mib": before["swap_mib"],
        "production_qualified": False,
    }
    write(
        OUT / "frozen.json",
        {
            "files": frozen,
            "admission": admission,
            "schedule": SCHEDULE,
            "scopes": SCOPES,
            "system": SYSTEM,
            "before": before,
            "max_calls": 36,
            "reasoning": None,
            "params": {},
            "prepared_model": model.model_dump(),
        },
    )
    write(QA / "ledger.json", {"calls": 0, "tasks": {}, "stopped": None, "active": None})
    print(json.dumps({"prepared": True, "admission": admission, "native_calls": 0}))


class CheckedRun(Run):
    async def emit(self, kind, data):
        await super().emit(kind, data)
        if kind == "tool.finished" and data["step"]["status"] != "done":
            self.ledger.stop("Tool permission/protocol/execution failure")
            raise Refused("First tool failure stops the experiment")


async def execute_case(
    task, corpus, model, admission, ledger, folder, capacity, *, upstream=None, sampler=sample
):
    fixture = Fixtures(corpus, task[3:])
    case = next(c for c in corpus["cases"] if c["id"] == task[3:])
    tools = fixture.tools()
    start = monotonic()
    transport = CountedTransport(
        ledger, task, tools, folder, capacity, upstream, deadline=start + MAX_SECONDS
    )
    adapter = Ollama(
        "native-n1",
        "http://127.0.0.1:11434",
        "30m",
        client=httpx.AsyncClient(
            transport=transport, timeout=httpx.Timeout(300, connect=5), trust_env=False
        ),
    )
    adapter.capacity = capacity
    adapter.models[MODEL] = model
    samples = []
    try:
        first = await sampler()
        resource_check(first, admission["swap_baseline_mib"], admission["digest"])
        samples.append(first)
        async with connect(folder / "data") as db:
            store = Store(db)
            stamp = "2026-10-18T00:00:00Z"
            await store.execute(
                "INSERT INTO chats(id,title,created_at,updated_at) VALUES (?,?,?,?)",
                (task, "Synthetic N1 task", stamp, stamp),
            )
            await store.execute(
                "INSERT INTO messages(id,chat_id,role,status,created_at,updated_at) "
                "VALUES (?,?,'assistant','streaming',?,?)",
                (task, task, stamp, stamp),
            )
            manager = RunManager(store, Registry(store, capacity), folder / "data")
            manager.web_finalize = partial(SearchPipeline.finalize, SimpleNamespace(store=store))
            manager.library_finalize = partial(
                LibraryPipeline.finalize, SimpleNamespace(store=store)
            )
            message = Message(
                id=task,
                chat_id=task,
                parent_id=None,
                role="assistant",
                content="",
                status="streaming",
                created_at=stamp,
                model_id=MODEL,
            )
            run = CheckedRun(task, message)
            run.ledger = ledger
            request = ChatRequest(
                MODEL,
                [ProviderMessage("system", SYSTEM), ProviderMessage("user", case["question"])],
                context_length=32768,
            )
            context = Context(request.messages, 0, 0, 1024, 0.3)
            agent = ExperimentalAgent(manager, adapter, model, tools, admission=admission)
            run.task = asyncio.create_task(agent(run, request, context, asyncio.Semaphore(1)))

            async def monitor():
                try:
                    while not run.task.done():
                        value = await sampler()
                        samples.append(value)
                        resource_check(value, admission["swap_baseline_mib"], admission["digest"])
                        await asyncio.sleep(1)
                except Exception as exc:
                    ledger.stop(type(exc).__name__ + ": " + str(exc))
                    run.task.cancel()

            observer = asyncio.create_task(monitor())

            async def deadline():
                await asyncio.sleep(max(0, MAX_SECONDS - (monotonic() - start)))
                ledger.stop("Task reached its hard 180-second deadline")
                run.task.cancel()

            timer = asyncio.create_task(deadline())
            try:
                await run.task
            finally:
                observer.cancel()
                timer.cancel()
                await asyncio.gather(observer, timer, return_exceptions=True)
            final = await sampler()
            samples.append(final)
            resource_check(final, admission["swap_baseline_mib"], admission["digest"])
            table = "message_sources" if fixture.kind == "web" else "message_library_sources"
            rows = await store.rows(f"SELECT * FROM {table} WHERE message_id=? ORDER BY n", (task,))
            mapping = {}
            for row in rows:
                original = next(
                    s
                    for s in fixture.rows
                    if (
                        s.get("url") == row.get("url")
                        if fixture.kind == "web"
                        else s["id"] == row.get("document_id")
                    )
                )
                mapping[str(row["n"])] = original["id"]
            cited = {mapping[str(n)] for n in citations.cited(message.content) if str(n) in mapping}
            done_tools = [p.step.tool for p in message.parts if p.step and p.step.status == "done"]
            automatic = {
                "complete": message.status == "complete" and bool(message.content.strip()),
                "no_notice_or_limit": bool(message.agent)
                and not message.agent.notice
                and not message.agent.limit_reached,
                "valid_calls": bool(message.agent) and message.agent.invalid_calls == 0,
                "required_citations": set(case["required_source_ids"]) <= cited,
                "required_arithmetic": task[3:] not in {"H03", "H04"} or "calculate" in done_tools,
            }
            result = {
                "task": task,
                "seconds": monotonic() - start,
                "automatic_checks": automatic,
                "source_map": mapping,
                "original_case": case,
                "message": message.model_dump(),
                "tool_names": done_tools,
                "samples": samples,
            }
            write(folder / "result.json", result)
            write(folder / "events.json", [event.model_dump() for event in run.events])
            if not all(automatic.values()):
                ledger.stop("First structural/citation/arithmetic/limit gate failed: " + task)
            return result
    finally:
        await adapter.close()
        write(folder / "resources.json", samples)


async def run_task(task):
    frozen = json.loads((OUT / "frozen.json").read_text())
    if not all(sha(ROOT / name) == value for name, value in frozen["files"].items()):
        raise Refused("Frozen source/input changed")
    model, version, identity = await observed_model()
    admission = frozen["admission"]
    if (
        model.digest != admission["digest"]
        or version != admission["runtime_version"]
        or identity != admission["show_hashes"]
    ):
        raise Refused("Frozen model/runtime identity changed")
    folder = OUT / task
    folder.mkdir(mode=0o700, exist_ok=False)
    ledger = Ledger(QA / "ledger.json")
    ledger.begin(task)
    try:
        result = await execute_case(
            task,
            json.loads((ROOT / "experiments/native_n1/cases-original.json").read_text()),
            model,
            admission,
            ledger,
            folder,
            Capacity(SHARED),
        )
        print(
            json.dumps(
                {
                    "task": task,
                    "seconds": result["seconds"],
                    "automatic_checks": result["automatic_checks"],
                }
            )
        )
    except BaseException as exc:
        ledger.stop(type(exc).__name__ + ": " + str(exc))
        write(folder / "controller-error.json", {"type": type(exc).__name__, "message": str(exc)})
        raise
    finally:
        write(OUT / "ledger-latest.json", json.loads(ledger.path.read_text()))


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["prepare", "run", "review"])
    parser.add_argument("--task", choices=SCHEDULE)
    parser.add_argument("--review-file", type=Path)
    args = parser.parse_args()
    QA.mkdir(mode=0o700, parents=True, exist_ok=True)
    with (QA / "controller.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if args.action == "prepare":
            asyncio.run(prepare())
        elif args.action == "run":
            if not args.task:
                parser.error("--task required")
            asyncio.run(run_task(args.task))
        else:
            if not args.task or not args.review_file:
                parser.error("--task and --review-file required")
            review = json.loads(args.review_file.read_text())
            result = json.loads((OUT / args.task / "result.json").read_text())
            if all(review["checks"].values()) and not all(result["automatic_checks"].values()):
                raise Refused("A structural failure cannot be manually passed")
            ledger = Ledger(QA / "ledger.json")
            ledger.review(args.task, review)
            write(OUT / args.task / "manual-review.json", review)
            write(OUT / "ledger-latest.json", json.loads(ledger.path.read_text()))


if __name__ == "__main__":
    main()
