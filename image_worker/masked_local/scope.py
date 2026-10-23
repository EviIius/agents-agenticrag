"""Six-slot focused-edit scope around the unchanged two-slot native controller."""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PARTS = ("hat", "front", "rear")
ORDER = [(part, engine) for part in PARTS for engine in ("flux", "qwen")]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def admitted(root, part, engine):
    frozen = json.loads((root / "scope.json").read_text())
    if frozen["maximum_native_invocations"] != 6 or frozen["order"] != [
        list(pair) for pair in ORDER
    ]:
        raise ValueError("Wrong six-slot scope")
    if sha(Path(__file__)) != frozen["scope_source_sha256"]:
        raise ValueError("Scope source differs from frozen preparation")
    for relative, expected in frozen["files"].items():
        if sha(root / relative) != expected:
            raise ValueError("Scope input/source changed after freezing")
    index = ORDER.index((part, engine))
    reservations = list(root.glob("*/attempts/*.reserved.json"))
    if len(reservations) != index:
        raise ValueError("Wrong order or exhausted allowance")
    for previous_part, previous_engine in ORDER[:index]:
        attempt = root / previous_part / "attempts"
        result = json.loads((attempt / f"{previous_engine}.result.json").read_text())
        review = json.loads((attempt / f"{previous_engine}.quality.json").read_text())
        if (
            not result.get("passed")
            or not result.get("worker_reaped")
            or not review.get("reviewed")
            or review.get("output_sha256") != result.get("output_sha256")
        ):
            raise ValueError("Prior technical pass and output-bound review required")
    return frozen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("part", choices=PARTS)
    parser.add_argument("engine", choices=("flux", "qwen"))
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    admitted(args.root, args.part, args.engine)
    subprocess.run(
        [
            sys.executable,
            str(REPO / "image_worker/masked_pair/run.py"),
            args.engine,
            "--root",
            str(args.root / args.part),
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
