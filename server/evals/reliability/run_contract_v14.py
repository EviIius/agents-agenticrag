"""Predeclared original-case smoke; fail closed before any later inference."""

import argparse
import hashlib
import importlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

SERVER = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SERVER))
from evals.models.run_comparison import child, get, verify_inputs  # noqa: E402

REPO = SERVER.parent
FOLDER = REPO / "artifacts/reliability/evidence-v14"
MODEL = "qwen3:30b-a3b-workbench-32k"


def verify():
    verify_inputs()
    manifest = json.loads((FOLDER / "manifest.json").read_text())
    for name, expected in manifest["files"].items():
        if hashlib.sha256((REPO / name).read_bytes()).hexdigest() != expected:
            raise RuntimeError("Frozen named-field experiment changed: " + name)


def isolated(suite, arguments, trace):
    location = SERVER / "evals/reliability/trials/evidence-v14/app"
    for name in ("runs", "search", "library"):
        package = importlib.import_module("app." + name)
        package.__path__.insert(0, str(location / name))
    from evals.reliability.contract_stream_v14 import install

    install(trace + "-selections.jsonl")
    child(suite, arguments, trace)


def check_gate(stage):
    if stage != "smoke":
        gate = json.loads((FOLDER / "smoke-review.json").read_text())
        if any(
            gate.get(key) is not True for key in ("protocol_pass", "rubric_pass", "semantic_pass")
        ):
            raise RuntimeError("Smoke failed; subsequent stages prohibited")
    if stage == "library":
        gate = json.loads((FOLDER / "web-review.json").read_text())
        if gate.get("all_release_and_semantic_gates") is not True:
            raise RuntimeError("Web qualification failed; Library prohibited")


def main(stage):
    verify()
    check_gate(stage)
    output = FOLDER / (stage + "-index.json")
    if output.exists():
        raise RuntimeError("Never overwrite or retry a retained trial")
    if get("http://127.0.0.1:8787/api/runs/active"):
        raise RuntimeError("Human inference active; stop")
    if get("http://127.0.0.1:8787/api/transcription/audio-storage")["active_files"]:
        raise RuntimeError("Human transcription active; stop")
    suite = "library" if stage == "library" else "web"
    arguments = ["--model", MODEL]
    if suite == "web":
        arguments += [
            "--replay-corpus",
            "--fixture-root",
            str(SERVER / "evals/web/fixtures/phase2-final-corpus"),
            "--search-key-db",
            str(Path.home() / ".local/share/workbench/data/workbench.db"),
        ]
        arguments += (
            ["--case", "nba-2021"]
            if stage == "smoke"
            else ["--cases-file", str(FOLDER / "remaining-web-cases.json")]
        )
    reports = SERVER / "evals" / suite / "reports"
    before = set(reports.glob("*.json"))
    record = {"stage": stage, "model": MODEL, "started_utc": datetime.now(UTC).isoformat()}
    command = [
        sys.executable,
        str(Path(__file__)),
        "--child",
        suite,
        "--trace",
        str(FOLDER / (stage + "-streams.jsonl")),
        "--",
        *arguments,
    ]
    try:
        with (FOLDER / (stage + ".log")).open("x") as log:
            result = subprocess.run(command, cwd=SERVER, stdout=log, stderr=subprocess.STDOUT)
        record["exit_code"] = result.returncode
        record["reports"] = [
            str(p.relative_to(REPO)) for p in sorted(set(reports.glob("*.json")) - before)
        ]
        if result.returncode or not record["reports"]:
            raise RuntimeError("Trial failed; retained trace requires review, no next stage")
    except BaseException as exc:
        record["execution_error"] = str(exc)
        raise
    finally:
        record["finished_utc"] = datetime.now(UTC).isoformat()
        output.write_text(json.dumps(record, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("smoke", "remaining-web", "library"))
    parser.add_argument("--child", choices=("web", "library"))
    parser.add_argument("--trace")
    args, remaining = parser.parse_known_args()
    verify()
    if args.child:
        isolated(args.child, remaining[1:] if remaining[:1] == ["--"] else remaining, args.trace)
    elif args.stage and not remaining:
        main(args.stage)
    else:
        parser.error("Provide one stage or a child suite")
