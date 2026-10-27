"""Freeze the candidate, then run the two required gates without source edits."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent


def main():
    old = json.loads((OUT / "executed-source.json").read_text())
    frozen = {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        for name in old
    }
    (OUT / "executed-source.json").write_text(json.dumps(frozen, indent=2) + "\n")
    backup = OUT / "make-check-before-final-qa.log"
    assert not backup.exists(), "Retain earlier logs before rerunning this controller"
    shutil.copyfile(OUT / "make-check-final.log", backup)
    for command, filename in [(["make", "check"], "make-check-final.log"), (["make", "e2e"], "make-e2e-final.log")]:
        with (OUT / filename).open("w") as output:
            result = subprocess.run(command, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT)
        print(json.dumps({"command": command, "exit_code": result.returncode}), flush=True)
        if result.returncode:
            raise SystemExit(result.returncode)
        assert all(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest for name, digest in frozen.items())
        if command == ["make", "check"]:
            result = subprocess.run(["server/.venv/bin/python", "scripts/measure_bundle.py"], cwd=ROOT, capture_output=True, text=True)
            (OUT / "bundle-final.json").write_text(result.stdout)
            result.check_returncode()


if __name__ == "__main__":
    main()
