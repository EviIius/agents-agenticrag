"""Only synthetic fixtures: these tests must never contain a real recording."""

import asyncio
import json
import shutil
from pathlib import Path
from typing import Any

import httpx
import pytest
from fastapi import FastAPI

from app.api import attachments as upload_api
from app.db import attachments
from app.errors import AppError
from app.transcribe.engine import Engine
from app.transcribe.jobs import Job
from tests.test_chat import finish

pytest_plugins = ["tests.test_chat"]

FAKE = Path(__file__).parent / "fake_transcribe"


async def upload(
    app: FastAPI, client: httpx.AsyncClient, directive: str = "fake"
) -> dict[str, Any]:
    await client.patch("/api/settings", json={"transcription.keep_audio": True})
    app.state.transcription.engine = Engine(FAKE)
    response = await client.post(
        "/api/attachments", files={"file": ("Synthetic.wav", directive.encode(), "audio/wav")}
    )
    assert response.status_code == 201, response.text
    return dict(response.json())


async def ready(app: FastAPI, item: dict[str, Any]) -> dict[str, Any]:
    await app.state.transcription.jobs[item["id"]].task
    return (await attachments.attachment(app.state.store, item["id"])).model_dump()


async def test_engine_contract(tmp_path: Path) -> None:
    engine = Engine(FAKE)
    state = await engine.status()
    assert state.ready and state.version == "fake-0.1.0"
    assert await engine.status() is state
    assert not (await Engine(None).status()).ready
    audio = tmp_path / "synthetic.wav"
    audio.write_text("fake")
    result = await engine.run(audio, tmp_path / "out", "split")
    assert result["channel_mode"] == "split" and len(result["segments"]) == 3
    audio.write_text("#fake:fail Synthetic unreadable audio")
    with pytest.raises(AppError, match="Synthetic unreadable audio"):
        await engine.run(audio, tmp_path / "out", "mix")
    audio.write_text("#fake:slow 30")
    task = asyncio.create_task(engine.run(audio, tmp_path / "out", "mix"))
    await asyncio.sleep(0.15)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    broken = tmp_path / "broken"
    (broken / "bin").mkdir(parents=True)
    script = broken / "bin/transcribe"
    script.write_text("#!/bin/sh\nprintf invalid")
    script.chmod(0o700)
    assert not (await Engine(broken).status()).ready


async def test_upload_limits_disk_headroom_and_pending(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI], monkeypatch: pytest.MonkeyPatch
) -> None:
    app, client, _ = chat_app
    response = await client.post("/api/attachments", files={"file": ("Synthetic.wav", b"fake")})
    assert response.json()["error"]["code"] == "transcription_unavailable"
    assert (await client.get("/api/transcription/status")).json()["configured"] is False
    assert (await client.get("/api/_schema/transcription-event")).json()["type"] == "stream.closed"
    item = await upload(app, client)
    assert item["transcript"]["status"] == "queued"
    assert (await client.get("/api/attachments/pending")).json()[0]["id"] == item["id"]
    await ready(app, item)
    target = next((app.state.config.data_dir / "attachments").glob("*.wav"))
    assert target.stat().st_mode & 0o777 == 0o600
    monkeypatch.setattr(upload_api, "AUDIO_LIMIT", 5)
    response = await client.post("/api/attachments", files={"file": ("Synthetic.wav", b"123456")})
    assert response.status_code == 413
    assert len(list(target.parent.iterdir())) == 1
    assert not list(target.parent.glob("*.part"))
    monkeypatch.setattr(shutil, "disk_usage", lambda _: shutil._ntuple_diskusage(100, 100, 0))
    response = await client.post("/api/attachments", files={"file": ("Synthetic.wav", b"fake")})
    assert response.status_code == 507


async def test_jobs_replay_snapshots_retry_cancel_recover_housekeeping(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, _ = chat_app
    one = await upload(app, client, "#fake:slow 30")
    two = await upload(app, client)
    manager = app.state.transcription
    assert manager.jobs[two["id"]].events[0].data["position"] == 2
    assert (await client.get("/api/attachments/" + one["id"] + "/transcript")).status_code == 409
    assert (
        await client.post("/api/attachments/" + one["id"] + "/transcribe", json={})
    ).status_code == 409
    await client.post("/api/attachments/" + one["id"] + "/cancel")
    assert (await attachments.attachment(app.state.store, one["id"])).model_dump()["transcript"][
        "status"
    ] == "cancelled"
    await ready(app, two)
    events = await client.get(
        "/api/attachments/" + two["id"] + "/events", headers={"last-event-id": "1"}
    )
    assert "id: 1\r\n" not in events.text and "transcription.done" in events.text
    manager.expire(manager.jobs[two["id"]])
    assert (
        "transcription.done" in (await client.get("/api/attachments/" + two["id"] + "/events")).text
    )
    failed = await upload(app, client, "#fake:fail Synthetic decoder failure")
    result = await ready(app, failed)
    assert result["transcript"]["error"]["message"] == "Synthetic decoder failure"
    path = (await app.state.store.one("SELECT path FROM attachments WHERE id=?", (failed["id"],)))[
        "path"
    ]
    (app.state.config.data_dir / path).write_text("fake")
    retry = await client.post(
        "/api/attachments/" + failed["id"] + "/transcribe", json={"channels": "split"}
    )
    assert retry.status_code == 202
    assert (await ready(app, failed))["transcript"]["channels"] == "split"
    interrupted = await upload(app, client, "#fake:slow 30")
    await manager.close()
    assert (await attachments.attachment(app.state.store, interrupted["id"])).model_dump()[
        "transcript"
    ]["error"]["code"] == "transcription_interrupted"
    await app.state.store.execute(
        "UPDATE transcripts SET status='transcribing',cleanup_status='running' "
        "WHERE attachment_id=?",
        (interrupted["id"],),
    )
    scratch = app.state.config.data_dir / "transcribe-tmp" / "fake"
    scratch.mkdir(parents=True)
    await manager.recover()
    assert not scratch.exists()
    await app.state.store.execute(
        "UPDATE attachments SET created_at='2000-01-01' WHERE id=?", (one["id"],)
    )
    await manager.housekeeping()
    assert not await app.state.store.one("SELECT id FROM attachments WHERE id=?", (one["id"],))
    assert (await client.delete("/api/attachments/" + two["id"])).status_code == 204
    assert (await client.get("/api/attachments/" + two["id"])).status_code == 404
    assert not list((app.state.config.data_dir / "transcribe-tmp").glob("*"))
    # Queued cancellation before the task's first instruction also persists its state.
    manager.semaphore = asyncio.Semaphore(0)
    queued = await upload(app, client)
    await manager.cancel(queued["id"])
    assert (await attachments.attachment(app.state.store, queued["id"])).model_dump()["transcript"][
        "status"
    ] == "cancelled"
    job = Job("synthetic")
    await job.emit("stream.closed", {})
    assert len([event async for event in job.tail(0)]) == 1


async def test_send_context_guard_downloads_delete(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, runtime = chat_app
    item = await upload(app, client, "#fake:slow 1")
    conn = (await client.get("/api/connections")).json()[0]["id"]
    chat = (
        await client.post(
            "/api/chats", json={"connection_id": conn, "model_id": "fake-chat", "web_enabled": True}
        )
    ).json()
    body = {
        "content": "Summarize this recording.",
        "attachment_ids": [item["id"]],
        "parent_id": None,
        "web": True,
    }
    response = await client.post("/api/chats/" + chat["id"] + "/messages", json=body)
    assert (
        response.status_code == 422 and response.json()["error"]["code"] == "transcript_not_ready"
    )
    await ready(app, item)
    # Fail the test if any web pipeline request is made with the recording guard on.
    old = app.state.runs.web_hook

    async def forbidden(*_: Any) -> None:
        raise AssertionError("Recording was sent to search")

    app.state.runs.web_hook = forbidden
    response = await client.post("/api/chats/" + chat["id"] + "/messages", json=body)
    assert response.status_code == 202, response.text
    run = await finish(app, response.json())
    assert run.message.web.notice.code == "search_blocked_recording"
    captured = runtime.state.captures[-1]["messages"][-1]["content"]
    assert captured.startswith(
        '<transcript name="Synthetic.wav" duration="0:01:15">\nFake transcript.'
    )
    assert captured.endswith("\n</transcript>\nSummarize this recording.")
    follow = await client.post(
        "/api/chats/" + chat["id"] + "/messages",
        json={"content": "What was decided?", "parent_id": run.message.id},
    )
    next_run = await finish(app, follow.json())
    assert any("<transcript" in m["content"] for m in runtime.state.captures[-1]["messages"])
    regen = await client.post(
        "/api/messages/" + next_run.message.id + "/regenerate", json={"force_web": True}
    )
    assert (await finish(app, regen.json())).message.web.notice.code == "search_blocked_recording"
    called = []

    async def allowed(*_: Any) -> None:
        called.append(True)

    app.state.runs.web_hook = allowed
    await client.patch("/api/settings", json={"transcription.block_web": False})
    regen = await client.post(
        "/api/messages/" + next_run.message.id + "/regenerate", json={"force_web": True}
    )
    await finish(app, regen.json())
    assert called
    app.state.runs.web_hook = old
    transcript = (await client.get("/api/attachments/" + item["id"] + "/transcript")).json()
    assert len(transcript["segments"]) == 3
    for fmt in ["txt", "srt", "json"]:
        download = await client.get(
            "/api/attachments/" + item["id"] + "/transcript/download?format=" + fmt
        )
        assert (
            download.status_code == 200
            and "Synthetic." + fmt in download.headers["content-disposition"]
        )
        if fmt == "srt":
            assert "00:00:00,000 --> 00:00:25,000" in download.text
        if fmt == "json":
            assert json.loads(download.text)["text"] == transcript["text"]
    assert (
        await client.get("/api/attachments/" + item["id"] + "/transcript/download?format=html")
    ).status_code == 422
    assert (await client.delete("/api/attachments/" + item["id"])).status_code == 409
    assert (await client.get("/api/attachments/pending")).json() == []
    path = (await app.state.store.one("SELECT path FROM attachments WHERE id=?", (item["id"],)))[
        "path"
    ]
    assert (await client.delete("/api/chats/" + chat["id"])).status_code == 204
    assert not (app.state.config.data_dir / path).exists()
    assert not await app.state.store.one(
        "SELECT * FROM transcripts WHERE attachment_id=?", (item["id"],)
    )


async def test_overflow_silence_glossary_local_only(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, _ = chat_app
    item = await upload(app, client, "#fake:words 20000")
    await ready(app, item)
    conn = (await client.get("/api/connections")).json()[0]["id"]
    chat = (
        await client.post("/api/chats", json={"connection_id": conn, "model_id": "fake-chat"})
    ).json()
    body = {"content": "Summarize", "attachment_ids": [item["id"]], "parent_id": None}
    response = await client.post("/api/chats/" + chat["id"] + "/messages", json=body)
    assert response.json()["error"]["code"] == "context_overflow"
    await app.state.store.execute(
        "UPDATE connections SET base_url='https://remote.example' WHERE id=?", (conn,)
    )
    response = await client.post("/api/chats/" + chat["id"] + "/messages", json=body)
    assert response.json()["error"]["code"] == "recording_requires_local"
    silence = await upload(app, client, "#fake:silence")
    assert (await ready(app, silence))["transcript"]["word_count"] == 0
    glossary = await upload(app, client, "#fake:glossary")
    assert (await ready(app, glossary))["transcript"]["correction_count"] == 1
    raw = await client.get(
        "/api/attachments/" + glossary["id"] + "/transcript/download?variant=raw"
    )
    assert "Gismo" in raw.text


async def test_version_one_migration_keeps_attachments(tmp_path: Path) -> None:
    import aiosqlite

    from app.db.core import MIGRATIONS, connect

    tmp_path.mkdir(exist_ok=True)
    async with aiosqlite.connect(tmp_path / "workbench.db") as db:
        await db.executescript((MIGRATIONS / "001_init.sql").read_text())
        await db.execute("PRAGMA user_version=1")
        await db.execute(
            "INSERT INTO attachments(id,kind,filename,mime_type,bytes,path,created_at) "
            "VALUES ('old','text','synthetic.txt','text/plain',4,'attachments/old.txt',"
            "'2000-01-01')"
        )
        await db.commit()
    async with connect(tmp_path) as db:
        async with db.execute("SELECT id,kind,filename FROM attachments") as cursor:
            assert await cursor.fetchone() == ("old", "text", "synthetic.txt")
        await db.execute(
            "INSERT INTO attachments(id,kind,filename,mime_type,bytes,path,created_at) "
            "VALUES ('new','audio','synthetic.wav','audio/wav',4,'attachments/new.wav',"
            "'2000-01-01')"
        )


async def test_temporary_audio_keeps_outputs_and_bulk_clear_skips_active(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, _ = chat_app
    assert (await client.get("/api/settings")).json()["transcription.keep_audio"] is False
    item = await upload(app, client, "#fake:slow 0.2")
    await client.patch("/api/settings", json={"transcription.keep_audio": False})
    result = await ready(app, item)
    assert result["audio_available"] is False
    assert result["transcript"]["status"] == "ready"
    assert (await client.get(f"/api/attachments/{item['id']}")).status_code == 404
    before = (await client.get(f"/api/attachments/{item['id']}/transcript")).json()
    for fmt in ("txt", "srt", "json"):
        assert (
            await client.get(f"/api/attachments/{item['id']}/transcript/download?format={fmt}")
        ).status_code == 200
    assert (await client.post(f"/api/attachments/{item['id']}/transcribe", json={})).json()[
        "error"
    ]["code"] == "audio_removed"
    assert (await client.get(f"/api/attachments/{item['id']}/transcript")).json() == before
    retained = await upload(app, client)
    assert (await ready(app, retained))["audio_available"] is True
    failed = await upload(app, client, "#fake:fail Synthetic failure")
    await ready(app, failed)
    active = await upload(app, client, "#fake:slow 30")
    stats = (await client.get("/api/transcription/audio-storage")).json()
    assert stats["files"] == 3 and stats["active_files"] == 1
    removed = (await client.delete("/api/transcription/audio-storage")).json()
    assert removed["files"] == 2 and removed["bytes"] > 0
    assert (await client.get("/api/transcription/audio-storage")).json()["files"] == 1
    assert (await client.get(f"/api/attachments/{retained['id']}/transcript")).status_code == 200
    assert (await client.delete("/api/transcription/audio-storage")).json()["files"] == 0
    await client.post(f"/api/attachments/{active['id']}/cancel")
    await client.delete("/api/transcription/audio-storage")
    assert (await client.get("/api/transcription/audio-storage")).json()["files"] == 0
    # Recovery frees historical completed audio without touching its output.
    historical = await upload(app, client)
    await ready(app, historical)
    await client.patch("/api/settings", json={"transcription.keep_audio": False})
    await app.state.transcription.close()
    await app.state.transcription.recover()
    assert (await client.get(f"/api/attachments/{historical['id']}/transcript")).status_code == 200
    assert (await client.get(f"/api/attachments/{historical['id']}")).status_code == 404

    await app.state.store.execute(
        "UPDATE attachments SET created_at='2000-01-01' WHERE id=?", (historical["id"],)
    )
    await app.state.transcription.housekeeping()
    assert (await client.get(f"/api/attachments/{historical['id']}/transcript")).status_code == 200
