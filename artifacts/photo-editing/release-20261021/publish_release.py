"""Approved PE1 publication: fresh private bundle, fixed service, no inference."""

import argparse
import asyncio
from contextlib import closing
from datetime import UTC, datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import plistlib
import shutil
import socket
import sqlite3
import subprocess
import sys
import time

import httpx
import sqlite_vec

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = Path.home() / ".local/share/workbench"
PLIST = Path.home() / "Library/LaunchAgents/dev.agenticrag.workbench.plist"
DOMAIN = f"gui/{os.getuid()}"
LABEL = "dev.agenticrag.workbench"
TAILSCALE = "/Applications/Tailscale.app/Contents/MacOS/Tailscale"
PRIVATE = BASE / "releases/photo-editing-20261021"
BUNDLE = PRIVATE / "bundle"
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "server")]
from prepare_photo_release import app_files, inventory, prepare, verify  # noqa: E402
from install_image_worker import FILES, install  # noqa: E402


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def command(args):
    result = subprocess.run([str(a) for a in args], capture_output=True)
    if result.returncode:
        raise RuntimeError(f"Operation failed: {Path(str(args[0])).name}, exit {result.returncode}")
    return result.stdout


def read_db(path):
    db = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    db.enable_load_extension(True)
    sqlite_vec.load(db)
    db.enable_load_extension(False)
    return db


def projections(path, columns=None):
    with closing(read_db(path)) as db:
        if columns is None:
            tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
            columns = {t: [r[1] for r in db.execute('PRAGMA table_info("' + t + '")')] for t in tables}
        result = {}
        for table, names in columns.items():
            rows = db.execute('SELECT ' + ','.join('"' + n + '"' for n in names) + ' FROM "' + table + '"')
            hashes = sorted(hashlib.sha256(json.dumps(list(row), ensure_ascii=False, separators=(",", ":"), default=lambda b: {"bytes": b.hex()}).encode()).hexdigest() for row in rows)
            result[table] = {"rows": len(hashes), "sha256": hashlib.sha256("".join(hashes).encode()).hexdigest()}
    return columns, result


def protected():
    result = {}
    for relative in ("app/server/.venv", "app/transcribe"):
        root = BASE / relative
        h = hashlib.sha256()
        files = 0
        for path in sorted(root.rglob("*")):
            if path.is_file() and not path.is_symlink() and "__pycache__" not in path.parts and path.suffix != ".pyc":
                h.update(str(path.relative_to(root)).encode())
                h.update(sha(path).encode())
                files += 1
        result[relative] = {"files": files, "sha256": h.hexdigest()}
    result["image_selectors"] = {n: sha(BASE / "image-worker/product" / n) for n in (".python", "config.json")}
    return result


def get(url):
    with httpx.Client(timeout=15, trust_env=False) as client:
        response = client.get(url)
        response.raise_for_status()
        return response


def idle():
    assert get("http://127.0.0.1:8787/api/runs/active").json() == [], "Chat work is active"
    counts = {}
    with closing(read_db(BASE / "data/workbench.db")) as db:
        for table, field, states in (
            ("image_jobs", "state", ["queued", "preparing", "running", "cancelling"]),
            ("workflow_runs", "state", ["queued", "running"]),
            ("workflow_graph_runs", "state", ["queued", "running"]),
            ("library_documents", "status", ["queued", "extracting", "embedding"]),
            ("transcripts", "status", ["queued", "transcribing"]),
        ):
            counts[table] = db.execute("SELECT count(*) FROM " + table + " WHERE " + field + " IN (" + ",".join("?" for _ in states) + ")", states).fetchone()[0]
        counts["transcript_cleanup"] = db.execute("SELECT count(*) FROM transcripts WHERE cleanup_status='running'").fetchone()[0]
    assert not any(counts.values()), "Background work is active; no task cancelled"
    fd = os.open(BASE / "data/native.lock", os.O_RDWR)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    finally:
        os.close(fd)
    return counts


def service():
    raw = PLIST.read_bytes()
    spec = plistlib.loads(raw)
    args = spec["ProgramArguments"]
    assert spec["Label"] == LABEL
    assert args[args.index("--host") + 1] == "127.0.0.1"
    assert args[args.index("--port") + 1] == "8787"
    assert args[args.index("--workers") + 1] == "1"
    assert spec["EnvironmentVariables"]["WORKBENCH_IMAGE_HOME"] == str(BASE / "image-worker/product")
    route = command([TAILSCALE, "serve", "status"])
    assert b"http://127.0.0.1:8787" in route
    return raw, route


def stop():
    command(["launchctl", "bootout", DOMAIN, PLIST])
    for _ in range(100):
        state = subprocess.run(["launchctl", "print", DOMAIN + "/" + LABEL], capture_output=True)
        with socket.socket() as sock:
            sock.settimeout(0.2)
            listening = sock.connect_ex(("127.0.0.1", 8787)) == 0
        if state.returncode and not listening:
            return
        time.sleep(0.1)
    raise RuntimeError("Existing service did not stop")


def start():
    command(["launchctl", "bootstrap", DOMAIN, PLIST])
    for _ in range(100):
        try:
            if get("http://127.0.0.1:8787/api/health").json()["ok"]:
                return
        except (httpx.HTTPError, ValueError):
            pass
        time.sleep(0.2)
    raise RuntimeError("Published service did not become healthy; preserve schema-aware source/current data")


def candidate():
    frozen = json.loads((ROOT / "artifacts/photo-editing/pe1-integration-20261021/executed-source.json").read_text())["files"]
    built = json.loads((ROOT / "artifacts/photo-editing/pe1-b-20261020/build-manifest.json").read_text())["files"]
    assert all(sha(ROOT / name) == value for name, value in frozen.items())
    assert inventory(ROOT / "server/app/static") == built
    return {"source_files": len(frozen), "static_files": len(built)}


def publish():
    assert not PRIVATE.exists(), "A release attempt already exists; review it before retrying"
    record = {"started_at": datetime.now(UTC).isoformat(), "published": False, "native_test_calls": 0, "model_test_calls": 0}
    record["candidate"] = candidate()
    plist_raw, route_raw = service()
    record["active_counts_before"] = idle()
    record["protected_before"] = protected()
    record["plist_sha256"] = hashlib.sha256(plist_raw).hexdigest()
    record["route_sha256"] = hashlib.sha256(route_raw).hexdigest()
    PRIVATE.mkdir(mode=0o700, parents=True)
    (PRIVATE / "route-before.txt").write_bytes(route_raw)
    (PRIVATE / "route-before.txt").chmod(0o600)
    (PRIVATE / "controller.py").write_bytes(Path(__file__).read_bytes())
    (PRIVATE / "controller.py").chmod(0o600)
    (OUT / "preflight.json").write_text(json.dumps(record, indent=2) + "\n")
    print("Preflight passed; quiescing the existing service.", flush=True)
    down_at = time.monotonic()
    stopped = False
    installed = False
    try:
        # Close the final check-to-stop interval without cancelling accepted tasks.
        idle()
        stop()
        stopped = True
        print("Service stopped; preparing the fresh private production bundle.", flush=True)
        bundle = prepare(BUNDLE, BASE / "data", BASE / "app", BASE / "image-worker/product", PLIST)
        verify(BUNDLE)
        record["production_bundle_files"] = len(bundle["files"])
        record["production_bundle_manifest_sha256"] = sha(BUNDLE / "release.json")
        record["bundle_contains_real_data"] = True
        assert app_files(ROOT) == app_files(BUNDLE / "candidate-app")
        columns, before = projections(BUNDLE / "data-snapshot/workbench.db")
        _, quiesced = projections(BASE / "data/workbench.db", columns)
        assert before == quiesced, "Snapshot/live projections differ"
        worker = BASE / "image-worker/product"
        python = Path((worker / ".python").read_text().strip())
        model = Path(json.loads((worker / "config.json").read_text())["model_path"])
        print("Bundle verified; installing the reviewed worker and application trees.", flush=True)
        install(worker, python, model)
        for relative in ("server/app", "shared"):
            destination = BASE / "app" / relative
            staging = destination.with_name(destination.name + ".pe1-new")
            assert not staging.exists()
            shutil.copytree(BUNDLE / "candidate-app" / relative, staging)
            assert inventory(staging) == inventory(BUNDLE / "candidate-app" / relative)
            previous = PRIVATE / ("replaced-" + relative.replace("/", "-"))
            os.replace(destination, previous)
            os.replace(staging, destination)
        installed = True
        assert app_files(BASE / "app") == app_files(BUNDLE / "candidate-app")
        assert all(sha(worker / n) == sha(BUNDLE / "worker" / n) for n in FILES)
        from app.db.core import connect

        async def migrate_only():
            async with connect(BASE / "data"):
                pass

        asyncio.run(migrate_only())
        _, migrated = projections(BASE / "data/workbench.db", columns)
        assert before == migrated, "Existing database rows changed during migration"
        with closing(read_db(BASE / "data/workbench.db")) as db:
            assert db.execute("PRAGMA user_version").fetchone()[0] == 14
            assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
            assert db.execute("PRAGMA foreign_key_check").fetchall() == []
        record["migration"] = {"from_schema": 13, "to_schema": 14, "old_tables_preserved": len(before), "old_rows_preserved": sum(r["rows"] for r in before.values()), "integrity": "ok", "foreign_keys": "ok"}
        # Before restart, all retained non-DB data files must match the snapshot.
        ignored = {"workbench.db", "workbench.db-wal", "workbench.db-shm", "native.lock", "backups"}
        live_inputs = inventory(BASE / "data", ignored)
        snapshot_inputs = inventory(BUNDLE / "data-snapshot", {"workbench.db", "workbench.db-wal", "workbench.db-shm"})
        assert live_inputs == snapshot_inputs
        record["retained_data_files_unchanged"] = len(live_inputs)
        assert protected() == record["protected_before"]
        assert PLIST.read_bytes() == plist_raw
        print("Migration and retained data verified; restarting the unchanged service.", flush=True)
        start()
        stopped = False
        record["downtime_seconds"] = round(time.monotonic() - down_at, 3)
        checks = {}
        for origin in ("http://127.0.0.1:8787", "https://jakes-mac-mini.tailc4d343.ts.net"):
            for endpoint in ("/api/health", "/api/workflows/defs", "/api/workflows/templates", "/api/images/status"):
                response = get(origin + endpoint)
                if endpoint == "/api/health":
                    assert response.json()["ok"]
                if endpoint == "/api/images/status":
                    assert response.json()["available"]
                checks[origin + endpoint] = response.status_code
            for name in ("index.html", "sw.js"):
                response = get(origin + "/" + name)
                assert hashlib.sha256(response.content).hexdigest() == sha(BUNDLE / "candidate-app/server/app/static" / name)
                checks[origin + "/" + name] = "200 + exact hash"
        assert service() == (plist_raw, route_raw)
        assert get("http://127.0.0.1:11434/api/version").json() == {"version": "0.35.0"}
        assert app_files(BASE / "app") == app_files(BUNDLE / "candidate-app")
        record.update(published=True, checks=checks, schema_version=14, installed_payload_files=len(app_files(BASE / "app")), worker_files_verified=len(FILES), service_identity_unchanged=True, tailscale_route_unchanged=True, protected_runtime_and_transcription_unchanged=True, fallback="Previous UI + current schema-aware backend/worker/current data; old backend prohibited")
        print("Publication verified: schema 14, local/HTTPS health and exact installed hashes pass.", flush=True)
    except BaseException as error:
        # No automatic old-backend/DB rollback is safe after migration 014.
        record["failure_type"] = type(error).__name__
        record["stopped_on_failure"] = stopped
        record["candidate_installed_on_failure"] = installed
        record["recovery"] = "Preserve current data and schema-aware backend; inspect private bundle, never restore old backend/DB"
        if stopped and not installed:
            # A preparation failure before replacement leaves the old app safe.
            if app_files(BASE / "app") == app_files(ROOT):
                pass
            elif not (PRIVATE / "replaced-server-app").exists():
                start()
                stopped = False
                record["previous_service_restarted_before_any_replacement"] = True
        raise
    finally:
        record["finished_at"] = datetime.now(UTC).isoformat()
        (PRIVATE / "result.json").write_text(json.dumps(record, indent=2) + "\n")
        (PRIVATE / "result.json").chmod(0o600)
        (OUT / "publication.json").write_text(json.dumps(record, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    if args.publish:
        publish()
    else:
        print(json.dumps({"candidate": candidate(), "active": idle(), "service": "existing identity verified"}))
        service()
