"""Approved Part A static publication; retain backend, current data and old assets."""

import argparse
from contextlib import closing
from datetime import UTC, datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
QA = ROOT / "artifacts/aero-blur-fix"
spec = importlib.util.spec_from_file_location(
    "release_helpers", ROOT / "artifacts/photo-editing/release-20261021/publish_release.py"
)
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)
BASE = helpers.BASE
PRIVATE = BASE / "releases/aero-blur-fix-20261025"
TARGET = BASE / "app/server/app/static"
SOURCE = ROOT / "server/app/static"


def pid():
    text = helpers.command(["launchctl", "print", helpers.DOMAIN + "/" + helpers.LABEL]).decode()
    match = re.search(r"^\s*pid = (\d+)\s*$", text, re.M)
    assert match, "Existing app is not running"
    return int(match[1])


def backend(root):
    return {n: h for n, h in helpers.app_files(root).items() if not n.startswith("server/app/static/")}


def atomic_copy(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(target.name + ".aero-blur-publish")
    shutil.copy2(source, temp)
    os.replace(temp, target)


def candidate():
    frozen = json.loads((OUT / "release-manifest.json").read_text())
    files = json.loads((QA / "executed-source.json").read_text())
    assert all(helpers.sha(ROOT / n) == h for n, h in files.items())
    evidence = json.loads((QA / "evidence-manifest.json").read_text())
    assert all(helpers.sha(QA / n) == h for n, h in evidence.items())
    gates = json.loads((QA / "verification.json").read_text())
    assert gates["passed"] and gates["browser_passed"] == 900 and gates["existing_browser_skips"] == 4
    assert json.loads((QA / "bundle.json").read_text())["gzip_bytes"] == 252228
    assert helpers.inventory(SOURCE) == frozen["static_files"]
    measured = json.loads(subprocess.check_output(["python3", str(ROOT / "scripts/measure_bundle.py")], cwd=ROOT))
    assert measured["gzip_bytes"] == 252228
    assert backend(ROOT) == backend(BASE / "app"), "Backend parity failed"
    for item in json.loads((QA / "candidate-glass.json").read_text())["stylesheets"]:
        assert helpers.sha(SOURCE / "assets" / item["file"]) == item["sha256"]
    subprocess.run(["python3", str(ROOT / "scripts/check_glass_css.py"), str(SOURCE / "assets")], check=True, capture_output=True)
    workers = {n: helpers.sha(BASE / "image-worker/product" / n) for n in helpers.FILES}
    assert workers == {n: helpers.sha(ROOT / "image_worker/product" / n) for n in helpers.FILES}
    return files, helpers.inventory(SOURCE), workers


def check():
    files, static, workers = candidate()
    plist, route = helpers.service()
    return {
        "source_files": len(files), "static_files": len(static),
        "backend_files_unchanged": len(backend(BASE / "app")),
        "worker_files_unchanged": len(workers), "initial_js_gzip_bytes": 252228,
        "service_pid": pid(), "service_label": helpers.LABEL,
        "plist_sha256": hashlib.sha256(plist).hexdigest(),
        "route_sha256": hashlib.sha256(route).hexdigest(),
        "model_calls": 0, "apply": False,
    }


def publish():
    assert not PRIVATE.exists(), "Review the recorded release attempt before retrying"
    record = check()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    main = subprocess.check_output(["git", "ls-remote", "origin", "refs/heads/main"], cwd=ROOT, text=True).split()[0]
    assert commit == main, "Publish the merged main tree only"
    _, static, workers = candidate()
    old = helpers.inventory(TARGET)
    code = backend(BASE / "app")
    protected = helpers.protected()
    plist, route = helpers.service()
    original_pid = pid()
    PRIVATE.mkdir(mode=0o700, parents=True)
    shutil.copyfile(Path(__file__), PRIVATE / "controller.py")
    (PRIVATE / "controller.py").chmod(0o600)
    record.update(source_commit=commit, started_at=datetime.now(UTC).isoformat(), published=False)
    changed = []
    try:
        shutil.copytree(TARGET, PRIVATE / "previous-static")
        assert helpers.inventory(PRIVATE / "previous-static") == old
        helpers.sqlite_backup = importlib.import_module("prepare_photo_release").sqlite_backup
        helpers.sqlite_backup(BASE / "data/workbench.db", PRIVATE / "workbench.db")
        with closing(helpers.read_db(PRIVATE / "workbench.db")) as db:
            assert db.execute("PRAGMA user_version").fetchone()[0] == 14
            assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
            assert db.execute("PRAGMA foreign_key_check").fetchall() == []
        recovery = {
            "previous_static": old,
            "database_sha256": helpers.sha(PRIVATE / "workbench.db"),
            "backend": code, "worker": workers, "protected": protected,
            "rule": "UI fallback only; keep current backend/worker/data. Never restore this DB over new user work.",
        }
        (PRIVATE / "recovery.json").write_text(json.dumps(recovery, indent=2) + "\n")
        (PRIVATE / "recovery.json").chmod(0o600)
        assert helpers.inventory(SOURCE) == static
        assert backend(BASE / "app") == code and helpers.service() == (plist, route)
        assert pid() == original_pid
        # Keep old content-addressed assets for already-open documents. All new
        # assets exist before switching HTML, with the update worker published last.
        for name in [n for n in static if n not in {"index.html", "sw.js"}] + ["index.html", "sw.js"]:
            if (TARGET / name).is_file() and helpers.sha(TARGET / name) == static[name]:
                continue
            atomic_copy(SOURCE / name, TARGET / name)
            changed.append(name)
        assert all(helpers.sha(TARGET / n) == h for n, h in static.items())
        retained = {n: h for n, h in old.items() if n not in static}
        assert all(helpers.sha(TARGET / n) == h for n, h in retained.items())
        checks = {}
        entry = json.loads((SOURCE / ".vite/manifest.json").read_text())["index.html"]["file"]
        names = ["index.html", "sw.js", "theme-init.js", entry, *["assets/" + item["file"] for item in json.loads((QA / "candidate-glass.json").read_text())["stylesheets"]]]
        for origin in ["http://127.0.0.1:8787", "https://jakes-mac-mini.tailc4d343.ts.net"]:
            assert helpers.get(origin + "/api/health").json()["ok"] is True
            for name in names:
                assert hashlib.sha256(helpers.get(origin + "/" + name).content).hexdigest() == static[name]
            checks[origin] = {"health": 200, "exact_assets": len(names)}
        assert backend(BASE / "app") == code
        assert {n: helpers.sha(BASE / "image-worker/product" / n) for n in workers} == workers
        assert helpers.protected() == protected
        assert helpers.service() == (plist, route) and pid() == original_pid
        record.update(
            published=True, apply=True, checks=checks,
            static_files_verified=len(static), old_assets_retained=len(retained),
            changed_files=len(changed), backend_unchanged=True, worker_unchanged=True,
            service_pid_unchanged=True, service_restarted=False, service_and_route_unchanged=True,
            runtime_and_selectors_unchanged=True, database_backup_schema=14,
            database_backup_integrity="ok", database_backup_foreign_keys=0,
            backup_sha256=recovery["database_sha256"],
            user_data_restored=False, controller_writes_to_live_data=False,
            fallback="Previous static UI only; keep current backend, worker and current data",
        )
    except BaseException as error:
        record["failure_type"] = type(error).__name__
        if changed:
            previous = PRIVATE / "previous-static"
            for name in [n for n in old if n not in {"index.html", "sw.js"}] + ["index.html", "sw.js"]:
                atomic_copy(previous / name, TARGET / name)
            assert all(helpers.sha(TARGET / n) == h for n, h in old.items())
            record["previous_ui_restored"] = True
        raise
    finally:
        record["finished_at"] = datetime.now(UTC).isoformat()
        (PRIVATE / "result.json").write_text(json.dumps(record, indent=2) + "\n")
        (PRIVATE / "result.json").chmod(0o600)
        (OUT / "publication.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({"published": True, "static_files": len(static), "service_restarted": False, "model_calls": 0}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    if parser.parse_args().apply:
        publish()
    else:
        print(json.dumps(check(), indent=2))
