"""Publish the tested composer/workflow static build, preserving server and rollback."""

import argparse
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from deploy import existing_service

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "artifacts/composer-workflows"
BASE = Path.home() / ".local/share/workbench"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def curl(url: str) -> tuple[int, bytes]:
    result = subprocess.run(
        [
            "/usr/bin/curl",
            "--silent",
            "--show-error",
            "--max-time",
            "20",
            "-w",
            "\n%{http_code}",
            url,
        ],
        capture_output=True,
        check=True,
    )
    body, status = result.stdout.rsplit(b"\n", 1)
    return int(status), body


def parity() -> int:
    names = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", "27dfaa3a", "--", "server/app"],
        cwd=ROOT,
        text=True,
    ).splitlines()
    for name in names:
        expected = subprocess.check_output(["git", "show", "27dfaa3a:" + name], cwd=ROOT)
        if (ROOT / name).read_bytes() != expected or (BASE / "app" / name).read_bytes() != expected:
            raise RuntimeError("Stable server parity failed: " + name)
    return len(names)


def atomic_copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".composer-publish")
    shutil.copy2(source, temporary)
    os.replace(temporary, destination)


def main(apply: bool) -> None:
    release = json.loads((EVIDENCE / "release-manifest.json").read_text())
    source = ROOT / "server/app/static"
    for name, expected in release["static_files"].items():
        if sha(source / name) != expected:
            raise RuntimeError("Build changed after validation: " + name)
    if not release["within_budget"]:
        raise RuntimeError("Initial JavaScript exceeds the existing release budget")
    gates = json.loads((EVIDENCE / "release-gates.json").read_text())
    if not (
        gates.get("all_passed") is True
        and gates.get("make_check_exit") == 0
        and gates.get("full_browser_exit") == 0
        and gates.get("failed_tests") == 0
    ):
        raise RuntimeError("Release gates have not passed")
    plist, service = existing_service()
    plist_hash = sha(plist)
    tailscale = "/Applications/Tailscale.app/Contents/MacOS/Tailscale"
    route = subprocess.check_output([tailscale, "serve", "status"], text=True)
    if "http://127.0.0.1:8787" not in route:
        raise RuntimeError("Existing Tailscale route changed")
    match = re.search(r"https://[^\s(]+", route)
    if not match:
        raise RuntimeError("Existing HTTPS endpoint unavailable")
    remote = match[0].rstrip("/")
    before_count = parity()
    if not apply:
        print(
            json.dumps(
                {
                    "apply": False,
                    "stable_server_files": before_count,
                    "static_files": len(release["static_files"]),
                }
            )
        )
        return
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    fallback = BASE / "data/backups" / ("composer-static-" + stamp)
    fallback.mkdir(mode=0o700)
    target = BASE / "app/server/app/static"
    shutil.copytree(target, fallback / "static")
    database = fallback / "workbench.db"
    database.touch(mode=0o600)
    with sqlite3.connect((BASE / "data/workbench.db").as_uri() + "?mode=ro", uri=True) as db:
        with sqlite3.connect(database) as backup:
            db.backup(backup)
    record = {
        "published": False,
        "source_commit": release["source_commit"],
        "stable_server_baseline": "27dfaa3a",
        "private_fallback_directory": str(fallback),
        "runtime_restarted": False,
        "saved_settings_changed": False,
        "method": "Static only; old hashed assets retained; index then service worker last",
    }
    try:
        for name in release["static_files"]:
            if name not in ("index.html", "sw.js"):
                atomic_copy(source / name, target / name)
        for name in ("index.html", "sw.js"):
            atomic_copy(source / name, target / name)
        for prefix in ("http://127.0.0.1:8787", remote):
            status, body = curl(prefix + "/api/health")
            if status != 200 or json.loads(body).get("ok") is not True:
                raise RuntimeError("Post-publication health check failed")
            for name in ("index.html", "sw.js"):
                status, body = curl(prefix + "/" + name)
                if (
                    status != 200
                    or hashlib.sha256(body).hexdigest() != release["static_files"][name]
                ):
                    raise RuntimeError("Published frontend hash mismatch")
        status, _ = curl("http://127.0.0.1:8787/design")
        if status != 404 or sha(plist) != plist_hash or parity() != before_count:
            raise RuntimeError("Deployment invariants changed")
        if subprocess.check_output([tailscale, "serve", "status"], text=True) != route:
            raise RuntimeError("Tailscale route changed")
        record.update(
            published=True,
            published_utc=datetime.now(UTC).isoformat(),
            stable_server_files=before_count,
            health="local and HTTPS both 200",
            service_label=service["Label"],
            service_identity_unchanged=True,
            production_design_status=404,
            service_worker_sha256=sha(target / "sw.js"),
        )
    except BaseException as exc:
        record["error"] = str(exc)
        for path in (fallback / "static").rglob("*"):
            if path.is_file():
                atomic_copy(path, target / path.relative_to(fallback / "static"))
        record["rolled_back_static"] = True
        record["restored_index_sha256"] = sha(target / "index.html")
        raise
    finally:
        with (EVIDENCE / ("publication-" + stamp + ".json")).open("x") as output:
            output.write(json.dumps(record, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    main(parser.parse_args().apply)
