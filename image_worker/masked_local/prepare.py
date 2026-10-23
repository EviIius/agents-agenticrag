"""Freeze the approved focused comparison, without inference or downloads."""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
BASE = Path.home() / ".local/share/workbench"
sys.path.insert(0, str(REPO / "scripts"))
from prepare_photo_release import inventory

PARTS = ("hat", "front", "rear")


def sha(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024**2), b""):
            result.update(chunk)
    return result.hexdigest()


def write(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--instructions", type=Path, required=True)
    args = parser.parse_args()
    root = args.root
    root.mkdir(mode=0o700, parents=True, exist_ok=False)
    previous = BASE / "qa/photo-editing-pair-20261023"
    previous_frozen = json.loads((previous / "frozen.json").read_text())
    for relative, expected in previous_frozen["files"].items():
        assert sha(previous / relative) == expected
    baseline = root / "baseline"
    baseline.mkdir()
    shutil.copyfile(args.instructions, baseline / "region-instructions.json")
    for source, target in (
        (previous / "flux/input.json", "input.json"),
        (previous / "flux/inputs/reference.png", "reference.png"),
        (previous / "regions.json", "regions.json"),
    ):
        shutil.copyfile(source, baseline / target)
    for part in PARTS:
        pair = root / part
        worker = pair / "worker"
        shutil.copytree(previous / "worker", worker)
        # The workers/controller/launcher and engine recipes remain byte exact.
        for engine in ("flux", "qwen"):
            shutil.copytree(previous / engine / "inputs", pair / engine / "inputs")
        shutil.copyfile(
            previous / "model-locations.json", pair / "model-locations.json"
        )
    python = (root / "hat/worker/.python").read_text().strip()
    subprocess.run(
        [python, str(HERE / "cpu.py"), "prepare", "--root", str(root)], check=True
    )
    models = json.loads((previous / "model-files.json").read_text())
    locations = json.loads((previous / "model-locations.json").read_text())
    for engine, files in models.items():
        snapshot = Path(locations[engine])
        assert {
            str(p.relative_to(snapshot)) for p in snapshot.rglob("*") if p.is_file()
        } == set(files)
        for relative, expected in files.items():
            path = snapshot / relative
            assert (
                path.stat().st_size == expected["bytes"]
                and sha(path) == expected["sha256"]
            )
        print(
            json.dumps(
                {
                    "stage": "verified_existing_checkpoint",
                    "engine": engine,
                    "files": len(files),
                }
            ),
            flush=True,
        )
    write(root / "model-files.json", models)
    sources = root / "scope-source"
    sources.mkdir()
    for path in sorted(HERE.glob("*.py")):
        shutil.copyfile(path, sources / path.name)
    engine_files = previous_frozen["engine_files"]
    for path, expected in engine_files.items():
        assert sha(Path(path)) == expected
    for part in PARTS:
        pair = root / part
        frozen = {
            "files": {
                str(p.relative_to(pair)): sha(p)
                for p in sorted(pair.rglob("*"))
                if p.is_file()
            },
            "engine_files": engine_files,
            "maximum_native_invocations": 2,
        }
        write(pair / "frozen.json", frozen)
        write(
            pair / "approval.json",
            {
                "basis": "New user request for focused quality trials, 23 October 2026; PE5 plan, six calls total",
                "maximum_native_invocations": 2,
                "frozen_sha256": sha(pair / "frozen.json"),
            },
        )
    write(
        root / "preservation-before.json",
        {
            "server": inventory(BASE / "app/server/app"),
            "worker": inventory(BASE / "image-worker/product"),
            "plist": sha(
                Path.home() / "Library/LaunchAgents/dev.agenticrag.workbench.plist"
            ),
        },
    )
    write(
        root / "scope.json",
        {
            "maximum_native_invocations": 6,
            "order": [[p, e] for p in PARTS for e in ("flux", "qwen")],
            "scope_source_sha256": sha(HERE / "scope.py"),
            "files": {
                str(p.relative_to(root)): sha(p)
                for p in sorted(root.rglob("*"))
                if p.is_file()
            },
        },
    )
    for path in root.rglob("*"):
        if path.is_file():
            path.chmod(0o600)
    print(
        json.dumps(
            {"stage": "frozen", "maximum_native_invocations": 6, "native_calls": 0}
        )
    )


if __name__ == "__main__":
    main()
