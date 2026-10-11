"""Frozen source comparison; synthetic replay, real runtime, no production writes."""
import argparse
import asyncio
import hashlib
import json
import os
import runpy
import subprocess
import sys
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path
from time import monotonic
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = Path(__file__).resolve().parent
BASELINE = ROOT / "tmp/images-i1/search-diagnosis/baseline"
MODEL = "qwen3:30b-a3b-instruct-2507-q4_K_M"
FIXTURE = ROOT / "server/evals/web/fixtures/phase2-final-corpus"
HOME = Path.home() / ".local/share/workbench/image-worker/product"
NOW = datetime(2026, 10, 11, 12, tzinfo=ZoneInfo("America/New_York"))
ORDER = [("pair-1-baseline", "baseline", True), ("pair-1-candidate", "candidate", True),
         ("pair-2-candidate", "candidate", True), ("pair-2-baseline", "baseline", True),
         ("pair-3-baseline", "baseline", True), ("pair-3-candidate", "candidate", True),
         ("full-candidate", "candidate", False), ("full-baseline", "baseline", False)]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frozen():
    document = json.loads((OUTPUT / "manifest.json").read_text())
    for name, expected in document["files"].items():
        assert digest(ROOT / name) == expected, name
    for name, expected in document["baseline_files"].items():
        assert digest(BASELINE / name) == expected, name


async def activity():
    import httpx
    async with httpx.AsyncClient(timeout=10, trust_env=False) as client:
        runs = await client.get("http://127.0.0.1:8787/api/runs/active")
        audio = await client.get("http://127.0.0.1:8787/api/transcription/audio-storage")
        runs.raise_for_status(); audio.raise_for_status()
        if runs.json() or audio.json()["active_files"]:
            raise RuntimeError("Human inference/transcription became active; diagnosis stopped.")


def child(label, arm, focused):
    frozen()
    source = BASELINE / "server" if arm == "baseline" else ROOT / "server"
    sys.path[:0] = [str(source), str(ROOT / "server"), str(ROOT / "server/evals/web")]
    # Import package identity before the unchanged evaluator adds its own path.
    import app
    assert Path(app.__file__).resolve().parent == source / "app"
    from app.providers.ollama import Ollama
    from app import main as app_main
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
    original_app = app_main.create_app

    def configured(settings=None, **kwargs):
        if arm == "candidate":
            assert settings is not None
            settings.image_home = HOME
        return original_app(settings, **kwargs)

    app_main.create_app = configured
    folder = OUTPUT / label
    folder.mkdir(exist_ok=False)
    original_init, original_stream, original_load = Ollama.__init__, Ollama.stream, Ollama.load

    def initialize(self, *args, **kwargs):
        original_init(self, *args, **kwargs)

        async def wire(request):
            if request.method == "POST" and request.url.path == "/api/chat":
                body = request.content.decode()
                with (folder / "wire.jsonl").open("a") as handle:
                    handle.write(json.dumps({"body": body, "sha256": hashlib.sha256(request.content).hexdigest()}) + "\n")

        self.client.event_hooks["request"].append(wire)

    async def captured_stream(self, request):
        await activity()
        entry = {"arm": arm, "capacity_enabled": bool(getattr(self, "capacity", None)),
                 "payload": self.payload(request), "events": [], "error": None}
        if entry["capacity_enabled"] != (arm == "candidate"):
            raise RuntimeError("Native-admission instrumentation did not match declared arm.")
        start = monotonic()
        stream = original_stream(self, request)
        try:
            async for event in stream:
                entry["events"].append({"type": type(event).__name__, "value": asdict(event)})
                yield event
        except BaseException as exc:
            entry["error"] = type(exc).__name__
            raise
        finally:
            await stream.aclose()
            entry["seconds"] = monotonic() - start
            with (folder / "trace.jsonl").open("a") as handle:
                handle.write(json.dumps(entry) + "\n")

    async def checked_load(self, *args, **kwargs):
        await activity()
        await original_load(self, *args, **kwargs)

    async def no_final_ejection(self, model):
        print("Diagnosis: final harness unload skipped; no human-model ejection.", flush=True)

    Ollama.__init__, Ollama.stream, Ollama.load, Ollama.unload = initialize, captured_stream, checked_load, no_final_ejection
    (folder / "instrumentation.json").write_text(json.dumps({"arm": arm, "source": str(source.relative_to(ROOT)),
        "clock": NOW.isoformat(), "native_admission_enabled": arm == "candidate", "image_calls": 0,
        "prompt_edit": False, "sampling_edit": False, "unload_policy": "Skip evaluator final unload; ordinary explicit warm load unchanged"}, indent=2) + "\n")
    target = ROOT / "server/evals/web/run_eval.py"
    sys.argv = [str(target), "--model", MODEL, "--replay-corpus", "--fixture-root", str(FIXTURE)]
    if focused:
        sys.argv += ["--case", "injection"]
    os.chdir(ROOT / "server")
    runpy.run_path(str(target), run_name="__main__")


def orchestrate():
    frozen()
    index = OUTPUT / "ordered-results.json"
    if index.exists():
        raise RuntimeError("The declared comparison already has results; no unretained retry.")
    entries = []
    reports = ROOT / "server/evals/web/reports"
    for label, arm, focused in ORDER:
        asyncio.run(activity())
        before = set(reports.glob("*.json"))
        with (OUTPUT / (label + ".log")).open("x") as handle:
            result = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--child", label, "--arm", arm,
                                     *( ["--focused"] if focused else [])], cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT, timeout=900)
        created = set(reports.glob("*.json")) - before
        if len(created) != 1:
            raise RuntimeError("Child did not produce exactly one retained report: " + label)
        report = created.pop()
        document = json.loads(report.read_text())
        entry = {"label": label, "arm": arm, "focused": focused, "exit_code": result.returncode,
                 "report": str(report.relative_to(ROOT)), "report_sha256": digest(report), "metrics": document["metrics"]}
        entries.append(entry)
        index.write_text(json.dumps({"declared_order": ORDER, "runs": entries}, indent=2) + "\n")
        print(json.dumps({"label": label, "exit_code": result.returncode, "cases_passed": document["metrics"]["cases_passed"],
                          "injection_exercised": document["metrics"]["gates"]["injection_exercised"]}), flush=True)
        frozen()
    print("Declared runs complete; failures retained. No release decision made.", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--child", default="")
    parser.add_argument("--arm", choices=["baseline", "candidate"])
    parser.add_argument("--focused", action="store_true")
    args = parser.parse_args()
    if args.child:
        child(args.child, args.arm, args.focused)
    else:
        orchestrate()
