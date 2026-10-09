"""Retain repair trials with the original suites and real installed profiles."""

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from time import monotonic

SERVER = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SERVER))
from evals.models.run_comparison import child, get, snapshot, verify_inputs  # noqa: E402

REPO = SERVER.parent
MODELS = ["qwen3:30b-a3b-workbench-32k", "qwen3.8:27b-atelier-eval-32k"]


def isolated_child(version: str, suite: str, trace: str, arguments: list[str]) -> None:
    """Load retained alternative modules before importing the application."""
    import importlib
    import runpy

    manifest = json.loads((REPO / "artifacts/reliability" / version / "manifest.json").read_text())
    if not manifest.get("module_override"):
        raise RuntimeError("v1 is source-archived; the current loader supports isolated v2+ only")
    if manifest.get("module_override"):
        location = SERVER / "evals/reliability/trials" / version / "app"
        for name in ("runs", "search", "library"):
            package = importlib.import_module("app." + name)
            if (location / name).is_dir():
                package.__path__.insert(0, str(location / name))
    if suite == "everyday":
        target = SERVER / "evals/models/run_everyday.py"
        sys.argv = [str(target), *arguments]
        runpy.run_path(str(target), run_name="__main__")
    else:
        child(suite, arguments, trace)


def main(version: str, repeat: int, profile: str) -> None:
    folder = REPO / "artifacts/reliability" / version
    manifest = json.loads((folder / "manifest.json").read_text())
    if not manifest.get("module_override"):
        raise RuntimeError("v1 is source-archived; the current loader supports isolated v2+ only")
    index = folder / f"run-{repeat}-{profile}-index.json"
    if index.exists():
        raise RuntimeError("Never overwrite or retry a retained trial")
    records = []
    document = {"version": version, "repeat": repeat, "results": records}
    order = MODELS if repeat % 2 else list(reversed(MODELS))
    if profile != "both":
        order = [MODELS[0 if profile == "baseline" else 1]]
    try:
        for model in order:
            name = "baseline" if model == MODELS[0] else "candidate"
            for suite in ("everyday", "web", "library"):
                verify_inputs()
                for path, expected in manifest["files"].items():
                    if hashlib.sha256((REPO / path).read_bytes()).hexdigest() != expected:
                        raise RuntimeError("Frozen repair trial changed: " + path)
                if get("http://127.0.0.1:8787/api/runs/active"):
                    raise RuntimeError("Human inference active; no new evaluation suite")
                if get("http://127.0.0.1:8787/api/transcription/audio-storage")["active_files"]:
                    raise RuntimeError("Human transcription active; no new evaluation suite")
                label = f"run-{repeat}-{name}-{suite}"
                report_folder = SERVER / "evals" / suite / "reports"
                previous = set(report_folder.glob("*.json"))
                arguments = ["--model", model]
                if suite == "everyday":
                    output = folder / (label + ".json")
                    arguments += ["--label", version + "-" + label, "--output", str(output)]
                else:
                    if suite == "web":
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
                    "--version",
                    version,
                    "--child",
                    suite,
                    "--trace",
                    str(folder / (label + "-streams.jsonl")),
                    "--",
                ]
                print("Starting " + version + "/" + label, flush=True)
                before = snapshot()
                started = monotonic()
                with (folder / (label + ".log")).open("x") as log:
                    result = subprocess.run(
                        command + arguments, cwd=SERVER, stdout=log, stderr=subprocess.STDOUT
                    )
                paths = (
                    [output]
                    if suite == "everyday"
                    else sorted(set(report_folder.glob("*.json")) - previous)
                )
                entry = {
                    "label": label,
                    "model": model,
                    "suite": suite,
                    "exit_code": result.returncode,
                    "elapsed_seconds": monotonic() - started,
                    "reports": [str(p.relative_to(REPO)) for p in paths if p.exists()],
                    "before": before,
                    "after": snapshot(),
                }
                records.append(entry)
                index.write_text(json.dumps(document, indent=2) + "\n")
                print(
                    json.dumps({k: entry[k] for k in ("label", "exit_code", "reports")}), flush=True
                )
                if not entry["reports"]:
                    raise RuntimeError("Harness setup failure; retained log, no silent restart")
        document["execution_complete"] = True
    except BaseException as exc:
        document["execution_error"] = str(exc)
        raise
    finally:
        document["finished_utc"] = datetime.now(UTC).isoformat()
        index.write_text(json.dumps(document, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--repeat", type=int, choices=(1, 2, 3))
    parser.add_argument("--child", choices=("everyday", "web", "library"))
    parser.add_argument("--trace", default="")
    parser.add_argument("--profile", choices=("baseline", "candidate", "both"), default="both")
    args, remaining = parser.parse_known_args()
    if args.child:
        isolated_child(
            args.version,
            args.child,
            args.trace,
            remaining[1:] if remaining[:1] == ["--"] else remaining,
        )
    else:
        if args.repeat is None or remaining:
            parser.error("Provide --repeat and no unknown arguments")
        main(args.version, args.repeat, args.profile)
