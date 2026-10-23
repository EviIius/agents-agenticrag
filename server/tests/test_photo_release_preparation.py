"""PE1 installer/fallback tests use synthetic files and never start a model."""

import fcntl
import importlib.util
import json
import plistlib
import sqlite3
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[2]


def script(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location("pe1_" + name, ROOT / "scripts" / (name + ".py"))
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def selectors(tmp_path: Path) -> tuple[Path, Path, Path]:
    home = tmp_path / "worker"
    home.mkdir()
    python = tmp_path / "fake-python"
    python.write_text("#!/bin/sh\nexit 99\n")  # No test executes this file.
    python.chmod(0o700)
    model = tmp_path / "e7b7dc27f91deacad38e78976d1f2b499d76a294"
    model.mkdir()
    (home / ".python").write_text(str(python))
    (home / "config.json").write_text(json.dumps({"model_path": str(model)}))
    (home / "worker.py").write_bytes((ROOT / "image_worker/product/worker.py").read_bytes())
    return home, python, model


def test_installer_adds_only_reviewed_files_and_preserves_selectors(tmp_path: Path) -> None:
    module = script("install_image_worker")
    home, python, model = selectors(tmp_path)
    before = {p.name: p.read_bytes() for p in home.iterdir()}
    (home / "private-note").write_text("fake local configuration")
    module.install(home, python, model, lock=tmp_path / "native.lock")
    for name in module.FILES:
        assert (home / name).read_bytes() == (ROOT / "image_worker/product" / name).read_bytes()
        assert (home / name).stat().st_mode & 0o777 == 0o600
    assert (home / "worker.py").read_bytes() == before["worker.py"]
    for name in (".python", "config.json"):
        assert (home / name).read_bytes() == before[name]
    assert (home / "private-note").read_text() == "fake local configuration"
    assert list(model.iterdir()) == []


def test_installer_refuses_occupied_native_lease_without_changes(tmp_path: Path) -> None:
    module = script("install_image_worker")
    home, python, model = selectors(tmp_path)
    before = {p.name: p.read_bytes() for p in home.iterdir()}
    with (tmp_path / "native.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(ValueError, match="Native worker is active"):
            module.install(home, python, model, lock=tmp_path / "native.lock")
    assert {p.name: p.read_bytes() for p in home.iterdir()} == before


def test_installer_copy_failure_restores_previous_worker_set(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = script("install_image_worker")
    home, python, model = selectors(tmp_path)
    (home / "worker.py").write_text("fake previous worker")
    before = {p.name: p.read_bytes() for p in home.iterdir()}
    original = module.replace
    failed = False

    def fail_once(path: Path, raw: bytes) -> None:
        nonlocal failed
        if path.name == "reference_contract.py" and not failed:
            failed = True
            raise OSError("synthetic interrupted source copy")
        original(path, raw)

    monkeypatch.setattr(module, "replace", fail_once)
    with pytest.raises(OSError, match="synthetic interrupted"):
        module.install(home, python, model, lock=tmp_path / "native.lock")
    assert {p.name: p.read_bytes() for p in home.iterdir()} == before


def test_installer_refuses_selector_change_or_symlink(tmp_path: Path) -> None:
    module = script("install_image_worker")
    home, python, model = selectors(tmp_path)
    (home / ".python").write_text("/unapproved/runtime")
    with pytest.raises(ValueError, match="runtime change"):
        module.install(home, python, model, lock=tmp_path / "native.lock")
    (home / ".python").unlink()
    (home / ".python").symlink_to(python)
    with pytest.raises(ValueError, match="symlinks"):
        module.install(home, python, model, lock=tmp_path / "native.lock")
    assert not (home / "edit_worker.py").exists()


def test_generic_deployment_cannot_bypass_photo_release_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = script("deploy")
    monkeypatch.setattr(sys, "argv", ["deploy.py", "--apply"])

    def forbidden() -> None:
        pytest.fail("Must refuse before inspecting or changing the installed service")

    monkeypatch.setattr(module, "existing_service", forbidden)
    with pytest.raises(RuntimeError, match="Photo-reference releases require"):
        module.main()


@pytest.fixture
def bundle_inputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[ModuleType, Path, Path, Path, Path]:
    module = script("prepare_photo_release")
    candidate, installed = tmp_path / "source", tmp_path / "installed"
    for base, label in [(candidate, "new"), (installed, "previous")]:
        (base / "server/app/static").mkdir(parents=True)
        (base / "shared").mkdir()
        (base / "shared/config.json").write_text('{"APP_NAME":"Aether"}')
        (base / "server/pyproject.toml").write_text("fake unchanged dependencies")
        (base / "server/uv.lock").write_text("fake unchanged lock")
        (base / "server/app/backend.py").write_text(label)
        (base / "server/app/static/index.html").write_text(label)
    (candidate / "server/app/db/migrations").mkdir(parents=True)
    (candidate / "server/app/db/migrations/014_image_references.sql").write_text("-- fake marker")
    (candidate / "image_worker/product").mkdir(parents=True)
    for name in (
        "worker.py",
        "edit_worker.py",
        "reference_contract.py",
        "reference_codec.py",
        "masked_edit.py",
    ):
        (candidate / "image_worker/product" / name).write_bytes(
            (ROOT / "image_worker/product" / name).read_bytes()
        )
    monkeypatch.setattr(module, "ROOT", candidate)
    worker, _, _ = selectors(tmp_path)
    plist = tmp_path / "original.plist"
    plist.write_bytes(
        plistlib.dumps(
            {
                "Label": "dev.agenticrag.workbench",
                "ProgramArguments": [
                    "python",
                    "-m",
                    "uvicorn",
                    "app.main:app",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "8787",
                ],
            }
        )
    )
    data = tmp_path / "data"
    data.mkdir()
    (data / "fake-draft.txt").write_text("fake unsent input kept in complete snapshot")
    with sqlite3.connect(data / "workbench.db") as db:
        db.executescript(
            "PRAGMA user_version=14; "
            "CREATE TABLE image_jobs(id TEXT,input_json TEXT,state TEXT); "
            "CREATE TABLE image_artifacts(job_id TEXT,sha256 TEXT);"
        )
    return module, data, installed, worker, plist


def test_bundle_keeps_new_backend_old_ui_and_complete_private_snapshot(
    tmp_path: Path, bundle_inputs: tuple[ModuleType, Path, Path, Path, Path]
) -> None:
    module, data, installed, worker, plist = bundle_inputs
    before = module.inventory(installed), module.inventory(worker), plist.read_bytes()
    bundle = tmp_path / "bundle"
    manifest = module.prepare(bundle, data, installed, worker, plist)
    module.verify(bundle)
    assert not manifest["publication_authorized"]
    assert (bundle / "candidate-app/server/app/backend.py").read_text() == "new"
    assert (bundle / "compatibility-app/server/app/backend.py").read_text() == "new"
    assert (bundle / "compatibility-app/server/app/static/index.html").read_text() == "previous"
    assert (bundle / "previous-app-archive/server/app/backend.py").read_text() == "previous"
    assert (bundle / "data-snapshot/fake-draft.txt").read_bytes() == (
        data / "fake-draft.txt"
    ).read_bytes()
    assert (bundle / "paired-backup/images/auto-release.json").is_file()
    assert before == (module.inventory(installed), module.inventory(worker), plist.read_bytes())
    assert not (bundle / "restore-verification").exists()


def test_bundle_detects_corruption_and_rejects_old_backend_selection(
    tmp_path: Path, bundle_inputs: tuple[ModuleType, Path, Path, Path, Path]
) -> None:
    module, data, installed, worker, plist = bundle_inputs
    bundle = tmp_path / "bundle"
    module.prepare(bundle, data, installed, worker, plist)
    file = bundle / "compatibility-app/server/app/backend.py"
    file.write_text("previous")
    with pytest.raises(ValueError, match="changed"):
        module.verify(bundle)
    manifest = json.loads((bundle / "release.json").read_text())
    manifest["files"][str(file.relative_to(bundle))] = module.sha(file)
    (bundle / "release.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="keep the candidate backend"):
        module.verify(bundle)


def test_busy_snapshot_refused_and_partial_bundle_removed(
    tmp_path: Path, bundle_inputs: tuple[ModuleType, Path, Path, Path, Path]
) -> None:
    module, data, installed, worker, plist = bundle_inputs
    with sqlite3.connect(data / "workbench.db") as db:
        db.execute("INSERT INTO image_jobs VALUES ('fake','{}','running')")
    bundle = tmp_path / "bundle"
    with pytest.raises(ValueError, match="quiesce/reap"):
        module.prepare(bundle, data, installed, worker, plist)
    assert not bundle.exists()


def test_source_change_during_snapshot_aborts_without_accepted_bundle(
    tmp_path: Path,
    bundle_inputs: tuple[ModuleType, Path, Path, Path, Path],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module, data, installed, worker, plist = bundle_inputs
    original = module.copy_files

    def changing(source: Path, target: Path, files: dict[str, str]) -> None:
        original(source, target, files)
        if source == data:
            (data / "fake-draft.txt").write_text("synthetic concurrent change")

    monkeypatch.setattr(module, "copy_files", changing)
    bundle = tmp_path / "bundle"
    with pytest.raises(ValueError, match="Data changed"):
        module.prepare(bundle, data, installed, worker, plist)
    assert not bundle.exists()


def test_bundle_refuses_wrong_service_bind_and_source_overlap(
    tmp_path: Path, bundle_inputs: tuple[ModuleType, Path, Path, Path, Path]
) -> None:
    module, data, installed, worker, plist = bundle_inputs
    with pytest.raises(ValueError, match="separate"):
        module.prepare(data / "bad-bundle", data, installed, worker, plist)
    value = plistlib.loads(plist.read_bytes())
    value["ProgramArguments"][-1] = "9999"
    plist.write_bytes(plistlib.dumps(value))
    with pytest.raises(ValueError, match="bind/port"):
        module.prepare(tmp_path / "bundle", data, installed, worker, plist)
    assert not (tmp_path / "bundle").exists()
