"""Freeze exactly one FLUX acceptance invocation; no inference/download."""

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
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024**2), b""):
            digest.update(block)
    return digest.hexdigest()


def write(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--preparation", type=Path, required=True)
    args = parser.parse_args()
    root = args.root
    root.mkdir(mode=0o700, parents=True, exist_ok=False)
    old = BASE / "qa/photo-editing-local-20261023"
    scope = json.loads((old / "scope.json").read_text())
    assert all(sha(old / n) == h for n, h in scope["files"].items())
    home = root / "worker"
    home.mkdir()
    for path in HERE.glob("*.py"):
        shutil.copyfile(path, home / path.name)
    previous = old / "hat/worker"
    for name in (
        "flux_worker.py",
        "masked_edit.py",
        "reference_contract.py",
        "reference_codec.py",
        ".python",
    ):
        shutil.copyfile(previous / name, home / name)
    spec = json.loads((previous / "pair.json").read_text())
    spec["checkpoint"] = "PE6 single overlap acceptance"
    spec["order"] = ["flux"]
    spec["engines"] = {"flux": spec["engines"]["flux"]}
    spec["maximum_native_invocations"] = 1
    write(home / "pair.json", spec)
    job = root / "flux"
    shutil.copytree(old / "hat/flux/inputs", job / "inputs")
    request = json.loads((old / "hat/flux/input.json").read_text())
    request["selection"] = json.loads((args.preparation / "selection.json").read_text())
    write(job / "input.json", request)
    for name in ("head-mask.png", "protected-features.png"):
        shutil.copyfile(args.preparation / name, root / name)
    python = (home / ".python").read_text().strip()
    subprocess.run(
        [
            python,
            "-c",
            "import json,sys;from PIL import Image,ImageDraw;r=json.load(open(sys.argv[1]));m=Image.new('L',(1536,2048),0);ImageDraw.Draw(m).polygon([tuple(p) for p in r['face_polygon']],fill=255);m.save(sys.argv[2])",
            str(old / "baseline/regions.json"),
            str(root / "original-face.png"),
        ],
        check=True,
    )
    retained = root / "retained"
    retained.mkdir()
    recorded = json.loads(
        (REPO / "artifacts/photo-editing/pe5-local-20261023/results.json").read_text()
    )
    for part in ("front", "rear"):
        image = old / part / "flux/working/image.png"
        assert sha(image) == recorded["per_region"][part]["flux"]["output_sha256"]
        shutil.copyfile(image, retained / f"{part}.png")
        shutil.copyfile(old / part / "flux/cpu-mask.png", retained / f"{part}-mask.png")
    subprocess.run(
        [python, str(HERE / "audit.py"), "preflight", "--root", str(root)], check=True
    )
    locations = json.loads((old / "hat/model-locations.json").read_text())
    write(root / "model-locations.json", {"flux": locations["flux"]})
    models = json.loads((old / "model-files.json").read_text())
    snapshot = Path(locations["flux"])
    assert {
        str(p.relative_to(snapshot)) for p in snapshot.rglob("*") if p.is_file()
    } == set(models["flux"])
    assert all(
        (snapshot / n).stat().st_size == v["bytes"] and sha(snapshot / n) == v["sha256"]
        for n, v in models["flux"].items()
    )
    write(root / "model-files.json", models)
    print(
        json.dumps({"stage": "existing_flux_reverified", "files": len(models["flux"])}),
        flush=True,
    )
    engine_files = json.loads((old / "hat/frozen.json").read_text())["engine_files"]
    assert all(sha(Path(n)) == h for n, h in engine_files.items())
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
        "maximum_native_invocations": 1,
    }
    write(root / "frozen.json", frozen)
    write(
        root / "approval.json",
        {
            "basis": "User accepted one correction and bounded acceptance check, 23 October 2026; PE6 plan",
            "maximum_native_invocations": 1,
            "frozen_sha256": sha(root / "frozen.json"),
        },
    )
    for path in root.rglob("*"):
        if path.is_file():
            path.chmod(0o600)
    print(
        json.dumps(
            {
                "stage": "frozen",
                "source_input_files": len(frozen["files"]),
                "maximum_native_invocations": 1,
                "native_calls": 0,
            }
        )
    )


if __name__ == "__main__":
    main()
