"""Static-only Tools repair; no launchd, database, model or worker mutation."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

import httpx

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
BASE = Path.home() / ".local/share/workbench"
TARGET = BASE / "app/server/app/static"
PRIVATE = BASE / "releases/mobile-tools-capped-20261021"
SOURCE = ROOT / "server/app/static"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def files(root, exclude=()):
    return {str(p.relative_to(root)): sha(p) for p in sorted(root.rglob("*")) if p.is_file() and not p.is_symlink() and "__pycache__" not in p.parts and p.relative_to(root).parts[0] not in exclude}


def protected():
    code = files(BASE / "app/server/app", ("static",))
    code.update({"shared/" + k: v for k, v in files(BASE / "app/shared").items()})
    worker = files(BASE / "image-worker/product")
    plist = Path.home() / "Library/LaunchAgents/dev.agenticrag.workbench.plist"
    status = subprocess.check_output(["launchctl", "print", f"gui/{os.getuid()}/dev.agenticrag.workbench"], text=True)
    pid = int(re.search(r"\bpid = (\d+)", status)[1])
    return {"code_files": len(code), "code_sha256": hashlib.sha256(json.dumps(code, sort_keys=True).encode()).hexdigest(), "worker_sha256": hashlib.sha256(json.dumps(worker, sort_keys=True).encode()).hexdigest(), "plist_sha256": sha(plist), "service_pid": pid}


def replace(path, raw):
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    assert not path.is_symlink()
    fd, temporary = tempfile.mkstemp(prefix=".tools-publish-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            os.fchmod(stream.fileno(), 0o600)
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


frozen = json.loads((OUT / "source-capped.json").read_text())["files"]
assert all(sha(ROOT / p) == digest for p, digest in frozen.items())
incoming = files(SOURCE)
old = files(TARGET)
before = protected()
PRIVATE.mkdir(mode=0o700, parents=True, exist_ok=False)
shutil.copytree(TARGET, PRIVATE / "static-before")
assert files(PRIVATE / "static-before") == old
(PRIVATE / "source-manifest.json").write_text(json.dumps(incoming, indent=2) + "\n")
record = {"published": False, "native_calls": 0, "backend_or_data_changes": False, "service_restart": False, "protected_before": before, "private_backup": str(PRIVATE), "built_files": len(incoming)}
try:
    # Hashed assets are immutable and retained for already-open clients.
    for name, digest in incoming.items():
        if name in ("index.html", "sw.js"):
            continue
        if name.startswith("assets/") and name in old:
            assert old[name] == digest, "Immutable asset collision"
        if old.get(name) != digest:
            replace(TARGET / name, (SOURCE / name).read_bytes())
    for name in ("index.html", "sw.js"):
        replace(TARGET / name, (SOURCE / name).read_bytes())
    assert all(sha(TARGET / name) == digest for name, digest in incoming.items())
    assert all(sha(TARGET / name) == digest for name, digest in old.items() if name.startswith("assets/"))
    assert protected() == before
    with httpx.Client(timeout=10, trust_env=False) as client:
        for origin in ("http://127.0.0.1:8787", "https://jakes-mac-mini.tailc4d343.ts.net"):
            response = client.get(origin + "/api/health"); response.raise_for_status(); assert response.json()["ok"]
            for name in ("index.html", "sw.js"):
                response = client.get(origin + "/" + name); response.raise_for_status()
                assert hashlib.sha256(response.content).hexdigest() == incoming[name]
    record.update(published=True, installed_candidate_files_verified=len(incoming), previous_hashed_assets_retained=sum(name.startswith("assets/") for name in old), local_and_verified_https=True, same_service_pid=True)
except BaseException:
    # Restore previous entry/UI files only. Keep all data and both asset sets.
    for name in old:
        replace(TARGET / name, (PRIVATE / "static-before" / name).read_bytes())
    record["previous_ui_restored"] = True
    raise
finally:
    (OUT / "publication-capped.json").write_text(json.dumps(record, indent=2) + "\n")
    (PRIVATE / "result.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps(record, indent=2))
