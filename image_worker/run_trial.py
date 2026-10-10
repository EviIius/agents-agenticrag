"""Execute one declared trial stage; never overwrite evidence or install alternatives."""

import argparse
import hashlib
import json
import os
import shutil
import urllib.request
from pathlib import Path

from control import get_json, require_idle, supervise, validate_output

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "artifacts/image-trial/i0"
WORKER = Path.home() / ".local/share/workbench/image-worker/i0"
SPEC = json.loads((ROOT / "image_worker/trial.json").read_text())


def verify() -> None:
    manifest = json.loads((EVIDENCE / "manifest.json").read_text())
    for name, digest in manifest["source_files"].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise RuntimeError(f"Frozen source changed: {name}")
    for name in ("worker.py", "trial.json"):
        source = ROOT / "image_worker" / name
        installed = WORKER / "source" / name
        if source.read_bytes() != installed.read_bytes():
            raise RuntimeError("Installed trial source mismatch")


def receipt_pass(stage: str, *, cancel: bool = False, fail: bool = False) -> None:
    previous = json.loads((EVIDENCE / "sessions" / stage / "receipt.json").read_text())
    passed = previous["success"]
    if cancel:
        passed = (
            previous["termination_signalled"]
            and previous["worker_reaped"]
            and not previous["completed_jobs"]
        )
    if fail:
        passed = (
            previous["worker_reaped"]
            and previous["exit_code"] != 0
            and not previous["completed_jobs"]
        )
    if not passed:
        raise RuntimeError(f"Previous stage did not pass: {stage}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "stage",
        choices=(
            "bad-input",
            "bad-initialization",
            "cancel-init",
            "cold",
            "cancel-generation",
            "cached",
            "resident",
            "edit",
            "chat-before",
            "chat-after",
        ),
    )
    args = parser.parse_args()
    verify()
    require_idle()
    phase = args.stage
    if phase in ("chat-before", "chat-after"):
        target = EVIDENCE / f"{phase}.json"
        if target.exists():
            raise RuntimeError("Chat probe already recorded")
        import time

        started = time.monotonic()
        request = urllib.request.Request(
            "http://127.0.0.1:11434/api/chat",
            data=json.dumps(SPEC["chat_probe"]).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            answer = json.load(response)
        target.write_text(
            json.dumps(
                {
                    "payload": SPEC["chat_probe"],
                    "answer": answer,
                    "elapsed_seconds": time.monotonic() - started,
                    "loaded_models": get_json("http://127.0.0.1:11434/api/ps"),
                },
                indent=2,
            )
            + "\n"
        )
        print(
            json.dumps(
                {
                    "stage": phase,
                    "reply": answer.get("message", {}).get("content"),
                    "seconds": time.monotonic() - started,
                }
            )
        )
        return
    prior = {
        "bad-initialization": ("bad-input", "fail"),
        "cancel-init": ("bad-initialization", "fail"),
        "cold": ("cancel-init", "cancel"),
        "cancel-generation": ("cold", "success"),
        "cached": ("cancel-generation", "cancel"),
        "resident": ("cached", "success"),
        "edit": ("resident", "success"),
    }
    if phase in prior:
        previous, expected = prior[phase]
        receipt_pass(previous, cancel=expected == "cancel", fail=expected == "fail")
    download = json.loads((EVIDENCE / "model-download.json").read_text())
    snapshot = Path(download["snapshot"])
    photo = {**SPEC["cases"][0], "case": "photograph", "seed": 42}
    photo.pop("id")
    requests = [photo]
    if phase == "bad-input":
        requests = []
    elif phase == "bad-initialization":
        snapshot = WORKER / "broken-snapshot" / SPEC["revision"]
        snapshot.mkdir(parents=True, exist_ok=False)
    elif phase == "cached":
        requests = [{**photo, "seed": 1337}]
    elif phase == "resident":
        requests = [
            {"case": case["id"], "prompt": case["prompt"], "seed": seed}
            for case in SPEC["cases"][1:]
            for seed in SPEC["seeds"]
        ]
    elif phase == "edit":
        reference = WORKER / "outputs/cold/photograph-42.png"
        validate_output(reference.parent, "photograph-42")
        requests = [
            {
                "case": SPEC["edit"]["id"],
                "seed": SPEC["edit"]["seed"],
                "prompt": SPEC["edit"]["prompt"],
                "reference": str(reference),
            }
        ]
    requests_dir = EVIDENCE / "requests"
    requests_dir.mkdir(exist_ok=True)
    request_path = requests_dir / f"{phase}.json"
    with request_path.open("x") as stream:
        json.dump(requests, stream, indent=2)
        stream.write("\n")
    private_requests = WORKER / "requests"
    private_requests.mkdir(exist_ok=True)
    installed_request = private_requests / request_path.name
    if installed_request.exists():
        raise RuntimeError("Refusing to replace installed request")
    shutil.copy2(request_path, installed_request)
    output = WORKER / "outputs" / phase
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
            "HF_HOME": str(Path.home() / ".local/share/workbench/models/image/huggingface"),
            "MFLUX_CACHE_DIR": str(WORKER / "cache"),
            "PYTHONUNBUFFERED": "1",
        }
    )
    command = [
        str(WORKER / "venv/bin/python"),
        str(WORKER / "source/worker.py"),
        "--model-path",
        str(snapshot),
        "--requests",
        str(installed_request),
        "--output",
        str(output),
        "--mode",
        "edit" if phase == "edit" else "generate",
    ]
    result = supervise(
        command,
        EVIDENCE / "sessions" / phase,
        cwd=WORKER,
        env=env,
        timeout=SPEC["measurement"]["worker_timeout_seconds"],
        grace=SPEC["measurement"]["terminate_grace_seconds"],
        cancel_on={
            "cancel-init": "initialization_start",
            "cancel-generation": "generation_progress",
        }.get(phase),
        cancel_delay=0.5 if phase == "cancel-init" else 0,
    )
    expected_failure = phase in ("bad-input", "bad-initialization")
    expected_cancel = phase.startswith("cancel-")
    if expected_failure:
        receipt_pass(phase, fail=True)
    elif expected_cancel:
        receipt_pass(phase, cancel=True)
    elif not result["success"]:
        raise RuntimeError("Image stage failed; stop and retain the outcome")
    else:
        for request in requests:
            validate_output(output, f"{request['case']}-{request['seed']}")
        expected_jobs = [f"{request['case']}-{request['seed']}" for request in requests]
        if result["completed_jobs"] != expected_jobs:
            raise RuntimeError("Missing/unexpected worker output")
    if output.exists():
        evidence_output = EVIDENCE / "images" / phase
        evidence_output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(output, evidence_output)
    memory_after = get_json("http://127.0.0.1:8787/api/health")
    summary = {
        "stage": phase,
        "expected_failure": expected_failure,
        "expected_cancel": expected_cancel,
        "result": {key: value for key, value in result.items() if key != "samples"},
        "app_health_after": memory_after,
        "loaded_models_after": get_json("http://127.0.0.1:11434/api/ps"),
        "disk_free_bytes": shutil.disk_usage(WORKER).free,
        "output_files": [p.name for p in output.iterdir()] if output.exists() else [],
    }
    (EVIDENCE / f"{phase}-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary["result"]))


if __name__ == "__main__":
    main()
