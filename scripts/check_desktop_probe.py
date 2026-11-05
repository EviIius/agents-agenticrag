"""Run only AS1-A manifest/synthetic/file-validation paths. Never a native job."""

import argparse
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path


def check(build: Path) -> dict[str, object]:
    executable = build / "Aether Desktop Trial.app/Contents/MacOS/DesktopTrial"
    cases: list[dict[str, object]] = []

    def run(name: str, args: list[str], data: bytes = b"", code: int = 0) -> bytes:
        result = subprocess.run(
            [str(executable), *args], input=data, capture_output=True, timeout=5, check=False
        )
        assert result.returncode == code, name
        assert not result.stderr, name
        cases.append({"case": name, "exit": result.returncode})
        return result.stdout

    manifest = json.loads(run("manifest", ["--manifest"]))
    assert manifest["text_reading"] is False and manifest["input_actions"] is False
    assert manifest["screenshots"] is False
    secret = "SYNTHETIC-PRIVATE-CONTENT-MUST-NOT-APPEAR"
    tree = {
        "role": "AXWindow",
        "title": secret,
        "children": [
            {"role": secret, "value": secret, "identifier": secret},
            {"role": "AXTextArea", "value": secret},
        ],
    }
    raw = run("redaction", ["--fixture"], json.dumps({"tree": tree}).encode())
    assert secret.encode() not in raw
    nodes = json.loads(raw)["nodes"]
    assert nodes[1]["role"] == "AXUnknown"
    assert all(set(node) == {"path", "role", "children"} for node in nodes)
    deep = {"role": "AXStaticText"}
    for _ in range(12):
        deep = {"role": "AXWindow", "children": [deep]}
    result = json.loads(run("depth", ["--fixture"], json.dumps({"tree": deep}).encode()))
    assert result["truncated"] is True and max(len(n["path"]) for n in result["nodes"]) == 8
    wide = {
        "role": "AXWindow",
        "children": [
            {"role": "AXGroup", "children": [{"role": "AXStaticText"} for _ in range(40)]}
            for _ in range(40)
        ],
    }
    result = json.loads(run("width-count", ["--fixture"], json.dumps({"tree": wide}).encode()))
    assert result["truncated"] is True and len(result["nodes"]) == 160
    assert all(all(index < 32 for index in n["path"]) for n in result["nodes"])
    run("invalid-json", ["--fixture"], b"not JSON", code=64)
    run("oversized-input", ["--fixture"], b" " * 1_048_577, code=64)
    run("unknown-argument", ["--send"], code=64)
    with tempfile.TemporaryDirectory(prefix="aether-as1-offline-") as temporary:
        directory = Path(temporary).resolve()
        os.chmod(directory, 0o700)
        file = directory / "request.json"
        base = {
            "protocol": 1,
            "request_id": "a" * 32,
            "operation": "structure",
            "app": "messages",
            "expires_at": time.time() + 30,
        }
        for name, change, status in [
            ("valid-job", {}, 0),
            ("unknown-field", {"value": secret}, 64),
            ("boolean-version", {"protocol": True}, 64),
            ("forbidden-send", {"operation": "send_reply"}, 64),
            ("forbidden-app", {"app": "safari"}, 64),
            ("expired-job", {"expires_at": time.time() - 1}, 64),
            ("long-job", {"expires_at": time.time() + 300}, 64),
        ]:
            file.write_text(json.dumps({**base, **change}))
            os.chmod(file, 0o600)
            run(name, ["--validate-job", str(directory)], code=status)
        file.write_text(json.dumps(base))
        os.chmod(file, 0o644)
        run("broad-file-permissions", ["--validate-job", str(directory)], code=64)
        file.unlink()
        outside = directory / "elsewhere"
        outside.write_text(json.dumps(base))
        os.chmod(outside, 0o600)
        file.symlink_to(outside)
        run("symlink-job", ["--validate-job", str(directory)], code=64)
    return {"native_jobs": 0, "model_calls": 0, "cases": cases, "passed": len(cases)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", required=True, type=Path)
    options = parser.parse_args()
    print(json.dumps(check(options.build), indent=2))
