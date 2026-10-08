"""Real T2 smoke using generated speech, isolated data and an invented glossary.

Print only timing/counts. Never read an existing transcript or recording.
"""

import argparse
import asyncio
import hashlib
import json
import logging
import shutil
import sqlite3
import subprocess
import tempfile
from pathlib import Path
from time import monotonic
from typing import Any

import httpx

from app.config import Settings
from app.main import create_app

BASE = Path.home() / ".local/share/workbench"


async def rehearse() -> dict[str, object]:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    args = parser.parse_args()
    installed = BASE / "app/transcribe"
    private = installed / "glossary.txt"
    before = hashlib.sha256(private.read_bytes()).digest() if private.exists() else None
    with sqlite3.connect(f"file:{BASE}/data/workbench.db?mode=ro", uri=True) as db:
        values = {
            key: json.loads(value)
            for key, value in db.execute(
                "SELECT key,value_json FROM settings WHERE key='default_connection_id'"
            )
        }
        connection = db.execute(
            "SELECT base_url FROM connections WHERE id=?", (values["default_connection_id"],)
        ).fetchone()
        pref = db.execute(
            "SELECT context_length FROM model_prefs WHERE connection_id=? AND model_id=?",
            (values["default_connection_id"], args.model),
        ).fetchone()
    assert connection
    with tempfile.TemporaryDirectory(prefix="workbench-t2-synthetic-") as name:
        root = Path(name)
        root.chmod(0o700)
        home = root / "engine"
        home.mkdir(mode=0o700)
        for folder in ("bin", "localtranscribe"):
            shutil.copytree(
                installed / folder, home / folder, ignore=shutil.ignore_patterns("__pycache__")
            )
        shutil.copyfile(installed / ".python", home / ".python")
        config = json.loads((installed / "config.json").read_text())
        for key in ("model", "vad_model"):
            if value := config.get(key):
                path = Path(value).expanduser()
                config[key] = str(path if path.is_absolute() else installed / path)
        config["data_dir"] = str(root / "runtime")
        config["glossary"] = str(home / "glossary.txt")
        for folder in ("inbox", "done", "failed", "logs"):
            config[folder + "_dir"] = None
            (root / "runtime" / folder).mkdir(parents=True, mode=0o700)
        (home / "config.json").write_text(json.dumps(config))
        (home / "config.json").chmod(0o600)
        (home / "glossary.txt").write_text("Invented Aurora\nInvented Grove\n")
        (home / "glossary.txt").chmod(0o600)
        paragraph = (
            "This is an invented meeting about a lantern workshop. We need to count the "
            "lanterns before opening the orchard gate. The first team will check the blue "
            "crates and the second team will carry the empty baskets. Please keep the spare "
            "candles in the dry cupboard. We will meet again after lunch to review the "
            "delivery schedule. Nobody should change the order until the whole team has read "
            "it. The next step is to write down the count and leave a note beside the door. "
        )
        speech = " ".join([paragraph] * 12)
        speech = " ".join(speech.split()[:800])
        source = root / "invented-speech.txt"
        source.write_text(speech)
        audio = root / "invented-speech.aiff"
        subprocess.run(
            ["/usr/bin/say", "-r", "160", "-f", str(source), "-o", str(audio)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        app = create_app(
            Settings(data_dir=root / "data", transcribe_home=home, log_level="WARNING")
        )
        async with (
            app.router.lifespan_context(app),
            httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://localhost", timeout=300
            ) as client,
        ):
            status = await client.get("/api/transcription/status")
            assert status.json()["ready"]
            conn = (
                await client.post(
                    "/api/connections",
                    json={"name": "Invented verification connection", "base_url": connection[0]},
                )
            ).json()
            if pref and pref[0]:
                response = await client.put(
                    "/api/models/prefs",
                    json={
                        "connection_id": conn["id"],
                        "model_id": args.model,
                        "context_length": pref[0],
                    },
                )
                response.raise_for_status()
            transcription_start = monotonic()
            with audio.open("rb") as handle:
                response = await client.post(
                    "/api/attachments",
                    files={"file": ("Invented speech.aiff", handle, "audio/aiff")},
                )
            response.raise_for_status()
            identifier = response.json()["id"]
            await app.state.transcription.jobs[identifier].task
            original = (await client.get(f"/api/attachments/{identifier}/transcript")).json()

            def digest(value: dict[str, Any]) -> bytes:
                return hashlib.sha256(
                    json.dumps(
                        {key: value[key] for key in ("text", "raw_text", "segments")},
                        sort_keys=True,
                    ).encode()
                ).digest()

            started = monotonic()
            response = await client.post(
                f"/api/attachments/{identifier}/cleanup",
                json={"connection_id": conn["id"], "model_id": args.model},
            )
            response.raise_for_status()
            await app.state.transcription.jobs[identifier].task
            seconds = monotonic() - started
            final = (await client.get(f"/api/attachments/{identifier}/transcript")).json()
            info = final["attachment"]["transcript"]["cleanup"]
            after = hashlib.sha256(private.read_bytes()).digest() if private.exists() else None
            assert digest(original) == digest(final)
            assert before == after
            assert info["status"] == "ready"
            return {
                "synthetic_speech_words": len(speech.split()),
                "duration_seconds": original["attachment"]["transcript"]["duration_seconds"],
                "audio_bytes": audio.stat().st_size,
                "transcription_seconds": round(started - transcription_start, 3),
                "cleanup_seconds": round(seconds, 3),
                "model_id": args.model,
                "status": info["status"],
                "sections": info["chunks"],
                "kept_original": info["kept_original"],
                "changed_words": info["changed_words"],
                "original_fields_identical": digest(original) == digest(final),
                "production_glossary_unchanged": before == after,
                "isolated_data": True,
                "temporary_files_removed_on_exit": True,
                "new_model_call_stages": 1,
            }


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    try:
        print(json.dumps(asyncio.run(rehearse()), indent=2))
    except Exception:
        print(
            json.dumps(
                {
                    "passed": False,
                    "detail": (
                        "Synthetic real-runtime rehearsal did not complete; "
                        "no private output emitted."
                    ),
                }
            )
        )
        raise SystemExit(1) from None
