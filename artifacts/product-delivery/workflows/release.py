"""Private rollback snapshot and hash-only release verification; no user content logs."""

import asyncio
import hashlib
import json
import plistlib
import sqlite3
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import httpx
import sqlite_vec

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = Path.home() / ".local/share/workbench"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    result = {}
    with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as db:
        db.enable_load_extension(True)
        sqlite_vec.load(db)
        db.enable_load_extension(False)
        tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        for (name,) in tables:
            if name.startswith("sqlite_") or name.startswith("chat_search"):
                continue
            quoted = '"' + name.replace('"', '""') + '"'
            data = [repr(tuple(row)) for row in db.execute("SELECT * FROM " + quoted)]
            result[name] = {
                "rows": len(data),
                "sha256": hashlib.sha256(json.dumps(sorted(data)).encode()).hexdigest(),
            }
    return result


async def idle():
    async with httpx.AsyncClient(timeout=10, trust_env=False) as client:
        runs = await client.get("http://127.0.0.1:8787/api/runs/active")
        audio = await client.get("http://127.0.0.1:8787/api/transcription/audio-storage")
        runs.raise_for_status()
        audio.raise_for_status()
        assert not runs.json() and not audio.json()["active_files"], "Active work; release held"
        images = await client.get("http://127.0.0.1:8787/api/images/jobs")
        images.raise_for_status()
        assert not any(
            j["state"] in {"queued", "preparing", "running", "cancelling"} for j in images.json()
        ), "Active images; release held"


def prepare():
    if (OUT / "prepared.json").exists():
        raise RuntimeError("A rollback snapshot is already prepared; inspect it before another copy.")
    asyncio.run(idle())

    async def backup():
        async with httpx.AsyncClient(timeout=90, trust_env=False) as client:
            response = await client.post("http://127.0.0.1:8787/api/backup")
            response.raise_for_status()
            assert response.json()["warning"] is None, "Output backup did not complete"

    asyncio.run(backup())
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
    private = BASE / "fallbacks" / ("workflows-delivery-" + stamp)
    private.mkdir(mode=0o700, parents=True)
    candidates = []
    for path in (Path.home() / "Library/LaunchAgents").glob("*.plist"):
        value = plistlib.loads(path.read_bytes())
        if value.get("Label") == "dev.agenticrag.workbench":
            candidates.append(path)
    assert len(candidates) == 1
    plist = candidates[0]
    (private / "service.plist").write_bytes(plist.read_bytes())
    subprocess.run(["/bin/cp", "-cR", str(BASE / "app"), str(private / "app")], check=True)
    with sqlite3.connect((BASE / "data/workbench.db").as_uri() + "?mode=ro", uri=True) as source:
        with sqlite3.connect(private / "workbench.db") as target:
            source.backup(target)
    previous = rows(private / "workbench.db")
    (private / "rows.json").write_text(json.dumps(previous, indent=2) + "\n")
    for path in (private / "workbench.db", private / "rows.json", private / "service.plist"):
        path.chmod(0o600)
    modules = {
        str(p.relative_to(ROOT / "server")): sha(p)
        for p in (ROOT / "server/app/search").glob("*.py")
    }
    assert all(sha(BASE / "app/server" / name) == value for name, value in modules.items())
    document = {
        "private_fallback": str(private),
        "plist": str(plist),
        "label": "dev.agenticrag.workbench",
        "old_tables": len(previous),
        "search_modules": modules,
        "old_database_sha256": sha(private / "workbench.db"),
        "no_real_recording_or_document_content_captured": True,
    }
    with (OUT / "prepared.json").open("x") as handle:
        json.dump(document, handle, indent=2)
    print(
        json.dumps(
            {
                "fallback_prepared": True,
                "old_tables": len(previous),
                "unchanged_search_modules": len(modules),
            }
        )
    )


async def verify():
    saved = json.loads((OUT / "prepared.json").read_text())
    private = Path(saved["private_fallback"])
    previous = json.loads((private / "rows.json").read_text())
    current = rows(BASE / "data/workbench.db")
    assert all(current.get(name) == value for name, value in previous.items()), (
        "Existing rows changed"
    )
    installed = BASE / "app/server"
    assert all(sha(installed / name) == value for name, value in saved["search_modules"].items())
    plist = plistlib.loads(Path(saved["plist"]).read_bytes())
    assert plist["Label"] == saved["label"]
    assert plist["EnvironmentVariables"]["WORKBENCH_IMAGE_HOME"] == str(
        BASE / "image-worker/product"
    )
    assert "8787" in plist["ProgramArguments"] and "127.0.0.1" in plist["ProgramArguments"]
    async with httpx.AsyncClient(timeout=15, trust_env=False) as client:
        health = {}
        for name, url in {
            "local": "http://127.0.0.1:8787/api/health",
            "https": "https://jakes-mac-mini.tailc4d343.ts.net/api/health",
            "images": "http://127.0.0.1:8787/api/images/status",
        }.items():
            response = await client.get(url)
            response.raise_for_status()
            health[name] = response.json()
        assert health["images"]["available"]
        response = await client.get("http://127.0.0.1:11434/api/version")
        assert response.json()["version"] == "0.35.0"
        response = await client.get("https://jakes-mac-mini.tailc4d343.ts.net/api/workflows")
        response.raise_for_status()
        assert isinstance(response.json()["runs"], list)
        health["workflow_snapshot_status"] = response.status_code
        for route in ("/workflows", "/images"):
            response = await client.get("https://jakes-mac-mini.tailc4d343.ts.net" + route)
            response.raise_for_status()
            assert '<div id="root"></div>' in response.text
        native_source = json.loads((OUT.parent / "release-server-manifest.json").read_text())
        assert all(sha(BASE / "app" / name) == digest for name, digest in native_source.items())
    result = {
        "old_tables_byte_equivalent": len(previous),
        "new_tables": sorted(set(current) - set(previous)),
        "search_modules_unchanged": len(saved["search_modules"]),
        "health": health,
        "service_identity_and_bind_unchanged": True,
        "ollama_version": "0.35.0",
    }
    result["installed_server_source_matches_release_manifest"] = len(native_source)
    (OUT / "verification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    import sys

    if sys.argv[-1] == "prepare":
        prepare()
    else:
        asyncio.run(verify())
