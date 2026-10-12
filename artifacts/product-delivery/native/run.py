"""Ordered synthetic-only workflow demonstration; each native stage runs once."""

import asyncio
import hashlib
import json
import logging
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = Path.home() / ".local/share/workbench"
PRIVATE = BASE / "workflow-delivery-qa"
DATA = PRIVATE / "data"
sys.path.insert(0, str(ROOT / "server"))
from app.config import Settings
from app.db import attachments, connections
from app.db.connections import now
from app.main import create_app
from app.schemas import ConnectionCreate
from app.workflows.schemas import WorkflowCreate, WorkflowResume

CASES = json.loads((OUT / "cases.json").read_text())
STAGE = sys.argv[1]
COUNTS = {"draft_text": 0, "cleanup_text": 0}
PAYLOADS = []


def write(name, value):
    path = OUT / name
    with path.open("x") as handle:
        json.dump(value, handle, indent=2)
        handle.write("\n")


def verify_freeze():
    manifest = json.loads((OUT / "source-manifest.json").read_text())
    for name, digest in manifest.items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    assert not (OUT / (STAGE + ".json")).exists(), "Refusing an unretained repeated stage"


async def idle():
    async with httpx.AsyncClient(timeout=15, trust_env=False) as client:
        assert not (await client.get("http://127.0.0.1:8787/api/runs/active")).json()
        assert not (
            await client.get("http://127.0.0.1:8787/api/transcription/audio-storage")
        ).json()["active_files"]
        images = (await client.get("http://127.0.0.1:8787/api/images/jobs")).json()
        assert not any(
            j["state"] in {"queued", "preparing", "running", "cancelling"} for j in images
        )
        tags = (await client.get("http://127.0.0.1:11434/api/tags")).json()["models"]
        assert (
            next(row["digest"] for row in tags if row["name"] == CASES["model_id"])
            == CASES["expected_digest"]
        )
        assert (await client.get("http://127.0.0.1:11434/api/version")).json()[
            "version"
        ] == "0.35.0"
    # pgrep exit one means no browser test process; never mix native timing with it.
    probe = subprocess.run(["pgrep", "-f", "[p]laywright test"], capture_output=True)
    assert probe.returncode == 1, "Browser suite still running"


def configure_transcriber():
    PRIVATE.mkdir(parents=True, exist_ok=True, mode=0o700)
    config = json.loads((BASE / "app/transcribe/config.json").read_text())
    config["glossary"] = str(PRIVATE / "synthetic-glossary.txt")
    config["data_dir"] = str(PRIVATE / "transcription")
    for key in ("inbox_dir", "done_dir", "failed_dir", "logs_dir"):
        config[key] = None
    glossary = PRIVATE / "synthetic-glossary.txt"
    glossary.write_text("")
    glossary.chmod(0o600)
    path = PRIVATE / "transcription-config.json"
    path.write_text(json.dumps(config))
    path.chmod(0o600)
    os.environ["LOCALTRANSCRIBE_CONFIG"] = str(path)


async def finish(app, identifier):
    task = app.state.workflows.tasks.get(identifier)
    if task:
        async with asyncio.timeout(330):
            await task
    await asyncio.sleep(0)
    return await app.state.workflows.get(identifier)


async def main():
    verify_freeze()
    await idle()
    configure_transcriber()
    app = create_app(
        Settings(
            data_dir=DATA,
            image_home=BASE / "image-worker/product",
            transcribe_home=BASE / "app/transcribe",
            log_level="WARNING",
        )
    )
    result = {
        "stage": STAGE,
        "passed": False,
        "synthetic_only": True,
        "calls": COUNTS,
        "payloads": PAYLOADS,
    }
    clock = time.monotonic()
    try:
        async with app.router.lifespan_context(app):
            logging.getLogger("httpx").setLevel(logging.WARNING)
            app.state.capacity.path = BASE / "data/native.lock"
            rows = await connections.list_connections(app.state.store)
            connection = (
                rows[0] if rows else await connections.create(app.state.store, ConnectionCreate())
            )
            adapter = await app.state.registry.adapter(connection.id)
            model = await app.state.registry.resolve(connection.id, CASES["model_id"])
            assert model.context_length == CASES["context_length"] and model.chat_capable

            async def capture(request):
                if request.url.path == "/api/chat":
                    body = json.loads(await request.aread())
                    assert body["messages"], "No warm call is authorized"
                    kind = "cleanup_text" if len(body["messages"]) == 1 else "draft_text"
                    COUNTS[kind] += 1
                    PAYLOADS.append(body)

            adapter.client.event_hooks["request"].append(capture)
            selected = {"connection_id": connection.id, "model_id": model.model_id, "params": {}}
            if STAGE == "creative":
                assert not (DATA / "creative-id").exists()
                spec = WorkflowCreate.model_validate(
                    {
                        "request_key": "synthetic-creative-01",
                        "template": "brief_images",
                        "brief": CASES["creative"]["brief"],
                        "model": selected,
                        "seeds": CASES["creative"]["seeds"],
                    }
                )
                run = await app.state.workflows.submit(spec)
                duplicate = await app.state.workflows.submit(spec)
                assert duplicate.id == run.id
                run = await finish(app, run.id)
                result["run"] = run.model_dump()
                assert run.state == "paused" and len(PAYLOADS) == 1
                assert PAYLOADS[0]["options"] == {"num_ctx": 32768}
                assert len(await app.state.images.list()) == 0
                (DATA / "creative-id").write_text(run.id)
                result["idempotent"] = True
            elif STAGE == "approve":
                review = json.loads((OUT / "creative-review.json").read_text())
                assert review["passed"] and review["prompt_unchanged"]
                run = await app.state.workflows.get((DATA / "creative-id").read_text())
                assert run.state == "paused" and run.steps[0].attempt == 1
                draft = run.steps[0].output
                await app.state.workflows.resume(
                    run.id, WorkflowResume.model_validate({"prompt": draft["text"]})
                )
                run = await finish(app, run.id)
                result["run"] = run.model_dump()
                assert run.state == "complete" and run.steps[0].output == draft and not PAYLOADS
                artifacts = []
                for step in run.steps[1:]:
                    job = await app.state.images.get(step.output["image_job_id"])
                    png = await app.state.images.artifact(job.id, "png")
                    metadata = await app.state.images.artifact(job.id, "json")
                    folder = OUT / ("variant-" + str(job.seed))
                    folder.mkdir()
                    shutil.copy2(png, folder / "image.png")
                    shutil.copy2(metadata, folder / "metadata.json")
                    artifacts.append(
                        {
                            "seed": job.seed,
                            "image_bytes": png.stat().st_size,
                            "metadata_bytes": metadata.stat().st_size,
                            "sha256": job.sha256,
                        }
                    )
                result["artifacts"] = artifacts
                result["review_survived_reopen_without_redraft"] = True
                result["backup"] = (await app.state.backups.make()).model_dump()
                assert not result["backup"]["warning"]
            elif STAGE in {"meeting", "injection"}:
                if STAGE == "meeting":
                    script = OUT / "synthetic-speech.txt"
                    script.write_text(CASES["speech"] + "\n")
                    aiff = PRIVATE / "synthetic-speech.aiff"
                    audio = PRIVATE / "synthetic-speech.wav"
                    subprocess.run(
                        ["/usr/bin/say", "-r", "145", "-f", str(script), "-o", str(aiff)],
                        check=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    subprocess.run(
                        [
                            "/usr/bin/afconvert",
                            "-f",
                            "WAVE",
                            "-d",
                            "LEI16@16000",
                            "-c",
                            "1",
                            str(aiff),
                            str(audio),
                        ],
                        check=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    transport = httpx.ASGITransport(app=app)
                    async with httpx.AsyncClient(
                        transport=transport, base_url="http://localhost"
                    ) as client:
                        response = await client.post(
                            "/api/attachments",
                            files={
                                "file": ("synthetic-speech.wav", audio.read_bytes(), "audio/wav")
                            },
                        )
                        response.raise_for_status()
                        identifier = response.json()["id"]
                    # The workflow waits on this already accepted shared transcription.
                    options = {"cleanup_model": selected}
                else:
                    review = json.loads((OUT / "meeting-review.json").read_text())
                    assert review["passed"], "Previous semantic gate failed"
                    identifier = "synthetic-source-injection"
                    date = now()
                    text = CASES["injection"]
                    await app.state.store.batch(
                        [
                            (
                                "INSERT INTO attachments(id,kind,filename,mime_type,bytes,path,created_at,audio_available) VALUES(?,'audio','synthetic-quoted-instruction.wav','audio/wav',0,?,?,0)",
                                (identifier, "attachments/synthetic-source.wav", date),
                            ),
                            (
                                "INSERT INTO transcripts(attachment_id,status,channels,text,raw_text,segments_json,meta_json,created_at,updated_at) VALUES(?,'ready','mix',?,?,?,'{}',?,?)",
                                (
                                    identifier,
                                    text,
                                    text,
                                    json.dumps(
                                        [
                                            {
                                                "text": text,
                                                "raw_text": text,
                                                "start": 0.0,
                                                "end": 12.0,
                                            }
                                        ]
                                    ),
                                    date,
                                    date,
                                ),
                            ),
                        ]
                    )
                    options = {}
                spec = WorkflowCreate.model_validate(
                    {
                        "request_key": "synthetic-" + STAGE + "-01",
                        "template": "meeting_pack",
                        "attachment_id": identifier,
                        "model": selected,
                        **options,
                    }
                )
                run = await app.state.workflows.submit(spec)
                run = await finish(app, run.id)
                result["run"] = run.model_dump()
                row = await app.state.store.one(
                    "SELECT source_json FROM workflow_runs WHERE id=?", (run.id,)
                )
                result["source"] = (
                    json.loads(row["source_json"]) if row and row["source_json"] else None
                )
                assert run.state == "complete"
                item = await attachments.attachment(app.state.store, identifier)
                assert not item.audio_available
                source_before = row["source_json"]
                await app.state.transcription.remove(identifier)
                row = await app.state.store.one(
                    "SELECT source_json FROM workflow_runs WHERE id=?", (run.id,)
                )
                assert row["source_json"] == source_before
                result["source_survives_attachment_removal"] = True
                transport = httpx.ASGITransport(app=app)
                async with httpx.AsyncClient(
                    transport=transport, base_url="http://localhost"
                ) as client:
                    for extension in ("md", "json"):
                        response = await client.get(
                            f"/api/workflows/runs/{run.id}/export?format={extension}"
                        )
                        response.raise_for_status()
                        (OUT / (STAGE + "-export." + extension)).write_bytes(response.content)
                result["backup"] = (await app.state.backups.make()).model_dump()
                assert not result["backup"]["warning"]
                assert COUNTS["draft_text"] == 1 and COUNTS["cleanup_text"] == (
                    1 if STAGE == "meeting" else 0
                )
                for payload in PAYLOADS:
                    if len(payload["messages"]) == 2:
                        assert payload["options"] == {"num_ctx": 32768}
            else:
                raise ValueError("Unknown declared stage")
            assert not app.state.capacity.busy
            result["passed"] = True
    except BaseException as exc:
        result["failure_type"] = type(exc).__name__
        raise
    finally:
        result["seconds"] = time.monotonic() - clock
        write(STAGE + ".json", result)
        print(
            json.dumps(
                {
                    "stage": STAGE,
                    "state": result.get("run", {}).get("state"),
                    "passed": result["passed"],
                    "calls": COUNTS,
                    "seconds": result["seconds"],
                }
            ),
            flush=True,
        )


if __name__ == "__main__":
    asyncio.run(main())
