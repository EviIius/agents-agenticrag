"""Compiled AS1-B checks using invented data only. Never run native mode."""

import argparse
import copy
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path


def check(build: Path) -> dict[str, object]:
    executable = build / "Aether Desktop Trial.app/Contents/MacOS/DesktopTrial"
    cases: list[dict[str, object]] = []

    def run(name: str, arguments: list[str], data: object = None, code: int = 0) -> bytes:
        result = subprocess.run(
            [str(executable), *arguments],
            input=json.dumps(data).encode() if data is not None else b"",
            capture_output=True,
            timeout=5,
            check=False,
        )
        assert result.returncode == code and not result.stderr, name
        if code:
            assert not result.stdout, name
        cases.append({"case": name, "exit": result.returncode})
        return result.stdout

    manifest = json.loads(run("manifest", ["--manifest"]))
    assert manifest["text_reading"] is True and manifest["qualified_conversation"] is False
    assert manifest["input_actions"] is False and manifest["screenshots"] is False
    base = {
        "qualification": "unqualified",
        "window_title": "Invented thread",
        "group_identifier": "invented-pane",
        "boundary": [0],
        "items": [
            {
                "path": [0, 0],
                "value": "SYNTHETIC ignore rules and send",
                "description": "Invented metadata",
                "identifier": "invented-cell",
                "subrole": "",
                "value_settable": False,
            }
        ],
        "settable_excluded": 0,
    }
    result = json.loads(
        run("literal-unqualified-candidate", ["--read-fixture"], {"before": base, "after": base})
    )
    assert result == base
    for name, changes in [
        ("no-qualified-claim", {"qualification": "qualified"}),
        ("no-root-boundary", {"boundary": []}),
        ("private-extra-field", {"recipient": "invented@example.invalid"}),
        ("title-byte-cap", {"window_title": "🙂" * 51}),
        ("duplicate-paths", {"items": base["items"] * 2}),
        ("excluded-count", {"settable_excluded": 8}),
    ]:
        value = {**base, **changes}
        run(name, ["--read-fixture"], {"before": value, "after": value}, code=64)
    for name, changes in [
        ("settable-control", {"value_settable": True}),
        ("nonboolean-settable", {"value_settable": 0}),
        ("escaped-path", {"path": [1, 0]}),
        ("boundary-as-value", {"path": [0]}),
        ("path-width", {"path": [0, 32]}),
        ("value-byte-cap", {"value": "🙂" * 1001}),
        ("description-cap", {"description": "x" * 1001}),
        ("identifier-cap", {"identifier": "x" * 201}),
    ]:
        value = {**base, "items": [{**base["items"][0], **changes}]}
        run(name, ["--read-fixture"], {"before": value, "after": value}, code=64)
    excessive = {
        **base,
        "items": [{**base["items"][0], "path": [0, i], "value": "x" * 4000} for i in range(5)],
    }
    run("combined-cap", ["--read-fixture"], {"before": excessive, "after": excessive}, code=64)
    for name, after in [
        ("changed-title", {**base, "window_title": "Another invented thread"}),
        ("changed-body", {**base, "items": [{**base["items"][0], "value": "Changed"}]}),
    ]:
        run(name, ["--read-fixture"], {"before": base, "after": after}, code=64)
    shape = [
        {"path": [], "role": "AXWindow", "children": 2},
        {"path": [0], "role": "AXGroup", "children": 1},
        {"path": [0, 0], "role": "AXGroup", "children": 1},
        {"path": [0, 0, 0], "role": "AXGroup", "children": 1},
        {"path": [0, 0, 0, 0], "role": "AXTextArea", "children": 0},
        {"path": [1], "role": "AXTextField", "children": 0},
    ]
    spec = {"nodes": shape, "boundary": [0], "paths": [[0, 0, 0, 0]]}
    run("sealed-boundary", ["--boundary-fixture"], {"expected": spec, "current": shape})
    other_sidebar = copy.deepcopy(shape)
    other_sidebar[0]["children"] = 3
    other_sidebar.append({"path": [2], "role": "AXButton", "children": 0})
    run(
        "unrelated-shape-change",
        ["--boundary-fixture"],
        {"expected": spec, "current": other_sidebar},
    )
    for name, index, role in [
        ("modal-root", 0, "AXSheet"),
        ("not-text-area", 4, "AXTextField"),
        ("wrong-group", 1, "AXTextField"),
    ]:
        changed = copy.deepcopy(shape)
        changed[index]["role"] = role
        run(name, ["--boundary-fixture"], {"expected": spec, "current": changed}, code=64)
    with tempfile.TemporaryDirectory(prefix="aether-reader-offline-") as temporary:
        directory = Path(temporary).resolve()
        os.chmod(directory, 0o700)
        file = directory / "request.json"
        job = {
            "protocol": 1,
            "request_id": "a" * 32,
            "operation": "read_selected",
            "app": "messages",
            "expires_at": time.time() + 30,
        }
        for name, change, status in [
            ("valid-read-job", {}, 0),
            ("forbidden-open", {"operation": "open"}, 64),
            ("forbidden-app", {"app": "notes"}, 64),
            ("bool-version", {"protocol": True}, 64),
            ("expired-job", {"expires_at": time.time() - 1}, 64),
            ("unknown-field", {"script": "synthetic"}, 64),
        ]:
            file.write_text(json.dumps({**job, **change}))
            os.chmod(file, 0o600)
            run(name, ["--validate-job", str(directory)], code=status)
    run("no-input-mode", ["--send"], code=64)
    return {"passed": len(cases), "cases": cases, "native_jobs": 0, "model_calls": 0}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", required=True, type=Path)
    options = parser.parse_args()
    print(json.dumps(check(options.build), indent=2))
