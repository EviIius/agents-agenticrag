"""Unprivileged invented SQLite tests and named helper's non-data manifest/symbol audit."""

import argparse
import json
import subprocess
from pathlib import Path


def check(build: Path) -> dict:
    fixtures = subprocess.run(
        [str(build / "StoreFixtures")], capture_output=True, timeout=15, check=True
    )
    assert not fixtures.stderr
    result = json.loads(fixtures.stdout)
    assert result["real_store_access"] is False and result["model_calls"] == 0
    executable = build / "Aether Messages Reader.app/Contents/MacOS/MessagesReader"
    manifest = json.loads(subprocess.check_output([str(executable), "--manifest"]))
    assert manifest["identity"] == "dev.agenticrag.aether.messages-reader"
    assert manifest["operations"] == ["resolve_self", "read_thread"]
    assert manifest["read_only"] is True and manifest["input_or_send"] is False
    for argument in ["--send", "--list-chats", "--fixture", "--script"]:
        refused = subprocess.run([str(executable), argument], capture_output=True, timeout=5)
        assert refused.returncode == 64 and not refused.stdout and not refused.stderr
    symbols = subprocess.check_output(["/usr/bin/nm", "-u", str(executable)]).decode()
    for forbidden in [
        "_AXUIElement",
        "_AXIsProcessTrusted",
        "_NSAppleScript",
        "_CGEventPost",
        "_CGWindowList",
        "_NSURLSession",
        "_system",
        "_popen",
    ]:
        assert forbidden not in symbols, forbidden
    binary = executable.read_bytes()
    assert b"CREATE TABLE chat" not in binary and b"INSERT INTO message" not in binary
    return {
        "database_cases": result["passed"],
        "manifest_and_symbol_audit": True,
        "forbidden_entrypoints_refused": 4,
        "real_store_access": False,
        "model_calls": 0,
        "cases": result["cases"],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(check(args.build), indent=2))
