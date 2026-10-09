"""Frozen full-pipeline pilot; ordinary answers retain the installed contract."""

import argparse
import hashlib
import importlib
import json
import runpy
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

SERVER = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SERVER))
from evals.models.run_comparison import child, get, verify_inputs  # noqa: E402

REPO = SERVER.parent
FOLDER = REPO / "artifacts/reliability/evidence-v11"
MODELS = ["qwen3:30b-a3b-workbench-32k", "qwen3.8:27b-atelier-eval-32k"]


def verify():
    verify_inputs()
    manifest = json.loads((FOLDER / "manifest.json").read_text())
    for name, expected in manifest["files"].items():
        if hashlib.sha256((REPO / name).read_bytes()).hexdigest() != expected:
            raise RuntimeError("Frozen evidence pilot changed: " + name)


def isolated(suite, arguments, trace):
    location = SERVER / "evals/reliability/trials/evidence-v11/app"
    for name in ("runs", "search", "library"):
        package = importlib.import_module("app." + name)
        package.__path__.insert(0, str(location / name))
    from evals.reliability.contract_stream_v11 import install

    install(trace + "-selections.jsonl")
    if suite == "everyday":
        target = SERVER / "evals/models/run_everyday.py"
        sys.argv = [str(target), *arguments]
        runpy.run_path(str(target), run_name="__main__")
    else:
        child(suite, arguments, trace)


def main(profile):
    output = FOLDER / (profile + "-index.json")
    if output.exists():
        raise RuntimeError("Never overwrite a retained pilot")
    report = {"profile": profile, "results": [], "started_utc": datetime.now(UTC).isoformat()}
    try:
        for suite in ("web", "library"):
            verify()
            if get("http://127.0.0.1:8787/api/runs/active"):
                raise RuntimeError("Human inference active; stop")
            if get("http://127.0.0.1:8787/api/transcription/audio-storage")["active_files"]:
                raise RuntimeError("Human transcription active; stop")
            model = MODELS[0 if profile == "baseline" else 1]
            label = profile + "-" + suite
            arguments = ["--model", model]
            reports = SERVER / "evals" / suite / "reports"
            prior = set(reports.glob("*.json"))
            result_file = FOLDER / (label + ".json")
            if suite == "everyday":
                arguments += ["--label", "evidence-v11-" + label, "--output", str(result_file)]
            elif suite == "web":
                arguments += [
                    "--replay-corpus",
                    "--fixture-root",
                    str(SERVER / "evals/web/fixtures/phase2-final-corpus"),
                    "--search-key-db",
                    str(Path.home() / ".local/share/workbench/data/workbench.db"),
                ]
            command = [
                sys.executable,
                str(Path(__file__)),
                "--child",
                suite,
                "--trace",
                str(FOLDER / (label + "-streams.jsonl")),
                "--",
                *arguments,
            ]
            print("Starting " + label, flush=True)
            with (FOLDER / (label + ".log")).open("x") as log:
                result = subprocess.run(command, cwd=SERVER, stdout=log, stderr=subprocess.STDOUT)
            generated = (
                [result_file]
                if suite == "everyday"
                else sorted(set(reports.glob("*.json")) - prior)
            )
            report["results"].append(
                {
                    "suite": suite,
                    "exit_code": result.returncode,
                    "reports": [str(p.relative_to(REPO)) for p in generated if p.exists()],
                }
            )
            output.write_text(json.dumps(report, indent=2) + "\n")
            if not generated or not any(p.exists() for p in generated):
                raise RuntimeError("No completed report; retain the interrupted pilot")
            print(label + " completed", flush=True)
    except BaseException as exc:
        report["execution_error"] = str(exc)
        raise
    finally:
        report["finished_utc"] = datetime.now(UTC).isoformat()
        output.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=("baseline", "candidate"))
    parser.add_argument("--child", choices=("everyday", "web", "library"))
    parser.add_argument("--trace")
    args, remaining = parser.parse_known_args()
    verify()
    if args.child:
        isolated(args.child, remaining[1:] if remaining[:1] == ["--"] else remaining, args.trace)
    elif args.profile and not remaining:
        main(args.profile)
    else:
        parser.error("Provide one profile or a child suite")
