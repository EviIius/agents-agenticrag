"""Freeze a fresh approved pair; CPU preparation and weight hashing, no inference."""

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


def sha(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024**2), b""):
            value.update(chunk)
    return value.hexdigest()


def write(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")
    path.chmod(0o600)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    root = args.root
    root.mkdir(mode=0o700, parents=True, exist_ok=False)
    old = BASE / "qa/photo-editing-pe3-20261022"
    masks = BASE / "qa/photo-editing-pe4-20261022"
    home = root / "worker"
    home.mkdir(mode=0o700)
    for name in (
        "run.py",
        "control.py",
        "flux_worker.py",
        "qwen_worker.py",
        "pair.json",
        "trial.json",
        "prepare.py",
        "cpu_preflight.py",
    ):
        shutil.copyfile(HERE / name, home / name)
    for name in ("masked_edit.py", "reference_contract.py", "reference_codec.py"):
        shutil.copyfile(HERE.parent / "product" / name, home / name)
    shutil.copyfile(BASE / "image-worker/product/.python", home / ".python")
    python = (home / ".python").read_text().strip()
    request = json.loads((old / "private/input.json").read_text())
    request["selection"] = json.loads((masks / "selection.json").read_text())
    for case in ("flux", "qwen"):
        job = root / case
        job.mkdir(mode=0o700)
        shutil.copytree(old / "private/inputs", job / "inputs")
        write(job / "input.json", request)
    shutil.copyfile(masks / "regions.json", root / "regions.json")
    shutil.copyfile(masks / "coverage.json", root / "previous-coverage.json")
    subprocess.run([python, str(home / "cpu_preflight.py"), str(root)], check=True)
    locations = {
        "flux": json.loads((BASE / "image-worker/product/config.json").read_text())[
            "model_path"
        ],
        "qwen": json.loads((old / "download.json").read_text())["snapshot"],
    }
    write(root / "model-locations.json", locations)
    spec = json.loads((home / "pair.json").read_text())
    flux_expected = json.loads(
        (REPO / "artifacts/image-trial/i0/model-download.json").read_text()
    )["files"]
    qwen_expected = json.loads(
        (HERE.parent / "masked_trial/model-files.json").read_text()
    )["files"]
    verified = {}
    for case, location in locations.items():
        model = Path(location)
        assert model.name == spec["engines"][case]["revision"]
        files = {
            str(p.relative_to(model)): {"bytes": p.stat().st_size, "sha256": sha(p)}
            for p in sorted(model.rglob("*"))
            if p.is_file()
        }
        if case == "flux":
            assert files == flux_expected
        else:
            assert set(files) == {item["path"] for item in qwen_expected}
            for item in qwen_expected:
                record = files[item["path"]]
                assert record["bytes"] == item["bytes"]
                if item["sha256"]:
                    assert record["sha256"] == item["sha256"]
                else:
                    raw = (model / item["path"]).read_bytes()
                    assert (
                        hashlib.sha1(
                            b"blob " + str(len(raw)).encode() + b"\0" + raw
                        ).hexdigest()
                        == item["git_blob_sha1"]
                    )
        verified[case] = files
        print(
            json.dumps(
                {
                    "stage": "verified_existing_checkpoint",
                    "engine": case,
                    "files": len(files),
                    "bytes": sum(f["bytes"] for f in files.values()),
                }
            ),
            flush=True,
        )
    write(root / "model-files.json", verified)
    # Locate package source without importing MLX/MFLUX or reading more weights.
    package = subprocess.check_output(
        [
            python,
            "-c",
            "import importlib.metadata;print(importlib.metadata.distribution('mflux').locate_file('mflux'))",
        ],
        text=True,
    ).strip()
    engine_files = {str(p): sha(p) for p in sorted(Path(package).rglob("*.py"))}
    engine_files.update(
        {str(p): sha(p) for p in sorted((REPO / "server/app").rglob("*.py"))}
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
    frozen = {
        "files": {
            str(p.relative_to(root)): sha(p)
            for p in sorted(root.rglob("*"))
            if p.is_file()
        },
        "engine_files": engine_files,
        "maximum_native_invocations": 2,
    }
    write(root / "frozen.json", frozen)
    write(
        root / "approval.json",
        {
            "basis": "Explicit corrected-mask comparison approval in current conversation; 23 October 2026",
            "maximum_native_invocations": 2,
            "frozen_sha256": sha(root / "frozen.json"),
        },
    )
    for p in root.rglob("*"):
        if p.is_file():
            p.chmod(0o600)
    print(
        json.dumps(
            {
                "stage": "frozen",
                "source_input_files": len(frozen["files"]),
                "engine_source_files": len(engine_files),
                "native_calls": 0,
                "maximum_native_invocations": 2,
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
