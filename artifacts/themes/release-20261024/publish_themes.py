"""Approved paired theme release using the existing PE1 production safeguards."""

import argparse
from contextlib import closing
from datetime import UTC, datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "theme_release_helpers",
    ROOT / "artifacts/photo-editing/release-20261021/publish_release.py",
)
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)
BASE = helpers.BASE
PRIVATE = BASE / "releases/themes-20261024"
BUNDLE = PRIVATE / "bundle"


def candidate():
    frozen = json.loads((OUT / "release-source.json").read_text())
    assert frozen["gates_passed"] and frozen["model_calls_authorized"] == 0
    assert frozen["initial_gzip_bytes"] <= 256000
    assert all(helpers.sha(ROOT / n) == h for n, h in frozen["files"].items())
    assert helpers.inventory(ROOT / "server/app/static") == frozen["static_files"]
    old = helpers.app_files(BASE / "app")
    new = helpers.app_files(ROOT)
    different = sorted(
        n for n in old.keys() | new.keys()
        if not n.startswith("server/app/static/") and old.get(n) != new.get(n)
    )
    assert different == ["server/app/db/settings.py"], different
    assert all(
        helpers.sha(BASE / "image-worker/product" / n)
        == helpers.sha(ROOT / "image_worker/product" / n)
        for n in helpers.FILES
    )
    return frozen, different


def check():
    frozen, differences = candidate()
    plist, route = helpers.service()
    active = helpers.idle()
    return {
        "qualified_commit": frozen["qualified_commit"],
        "source_files": len(frozen["files"]),
        "static_files": len(frozen["static_files"]),
        "initial_gzip_bytes": frozen["initial_gzip_bytes"],
        "backend_differences": differences,
        "active_counts": active,
        "plist_sha256": hashlib.sha256(plist).hexdigest(),
        "route_sha256": hashlib.sha256(route).hexdigest(),
        "model_calls": 0,
        "publication": False,
    }


def publish():
    assert not PRIVATE.exists(), "Review the recorded attempt before retrying"
    record = check()
    merged = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    main = subprocess.check_output(
        ["git", "ls-remote", "origin", "refs/heads/main"], cwd=ROOT, text=True
    ).split()[0]
    assert merged == main, "Publish only the verified merged main tree"
    record.update(source_commit=merged, started_at=datetime.now(UTC).isoformat())
    protected = helpers.protected()
    plist, route = helpers.service()
    PRIVATE.mkdir(mode=0o700, parents=True)
    shutil.copyfile(Path(__file__), PRIVATE / "controller.py")
    (PRIVATE / "controller.py").chmod(0o600)
    (OUT / "preflight.json").write_text(json.dumps(record, indent=2) + "\n")
    stopped = False
    replaced = []
    try:
        helpers.idle()
        start = time.monotonic()
        helpers.stop()
        stopped = True
        print("Service quiesced; preparing the private recovery bundle.", flush=True)
        bundle = helpers.prepare(
            BUNDLE, BASE / "data", BASE / "app", BASE / "image-worker/product", helpers.PLIST
        )
        helpers.verify(BUNDLE)
        assert helpers.app_files(ROOT) == helpers.app_files(BUNDLE / "candidate-app")
        columns, before = helpers.projections(BASE / "data/workbench.db")
        assert helpers.projections(BUNDLE / "data-snapshot/workbench.db", columns)[1] == before
        record["private_bundle_files"] = len(bundle["files"])
        record["private_bundle_manifest_sha256"] = helpers.sha(BUNDLE / "release.json")
        for relative in ("server/app", "shared"):
            destination = BASE / "app" / relative
            staging = destination.with_name(destination.name + ".themes-new")
            assert not staging.exists()
            shutil.copytree(BUNDLE / "candidate-app" / relative, staging)
            assert helpers.inventory(staging) == helpers.inventory(BUNDLE / "candidate-app" / relative)
            previous = PRIVATE / ("replaced-" + relative.replace("/", "-"))
            os.replace(destination, previous)
            replaced.append((destination, previous))
            os.replace(staging, destination)
        assert helpers.app_files(BASE / "app") == helpers.app_files(BUNDLE / "candidate-app")
        assert helpers.projections(BASE / "data/workbench.db", columns)[1] == before
        with closing(helpers.read_db(BASE / "data/workbench.db")) as db:
            assert db.execute("PRAGMA user_version").fetchone()[0] == 14
            assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
            assert db.execute("PRAGMA foreign_key_check").fetchall() == []
        ignored = {"workbench.db", "workbench.db-wal", "workbench.db-shm", "native.lock", "backups"}
        inputs = helpers.inventory(BASE / "data", ignored)
        assert inputs == helpers.inventory(
            BUNDLE / "data-snapshot", {"workbench.db", "workbench.db-wal", "workbench.db-shm"}
        )
        assert helpers.protected() == protected
        assert helpers.service() == (plist, route)
        helpers.start()
        stopped = False
        record["downtime_seconds"] = round(time.monotonic() - start, 3)
        checks = {}
        frozen = json.loads((OUT / "release-source.json").read_text())
        for origin in ("http://127.0.0.1:8787", "https://jakes-mac-mini.tailc4d343.ts.net"):
            assert helpers.get(origin + "/api/health").json()["ok"]
            status = helpers.get(origin + "/api/images/status").json()
            assert status["available"] and status["editing_available"]
            for n in ["index.html", "sw.js", "theme-init.js", *[
                n for n in frozen["static_files"]
                if n.startswith(("icons/", "manifests/"))
            ]]:
                content = helpers.get(origin + "/" + n).content
                assert hashlib.sha256(content).hexdigest() == frozen["static_files"][n], n
            checks[origin] = "health, editing capability and exact theme asset hashes pass"
        assert helpers.protected() == protected
        assert helpers.service() == (plist, route)
        assert helpers.get("http://127.0.0.1:11434/api/version").json() == {"version": "0.35.0"}
        helpers.verify(BUNDLE)
        record.update(
            publication=True, checks=checks, schema_version=14,
            installed_files=len(helpers.app_files(BASE / "app")),
            preexisting_tables_preserved=len(before),
            preexisting_rows_preserved=sum(t["rows"] for t in before.values()),
            non_db_data_files_preserved=len(inputs),
            worker_files_unchanged=len(helpers.FILES),
            protected_runtimes_and_selectors_unchanged=True,
            service_and_route_unchanged=True,
            fallback="Previous UI + current schema-aware backend/worker/current data; never restore the snapshot over newer work",
        )
        print("Paired theme publication verified; no model inference invoked.", flush=True)
    except BaseException as error:
        record.update(failure_type=type(error).__name__, stopped_on_failure=stopped,
                      recovery="Preserve current data and schema-aware code; inspect the private bundle")
        # Both prior and candidate backends are schema 14 and differ only in
        # theme setting validation. Recover a partial file replacement before
        # restart; never replace user data or reference-aware worker code.
        if stopped:
            for destination, previous in reversed(replaced):
                if destination.exists():
                    os.replace(destination, PRIVATE / (destination.name + ".failed-themes"))
                os.replace(previous, destination)
            helpers.start()
            stopped = False
            record["service_recovered"] = True
        raise
    finally:
        record["finished_at"] = datetime.now(UTC).isoformat()
        (PRIVATE / "result.json").write_text(json.dumps(record, indent=2) + "\n")
        (PRIVATE / "result.json").chmod(0o600)
        (OUT / "publication.json").write_text(json.dumps(record, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.apply:
        publish()
    else:
        print(json.dumps(check(), indent=2))
