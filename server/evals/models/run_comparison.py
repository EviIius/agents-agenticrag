"""Run the approved pairs; never change the live application or model defaults."""

import argparse
import hashlib
import json
import runpy
import subprocess
import sys
import urllib.request
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from time import monotonic

SERVER = Path(__file__).resolve().parents[2]
REPO = SERVER.parent
OUTPUT = REPO / "artifacts/model-comparison"
BASELINE = "qwen3:30b-a3b-workbench-32k"
CANDIDATE = "qwen3.8:27b-atelier-eval-32k"


def get(url: str):
    with urllib.request.urlopen(url, timeout=15) as response:
        return json.load(response)


def snapshot():
    return {
        "time_utc": datetime.now(UTC).isoformat(),
        "runtime_ps": get("http://127.0.0.1:11434/api/ps"),
        "memory_pressure": subprocess.run(
            ["/usr/bin/memory_pressure"], capture_output=True, text=True, check=True
        ).stdout,
        "limitation": "Snapshots only; not peak residency.",
    }


def verify_inputs():
    frozen = json.loads((REPO / "docs/model-comparison/frozen-inputs.json").read_text())
    for name, expected in frozen["sha256"].items():
        actual = hashlib.sha256((REPO / name).read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError("Frozen comparison input changed: " + name)


def child(suite: str, arguments: list[str], trace: str):
    # The existing Web harness unloads its model after evaluation. Skip that
    # management action in this process so it cannot eject a concurrent user.
    # This affects residency only, never prompts, sampling, calls or grading.
    sys.path.insert(0, str(SERVER))
    from app.providers.ollama import Ollama

    original_stream = Ollama.stream

    async def retained_stream(self, request):
        result = {"payload": self.payload(request), "events": []}
        started = monotonic()
        try:
            async for event in original_stream(self, request):
                result["events"].append(
                    {
                        "type": type(event).__name__,
                        "value": asdict(event),
                        "elapsed_ms": (monotonic() - started) * 1000,
                    }
                )
                yield event
        finally:
            with Path(trace).open("a") as output:
                output.write(json.dumps(result) + "\n")

    Ollama.stream = retained_stream

    async def keep_resident(self, model_id: str):
        print("Comparison: final harness unload skipped to preserve active users", flush=True)

    Ollama.unload = keep_resident
    target = SERVER / "evals" / suite / "run_eval.py"
    sys.path.insert(0, str(target.parent))
    sys.argv = [str(target), *arguments]
    runpy.run_path(str(target), run_name="__main__")


def compare(resume: bool = False):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    index = OUTPUT / "pairs.json"
    if index.exists() and not resume:
        raise RuntimeError("Never overwrite a previous comparison")
    smoke = json.loads((OUTPUT / "smoke-review.json").read_text())
    assert smoke["all_smoke_pass"] is True
    report = {
        "started_utc": datetime.now(UTC).isoformat(),
        "order": ["baseline/candidate", "candidate/baseline", "baseline/candidate"],
        "web_mode": "Frozen recorded result batches, real planner; no frozen plans",
        "unload_policy": "Evaluator final unload skipped; no forced human-model ejection",
        "results": [],
        "manual_review_required": True,
    }
    if resume:
        report = json.loads(index.read_text())
        if "execution_error" in report:
            report.setdefault("interruptions", []).append(
                {
                    "error": report.pop("execution_error"),
                    "time_utc": report.pop("finished_utc", None),
                }
            )
    try:
        for pair, order in enumerate(
            [(BASELINE, CANDIDATE), (CANDIDATE, BASELINE), (BASELINE, CANDIDATE)], 1
        ):
            for model in order:
                name = "baseline" if model == BASELINE else "candidate"
                for suite in ("everyday", "web", "library"):
                    verify_inputs()
                    if get("http://127.0.0.1:8787/api/runs/active"):
                        raise RuntimeError("Live inference active; stop before another suite")
                    storage = get("http://127.0.0.1:8787/api/transcription/audio-storage")
                    if storage["active_files"]:
                        raise RuntimeError("Live transcription active; stop before another suite")
                    label = f"pair-{pair}-{name}-{suite}"
                    earlier = [r for r in report["results"] if r["label"] == label]
                    if any(r["reports"] and not r.get("setup_invalid") for r in earlier):
                        continue
                    before = snapshot()
                    log_name = label + (f"-attempt-{len(earlier) + 1}" if earlier else "")
                    arguments = ["--model", model]
                    folder = SERVER / "evals" / suite / "reports"
                    previous = set(folder.glob("*.json"))
                    if suite == "everyday":
                        output = OUTPUT / (label + ".json")
                        arguments += ["--label", label, "--output", str(output)]
                        command = [sys.executable, str(Path(__file__).with_name("run_everyday.py"))]
                    else:
                        command = [
                            sys.executable,
                            str(Path(__file__)),
                            "--child",
                            suite,
                            "--trace",
                            str(OUTPUT / (log_name + "-streams.jsonl")),
                            "--",
                        ]
                        if suite == "web":
                            arguments += [
                                "--replay-corpus",
                                "--fixture-root",
                                str(SERVER / "evals/web/fixtures/phase2-final-corpus"),
                                "--search-key-db",
                                str(Path.home() / ".local/share/workbench/data/workbench.db"),
                            ]
                    print("Starting " + label, flush=True)
                    started = monotonic()
                    with (OUTPUT / (log_name + ".log")).open("x") as log:
                        result = subprocess.run(
                            command + arguments, cwd=SERVER, stdout=log, stderr=subprocess.STDOUT
                        )
                    paths = (
                        [output]
                        if suite == "everyday"
                        else sorted(set(folder.glob("*.json")) - previous)
                    )
                    entry = {
                        "label": label,
                        "log": log_name + ".log",
                        "model": model,
                        "suite": suite,
                        "exit_code": result.returncode,
                        "elapsed_seconds": monotonic() - started,
                        "reports": [str(p.relative_to(REPO)) for p in paths if p.exists()],
                        "before": before,
                        "after": snapshot(),
                    }
                    report["results"].append(entry)
                    index.write_text(json.dumps(report, indent=2) + "\n")
                    print(
                        json.dumps(
                            {
                                k: entry[k]
                                for k in ("label", "exit_code", "elapsed_seconds", "reports")
                            }
                        ),
                        flush=True,
                    )
                    if not entry["reports"]:
                        raise RuntimeError("Harness failed before producing a report; retain log")
        verify_inputs()
        report["full_execution_complete"] = True
    except BaseException as exc:
        report["execution_error"] = str(exc)
        raise
    finally:
        report["finished_utc"] = datetime.now(UTC).isoformat()
        index.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--child", choices=("web", "library"))
    parser.add_argument("--trace", default="")
    parser.add_argument("--resume", action="store_true")
    args, remaining = parser.parse_known_args()
    if args.child:
        child(args.child, remaining[1:] if remaining[:1] == ["--"] else remaining, args.trace)
    else:
        compare(args.resume)
