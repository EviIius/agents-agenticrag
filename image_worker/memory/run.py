"""Run one frozen memory-policy stage, retaining outcomes without retries."""

import argparse
import hashlib
import json
import os
import shutil
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "image_worker"))
import control  # noqa: E402
from guard import ResourceSampler, probe_ok, swap_mib  # noqa: E402

EVIDENCE = ROOT / "artifacts/image-trial/i1-0"
PRIVATE = Path.home() / ".local/share/workbench/image-worker/i1-0"
ENVIRONMENT = Path.home() / ".local/share/workbench/image-worker/i0/venv"
SPEC = json.loads(Path(__file__).with_name("trial.json").read_text())
POLICY = SPEC["resource"]


def verify() -> None:
    manifest = json.loads((EVIDENCE / "manifest.json").read_text())
    for name, digest in manifest["files"].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise RuntimeError("Frozen source changed: " + name)
    for name in ("worker.py", "trial.json"):
        if Path(__file__).with_name(name).read_bytes() != (PRIVATE / "source" / name).read_bytes():
            raise RuntimeError("Private trial source differs")
    expected_runtime = json.loads((EVIDENCE / "production-before.json").read_text())["ollama"]
    if control.get_json("http://127.0.0.1:11434/api/version") != expected_runtime:
        raise RuntimeError("Ollama version changed; stop this frozen comparison")


def write_new(path: Path, value: dict | list) -> None:
    with path.open("x") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def residency() -> dict:
    data = control.get_json("http://127.0.0.1:11434/api/ps")
    target = SPEC["chat_probe"]["model"]
    matching = [
        row for row in data["models"] if row.get("name") == target or row.get("model") == target
    ]
    return {"target": target, "loaded": bool(matching), "models": data["models"]}


def check_prior(stage: str) -> None:
    index = POLICY["stage_order"].index(stage)
    if index:
        prior = json.loads(
            (EVIDENCE / (POLICY["stage_order"][index - 1] + "-summary.json")).read_text()
        )
        if not prior["passed"]:
            raise RuntimeError("Previous guard failed; stop without retry")
    if (EVIDENCE / (stage + "-summary.json")).exists():
        raise RuntimeError("Stage already recorded; refuse an unretained retry")


def chat(stage: str) -> None:
    before = residency()
    # Avoid evicting an unrelated loaded model or silently refreshing absent
    # residency after the image batch. No management request is sent.
    target = SPEC["chat_probe"]["model"]
    unrelated = [
        row for row in before["models"] if row.get("name") != target and row.get("model") != target
    ]
    if unrelated or (stage == "chat-after" and not before["loaded"]):
        summary = {
            "stage": stage,
            "passed": False,
            "loaded_before": before,
            "reason": "unqualified_other_model_or_expired_residency",
            "request_sent": False,
        }
        write_new(EVIDENCE / (stage + "-summary.json"), summary)
        raise RuntimeError(summary["reason"])
    started = time.monotonic()
    request = urllib.request.Request(
        "http://127.0.0.1:11434/api/chat",
        data=json.dumps(SPEC["chat_probe"]).encode(),
        headers={"Content-Type": "application/json"},
    )
    answer = None
    error = None
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            answer = json.load(response)
    except Exception as caught:
        error = type(caught).__name__
    elapsed = time.monotonic() - started
    after = residency()
    passed = not error and probe_ok(answer, elapsed, POLICY, after["loaded"])
    summary = {
        "stage": stage,
        "passed": passed,
        "payload": SPEC["chat_probe"],
        "answer": answer,
        "error": error,
        "elapsed_seconds": elapsed,
        "loaded_before": before,
        "loaded_after": after,
    }
    write_new(EVIDENCE / (stage + "-summary.json"), summary)
    print(json.dumps({"stage": stage, "passed": passed, "seconds": elapsed}), flush=True)
    if not passed:
        raise RuntimeError("Chat probe failed; stop")


def native(stage: str) -> None:
    before = residency()
    if not before["loaded"]:
        write_new(
            EVIDENCE / (stage + "-summary.json"),
            {
                "stage": stage,
                "passed": False,
                "reason": "residency_absent",
                "loaded_before": before,
            },
        )
        raise RuntimeError("Chat residency absent; no native worker started")
    cases = [row for row in SPEC["cases"] if row["id"] in POLICY["generation_cases"]]
    requests = [{"case": cases[0]["id"], "prompt": cases[0]["prompt"], "seed": 42}]
    if stage == "recovery-batch":
        requests = [
            {"case": row["id"], "prompt": row["prompt"], "seed": seed}
            for row in cases
            for seed in SPEC["seeds"]
        ]
    (EVIDENCE / "requests").mkdir(exist_ok=True)
    request_file = EVIDENCE / "requests" / (stage + ".json")
    write_new(request_file, requests)
    (PRIVATE / "requests").mkdir(exist_ok=True)
    private_request = PRIVATE / "requests" / request_file.name
    if private_request.exists():
        raise RuntimeError("Refusing to overwrite a private request")
    shutil.copy2(request_file, private_request)
    snapshot = json.loads((ROOT / "artifacts/image-trial/i0/model-download.json").read_text())[
        "snapshot"
    ]
    output = PRIVATE / "outputs" / stage
    command = [
        str(ENVIRONMENT / "bin/python"),
        str(PRIVATE / "source/worker.py"),
        "--model-path",
        snapshot,
        "--requests",
        str(private_request),
        "--output",
        str(output),
    ]
    env = {
        key: os.environ[key]
        for key in ("HOME", "PATH", "TMPDIR", "LANG", "LC_CTYPE")
        if key in os.environ
    }
    env.update(
        {
            "HF_HUB_OFFLINE": "1",
            "HF_HUB_DISABLE_TELEMETRY": "1",
            "TOKENIZERS_PARALLELISM": "false",
            "PYTHONUNBUFFERED": "1",
            "HF_HOME": str(Path.home() / ".local/share/workbench/models/image/huggingface"),
            "MFLUX_CACHE_DIR": str(PRIVATE / "cache"),
        }
    )
    original_sample = control.sample
    baseline = original_sample(os.getpid())

    def measured(pid):
        data = original_sample(pid)
        try:
            data["human_work_active"] = bool(
                control.get_json("http://127.0.0.1:8787/api/runs/active")
            ) or bool(
                control.get_json("http://127.0.0.1:8787/api/transcription/audio-storage")[
                    "active_files"
                ]
            )
        except Exception as error:
            data["activity_error"] = type(error).__name__
        return data

    sampler = ResourceSampler(measured, swap_mib(baseline["swap"]), POLICY)
    started_epoch_ms = time.time_ns() // 1_000_000
    control.sample = sampler
    result = None
    error = None
    try:
        result = control.supervise(
            command,
            EVIDENCE / "sessions" / stage,
            cwd=PRIVATE,
            env=env,
            timeout=POLICY["worker_timeout_seconds"],
            grace=SPEC["measurement"]["terminate_grace_seconds"],
            cancel_on={
                "cancel-init": "initialization_start",
                "cancel-generation": "generation_progress",
            }.get(stage),
            cancel_delay=0.5 if stage == "cancel-init" else 0,
        )
    except Exception as caught:
        error = {"type": type(caught).__name__, "message": str(caught)}
    finally:
        control.sample = original_sample
    after = residency()
    finished_epoch_ms = time.time_ns() // 1_000_000
    if output.exists():
        (EVIDENCE / "images").mkdir(exist_ok=True)
        shutil.copytree(output, EVIDENCE / "images" / stage)
    events = []
    try:
        events = [
            json.loads(line)
            for line in (EVIDENCE / "sessions" / stage / "events.jsonl").read_text().splitlines()
        ]
    except Exception as caught:
        if error is None:
            error = {"type": type(caught).__name__, "message": str(caught)}
    passed = False
    expected_cancel = stage.startswith("cancel-")
    try:
        if error or sampler.problems or not after["loaded"] or not result:
            raise RuntimeError("Supervision/resource/residency guard failed")
        if expected_cancel:
            passed = (
                result["termination_signalled"]
                and result["worker_reaped"]
                and result["process_absent_after_reap"]
                and not result["completed_jobs"]
                and result["exit_code"] != 0
                and not result["timed_out"]
            )
        else:
            expected = [f"{row['case']}-{row['seed']}" for row in requests]
            if not result["success"] or result["completed_jobs"] != expected:
                raise RuntimeError("Incomplete worker/output batch")
            for job in expected:
                metadata = control.validate_output(output, job)
                if metadata["generate_seconds"] > POLICY["maximum_generation_seconds"]:
                    raise RuntimeError("Image latency guard failed")
                progress = [
                    e["completed_steps"]
                    for e in events
                    if e["type"] == "generation_progress" and e["job"] == job
                ]
                presence = [e for e in events if e["type"] == "chat_residency" and e["job"] == job]
                if (
                    progress != [1, 2, 3, 4]
                    or [e["when"] for e in presence] != ["before", "after"]
                    or not all(e["loaded"] for e in presence)
                ):
                    raise RuntimeError("Incomplete actual progress/residency evidence")
                if metadata["cache_limit_verified_bytes"] != POLICY["cache_limit_bytes"]:
                    raise RuntimeError("Cache setting mismatch")
            passed = True
    except Exception as caught:
        if error is None:
            error = {"type": type(caught).__name__, "message": str(caught)}
    summary = {
        "stage": stage,
        "passed": passed,
        "expected_cancel": expected_cancel,
        "started_epoch_ms": started_epoch_ms,
        "finished_epoch_ms": finished_epoch_ms,
        "baseline_sample": baseline,
        "resource_violations": sampler.problems,
        "safety_signal_sent": sampler.signal_sent,
        "result": result,
        "loaded_before": before,
        "loaded_after": after,
        "error": error,
    }
    write_new(EVIDENCE / (stage + "-summary.json"), summary)
    print(
        json.dumps(
            {
                "stage": stage,
                "passed": passed,
                "resource_violations": sampler.problems,
                "seconds": result["elapsed_seconds"] if result else None,
            }
        ),
        flush=True,
    )
    if not passed:
        raise RuntimeError("Native memory-policy guard failed; stop and retain all outcomes")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=POLICY["stage_order"])
    args = parser.parse_args()
    verify()
    control.require_idle()
    check_prior(args.stage)
    if args.stage.startswith("chat-"):
        chat(args.stage)
    else:
        native(args.stage)


if __name__ == "__main__":
    main()
