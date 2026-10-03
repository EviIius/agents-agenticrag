"""Deployment safety checks use isolated synthetic engine/config/database files."""

import importlib.util
import json
import plistlib
import sqlite3
from pathlib import Path
from types import ModuleType

import pytest


def deployment() -> ModuleType:
    path = Path(__file__).resolve().parents[2] / "scripts/deploy.py"
    spec = importlib.util.spec_from_file_location("workbench_deployment", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_existing_identity_preserved_and_wrong_bind_refused(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = deployment()
    directory = tmp_path / "Library/LaunchAgents"
    directory.mkdir(parents=True)
    path = directory / "dev.agenticrag.workbench.plist"
    data = {
        "Label": "dev.agenticrag.workbench",
        "ProgramArguments": ["python", "-m", "agenticrag", "serve"],
    }
    path.write_bytes(plistlib.dumps(data))
    (directory / "dev.agenticrag.ollama.plist").write_bytes(
        plistlib.dumps({"ProgramArguments": ["ollama", "serve"]})
    )
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    found, previous = module.existing_service()
    assert found == path and previous["Label"] == data["Label"]
    data["ProgramArguments"] = ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0"]
    path.write_bytes(plistlib.dumps(data))
    with pytest.raises(RuntimeError, match="Existing bind"):
        module.existing_service()


def test_database_backup_is_consistent_private_and_bounded(tmp_path: Path) -> None:
    module = deployment()
    with sqlite3.connect(tmp_path / "workbench.db") as db:
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("CREATE TABLE example(value TEXT)")
        db.execute("INSERT INTO example VALUES ('synthetic')")
        db.commit()
        for _ in range(12):
            module.backup_database(tmp_path)
    backups = sorted((tmp_path / "backups").glob("workbench-*.db"))
    assert len(backups) == 10
    assert backups[-1].stat().st_mode & 0o777 == 0o600
    with sqlite3.connect(backups[-1]) as copy:
        assert copy.execute("SELECT value FROM example").fetchone() == ("synthetic",)


def test_engine_install_excludes_recordings_and_preserves_private_config(tmp_path: Path) -> None:
    module = deployment()
    source, target = tmp_path / "source", tmp_path / "installed/app/transcribe"
    for name in ("bin", "localtranscribe", "tests", "models", "inbox"):
        (source / name).mkdir(parents=True)
    (source / "inbox/synthetic.wav").write_text("synthetic audio, never copied")
    (source / "models/weight.bin").write_text("fake weight")
    script = source / "bin/transcribe"
    script.write_text("#!/bin/sh\nprintf '{\"ok\":true}'")
    script.chmod(0o700)
    for name in (
        "README.md",
        "config.example.json",
        "glossary.example.txt",
        "install.sh",
        "uninstall.sh",
    ):
        (source / name).write_text("synthetic public source")
    (source / "glossary.txt").write_text("synthetic glossary")
    (source / ".python").write_text("synthetic interpreter")
    (source / "config.json").write_text(json.dumps({"model": str(source / "models/weight.bin")}))
    module.install_engine(source, target)
    assert not (target / "inbox").exists()
    assert json.loads((target / "config.json").read_text())["data_dir"] == str(target / "runtime")
    assert list((target / "runtime/inbox").iterdir()) == []
    assert (target / "runtime").stat().st_mode & 0o777 == 0o700
    assert json.loads((target / "config.json").read_text())["model"] == str(
        target / "models/weight.bin"
    )
    assert (target / "config.json").stat().st_mode & 0o777 == 0o600
    (target / "glossary.txt").write_text("installed glossary edited later")
    (source / "glossary.txt").write_text("source glossary changed later")
    module.install_engine(source, target)
    assert (target / "glossary.txt").read_text() == "installed glossary edited later"
