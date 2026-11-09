"""The real-trial operator's budget gates, with no runtime or app access."""

import hashlib
import json
import sys
import types
from pathlib import Path
from typing import Any

import pytest

from app.assistant.app_open import prompt_hash
from app.assistant.mac_probe import private_write


def operator(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, passed: bool = True) -> Any:
    script = Path(__file__).resolve().parents[2] / "scripts/run_app_open_trial.py"
    module: Any = types.ModuleType("app_open_trial_test")
    module.__file__ = str(script)
    exec(compile(script.read_text(), str(script), "exec"), module.__dict__)
    module.ROOT = tmp_path
    module.STAGE = tmp_path / "private"
    module.STAGE.mkdir(mode=0o700)
    manifest = {"build": {}, "files": {}, "prompt_sha256": prompt_hash()}
    file = tmp_path / "artifacts/assistant-app-open-20261108/source-manifest-v2.json"
    file.parent.mkdir(parents=True)
    file.write_text(json.dumps(manifest))
    module.digest = hashlib.sha256(file.read_bytes()).hexdigest()
    private_write(module.STAGE / "build.json", b"{}")
    module.calls = []

    async def fake_trial(index: int, build: dict[str, Any]) -> dict[str, Any]:
        app = module.CASES[index][0]
        module.calls.append(app)
        result = {"gate_passed": passed}
        private_write(module.STAGE / (app + ".summary.json"), json.dumps(result).encode())
        return result

    module.trial = fake_trial

    def run(app: str) -> None:
        monkeypatch.setattr(sys, "argv", [str(script), app, "--manifest-sha256", module.digest])
        module.main()

    module.run = run
    return module


def test_two_task_ledger_cannot_be_replayed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial = operator(tmp_path, monkeypatch)
    trial.run("notes")
    trial.run("messages")
    for app in ("notes", "messages"):
        with pytest.raises(SystemExit):
            trial.run(app)
    assert trial.calls == ["notes", "messages"]
    assert len(json.loads((trial.STAGE / "native/ledger.json").read_text())) == 2


def test_first_failure_stops_next_task(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    trial = operator(tmp_path, monkeypatch, passed=False)
    with pytest.raises(SystemExit):
        trial.run("notes")
    with pytest.raises(SystemExit):
        trial.run("messages")
    assert trial.calls == ["notes"]


def test_phase_order_cannot_skip_first_task(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    trial = operator(tmp_path, monkeypatch)
    with pytest.raises(SystemExit):
        trial.run("messages")
    assert trial.calls == []


def test_changed_manifest_cannot_dispatch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    trial = operator(tmp_path, monkeypatch)
    trial.digest = "0" * 64
    with pytest.raises(SystemExit):
        trial.run("notes")
    assert trial.calls == []
