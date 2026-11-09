"""Compare Python/compiled metadata guards on invented fixtures; no native app access."""

import argparse
import copy
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
from tests.test_mac_metadata import candidate, metadata_cases


def check(build: Path) -> dict:
    executable = build / "Aether Desktop Trial.app/Contents/MacOS/DesktopTrial"
    cases = []

    def run(name: str, args: list[str], data: object = None, valid: bool = True) -> bytes:
        result = subprocess.run(
            [str(executable), *args],
            input=json.dumps(data).encode() if data is not None else b"",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
            check=False,
        )
        assert result.returncode == (0 if valid else 64), name
        assert not result.stderr, name
        if not valid:
            assert not result.stdout, name
        cases.append({"case": name, "passed": True})
        return result.stdout

    manifest = json.loads(run("manifest", ["--manifest"]))
    assert manifest == {
        "protocol": 3,
        "access": "read_only",
        "operations": ["inspect_metadata"],
        "body_reading": False,
        "qualified_conversation": False,
        "input_actions": False,
        "screenshots": False,
    }
    for name, value, valid in metadata_cases():
        run(name, ["--metadata-fixture"], {"before": value, "after": value}, valid)
    changed = copy.deepcopy(candidate())
    changed["items"][1]["fields"]["AXIdentifier"] = "Changed invented ID"
    run(
        "changed-container-metadata",
        ["--metadata-fixture"],
        {"before": candidate(), "after": changed},
        False,
    )
    with tempfile.TemporaryDirectory(prefix="aether-metadata-offline-") as temporary:
        directory = Path(temporary).resolve()
        os.chmod(directory, 0o700)
        file = directory / "request.json"
        base = {
            "protocol": 3,
            "request_id": "a" * 32,
            "operation": "inspect_metadata",
            "app": "messages",
            "expires_at": time.time() + 14,
        }
        for name, changes, valid in [
            ("valid-job", {}, True),
            ("no-body-read", {"operation": "read_selected"}, False),
            ("no-send", {"operation": "send"}, False),
            ("no-other-app", {"app": "notes"}, False),
            ("no-bool-version", {"protocol": True}, False),
            ("no-fraction-version", {"protocol": 3.5}, False),
            ("expired", {"expires_at": time.time() - 1}, False),
            ("extra-argument", {"script": "synthetic"}, False),
        ]:
            file.write_text(json.dumps(base | changes))
            os.chmod(file, 0o600)
            run(name, ["--validate-job", str(directory)], valid=valid)
    run("no-input-mode", ["--send"], valid=False)
    symbols = subprocess.check_output(["/usr/bin/nm", "-u", str(executable)]).decode()
    for symbol in (
        "_AXUIElementSetAttributeValue",
        "_AXUIElementPerformAction",
        "_CGEventPost",
        "_NSAppleScript",
        "_AXUIElementCopyParameterizedAttributeValue",
    ):
        assert symbol not in symbols, symbol
    return {"passed": len(cases), "native_jobs": 0, "model_calls": 0, "cases": cases}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(check(args.build), indent=2))
