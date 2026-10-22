"""Narrow upload repair publication. Existing runtimes/data/service; no inference."""

import importlib.util
import json
import os
import shutil
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "release_helpers", ROOT / "artifacts/photo-editing/release-20261021/publish_release.py"
)
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)
BASE = helpers.BASE
PRIVATE = BASE / "releases/heic-preparation-20261021"
BUNDLE = PRIVATE / "bundle"


def publish():
    assert not PRIVATE.exists(), "Review the previous attempt before any retry"
    frozen = json.loads((OUT / "release-source.json").read_text())
    assert all(helpers.sha(ROOT / name) == digest for name, digest in frozen["files"].items())
    assert frozen["gates_passed"] is True
    plist, route = helpers.service()
    counts = helpers.idle()
    protected = helpers.protected()
    record = {"published": False, "started_at": datetime.now(UTC).isoformat(),
              "model_calls": 0, "active_counts_before": counts,
              "source_commit": frozen["source_commit"], "schema_version": 14}
    PRIVATE.mkdir(mode=0o700, parents=True)
    shutil.copyfile(Path(__file__), PRIVATE / "controller.py")
    stopped = False
    try:
        helpers.idle()
        start = time.monotonic()
        helpers.stop()
        stopped = True
        bundle = helpers.prepare(BUNDLE, BASE / "data", BASE / "app",
                                 BASE / "image-worker/product", helpers.PLIST)
        helpers.verify(BUNDLE)
        record["private_bundle_files"] = len(bundle["files"])
        columns, before = helpers.projections(BASE / "data/workbench.db")
        worker = BASE / "image-worker/product"
        python = Path((worker / ".python").read_text().strip())
        model = Path(json.loads((worker / "config.json").read_text())["model_path"])
        helpers.install(worker, python, model)
        for relative in ("server/app", "shared"):
            destination = BASE / "app" / relative
            staging = destination.with_name(destination.name + ".photo-upload-new")
            assert not staging.exists()
            shutil.copytree(BUNDLE / "candidate-app" / relative, staging)
            assert helpers.inventory(staging) == helpers.inventory(BUNDLE / "candidate-app" / relative)
            os.replace(destination, PRIVATE / ("replaced-" + relative.replace("/", "-")))
            os.replace(staging, destination)
        assert helpers.app_files(BASE / "app") == helpers.app_files(BUNDLE / "candidate-app")
        assert all(helpers.sha(worker / n) == helpers.sha(BUNDLE / "worker" / n) for n in helpers.FILES)
        assert helpers.projections(BASE / "data/workbench.db", columns)[1] == before
        ignored = {"workbench.db", "workbench.db-wal", "workbench.db-shm", "native.lock", "backups"}
        assert helpers.inventory(BASE / "data", ignored) == helpers.inventory(
            BUNDLE / "data-snapshot", {"workbench.db", "workbench.db-wal", "workbench.db-shm"})
        assert helpers.protected() == protected
        assert helpers.service() == (plist, route)
        helpers.start()
        stopped = False
        record["downtime_seconds"] = round(time.monotonic() - start, 3)
        checks = {}
        for origin in ("http://127.0.0.1:8787", "https://jakes-mac-mini.tailc4d343.ts.net"):
            assert helpers.get(origin + "/api/health").json()["ok"]
            status = helpers.get(origin + "/api/images/status").json()
            assert status["available"] and status["editing_available"]
            for name in ("index.html", "sw.js"):
                content = helpers.get(origin + "/" + name).content
                import hashlib
                assert hashlib.sha256(content).hexdigest() == helpers.sha(ROOT / "server/app/static" / name)
            checks[origin] = "health, edit capability, exact index/service-worker hashes pass"
        assert helpers.get("http://127.0.0.1:11434/api/version").json() == {"version": "0.35.0"}
        assert helpers.service() == (plist, route)
        helpers.verify(BUNDLE)
        record.update(published=True, checks=checks, runtime_and_selectors_unchanged=True,
                      service_and_route_unchanged=True, database_and_inputs_preserved=True,
                      installed_app_files=len(helpers.app_files(BASE / "app")),
                      worker_files_verified=len(helpers.FILES),
                      fallback="Previous UI + current schema-aware backend/worker/current data")
    finally:
        if stopped:
            # Preserve the schema-aware backend/current data; never restore an old DB.
            helpers.start()
        (PRIVATE / "result.json").write_text(json.dumps(record, indent=2) + "\n")
        (OUT / "publication.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record))


if __name__ == "__main__":
    if sys.argv[1:] != ["--apply"]:
        raise SystemExit("Use --apply only after the reviewed repair gates pass")
    publish()
