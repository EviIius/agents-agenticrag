"""T2 uses invented speech and terms only; no private engine data."""

import asyncio
import hashlib
import json
import math
import re
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

import httpx
import pytest
from fastapi import FastAPI

from app.db import attachments
from app.errors import AppError
from app.providers.base import ChatRequest, Finish, ProviderEvent, TextDelta
from app.transcribe import cleanup
from app.transcribe.cleanup import accept, changed_words, chunks, sections, tidy, words
from app.transcribe.glossary import GlossaryFile, validate
from tests.test_chat import finish, start
from tests.test_deployment import deployment
from tests.test_transcription import FAKE, ready, upload


async def record(app: FastAPI, client: httpx.AsyncClient, text: str) -> dict[str, Any]:
    item = await ready(app, await upload(app, client))
    await app.state.store.execute(
        "UPDATE transcripts SET text=? WHERE attachment_id=?", (text, item["id"])
    )
    return item


async def launch(app: FastAPI, client: httpx.AsyncClient, identifier: str) -> httpx.Response:
    return await client.post(
        f"/api/attachments/{identifier}/cleanup",
        json={"connection_id": app.state.test_connection, "model_id": "fake-chat"},
    )


async def original(app: FastAPI, identifier: str) -> str:
    row = await app.state.store.one(
        "SELECT text,raw_text,segments_json FROM transcripts WHERE attachment_id=?", (identifier,)
    )
    return hashlib.sha256(json.dumps(row, sort_keys=True).encode()).hexdigest()


def test_guard_vectors_chunking_and_frozen_active_prompt() -> None:
    root = Path(__file__).resolve().parents[2]
    for case in json.loads((root / "shared/cleanup_guard_cases.json").read_text()):
        assert accept(case["source"], case["cleaned"]) is case["accept"], case["name"]
    source = ("Invented lantern. Another sentence! " * 100) + "\n\n" + "word " * 1100
    parts = chunks(source)
    assert all(len(part) <= 2000 for part in parts)
    assert words("\n\n".join(parts)) == words(source)
    assert len(chunks("x" * 2100)) == 2
    assert changed_words("one two", "One, two!") == 0
    assert tidy("<think>synthetic reasoning</think><chunk>Lantern.</chunk>") == "Lantern."
    assert tidy(" plain ") == "plain"
    expected = re.search(
        r"### 6\.2 Prompt.*?```text\n(.*?)\n```",
        (root / "docs/TRANSCRIPTION-SPEC.md").read_text(),
        re.S,
    )
    assert expected and cleanup.PROMPT == expected[1]
    hashes = json.loads((root / "artifacts/baseline/prompt-hashes-phase3.json").read_text())
    assert (
        hashlib.sha256(cleanup.PROMPT.encode()).hexdigest() == hashes["transcription-cleanup-spec"]
    )
    split = sections("Speaker 1: invented lantern\n\nSpeaker 2: invented ember", True)
    assert split == [("Speaker 1: ", "invented lantern"), ("Speaker 2: ", "invented ember")]
    assert sections("plain unlabeled paragraph", True) == [("", "plain unlabeled paragraph")]


async def test_cleanup_guard_progress_versions_context_discard_and_request(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app, client, runtime = chat_app
    glossary = tmp_path / "invented-glossary.txt"
    glossary.write_text("Invented Orion = invented orion\n")
    monkeypatch.setenv("FAKE_TRANSCRIBE_GLOSSARY", str(glossary))
    source = (
        ("invented lantern ember orchard sky " * 55).strip()
        + "\n\n"
        + ("FAKE-REWRITE invented branch harvest seed " * 55).strip()
    )
    item = await record(app, client, source)
    before = await original(app, item["id"])
    started = await launch(app, client, item["id"])
    assert started.status_code == 202
    assert (await launch(app, client, item["id"])).status_code == 409
    job = app.state.transcription.jobs[item["id"]]
    await job.task
    value = (await client.get(f"/api/attachments/{item['id']}/transcript")).json()
    info = value["attachment"]["transcript"]["cleanup"]
    assert info["status"] == "ready" and info["kept_original"] >= 1
    assert info["done"] == info["chunks"] and info["elapsed_seconds"] >= 0
    assert "FAKE-REWRITE" in value["cleaned_text"]
    assert before == await original(app, item["id"])
    assert [e.type for e in job.events][0] == "cleanup.started"
    progress = [e.data for e in job.events if e.type == "cleanup.progress"]
    assert [p["done"] for p in progress] == list(range(1, info["chunks"] + 1))
    assert [e.type for e in job.events][-2:] == ["cleanup.done", "stream.closed"]
    captures = [b for b in runtime.state.captures if b.get("messages")]
    assert len(captures) == info["chunks"]
    for capture in captures:
        content = capture["messages"][0]["content"]
        assert len(capture["messages"]) == 1 and capture["messages"][0]["role"] == "user"
        assert "Spell these names exactly as written when they occur: Invented Orion." in content
        chunk = content.split("<chunk>\n")[-1].split("\n</chunk>")[0]
        assert "think" not in capture  # Runtime reports no reasoning capability for fake-chat.
        assert capture["options"] == {
            "temperature": 0,
            "num_predict": min(4096, math.ceil(len(chunk) * 0.5) + 128),
            "num_ctx": 16384,
        }
    txt = await client.get(
        f"/api/attachments/{item['id']}/transcript/download?format=txt&variant=best"
    )
    assert txt.text == value["cleaned_text"]
    assert (
        await client.get(
            f"/api/attachments/{item['id']}/transcript/download?format=srt&variant=best"
        )
    ).status_code == 422
    app.state.transcription.jobs.pop(item["id"])
    snapshot = await client.get(f"/api/attachments/{item['id']}/events")
    assert "event: cleanup.done" in snapshot.text
    chat = (
        await client.post(
            "/api/chats", json={"connection_id": app.state.test_connection, "model_id": "fake-chat"}
        )
    ).json()
    sent = await client.post(
        f"/api/chats/{chat['id']}/messages",
        json={"content": "Summarize invented speech", "attachment_ids": [item["id"]]},
    )
    await finish(app, sent.json())
    capture = runtime.state.captures[-1]
    assert value["cleaned_text"] in capture["messages"][-1]["content"]
    assert (await client.delete(f"/api/attachments/{item['id']}/cleanup")).status_code == 204
    value = (await client.get(f"/api/attachments/{item['id']}/transcript")).json()
    assert value["cleaned_text"] is None and value["attachment"]["transcript"]["cleanup"] is None
    assert before == await original(app, item["id"])


async def test_cleanup_rejections_timeout_cancel_and_local_guard(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI], monkeypatch: pytest.MonkeyPatch
) -> None:
    app, client, runtime = chat_app
    item = await record(app, client, "FAKE-REWRITE invented orchard lantern ember " * 50)
    before = await original(app, item["id"])
    await launch(app, client, item["id"])
    await app.state.transcription.jobs[item["id"]].task
    meta = (await attachments.attachment(app.state.store, item["id"])).transcript
    assert meta and meta.cleanup and meta.cleanup.status == "failed"
    assert meta.cleanup.error and "every section" in meta.cleanup.error.message
    monkeypatch.setattr(cleanup, "TIMEOUT", 0.001)
    await app.state.store.execute(
        "UPDATE transcripts SET text=? WHERE attachment_id=?", ("invented word " * 150, item["id"])
    )
    before = await original(app, item["id"])
    count = len(runtime.state.captures)
    await launch(app, client, item["id"])
    await app.state.transcription.jobs[item["id"]].task
    assert len(runtime.state.captures) == count + len(chunks("invented word " * 150))
    assert before == await original(app, item["id"])
    monkeypatch.setattr(cleanup, "TIMEOUT", 300)
    await launch(app, client, item["id"])
    await asyncio.sleep(0.02)
    await client.post(f"/api/attachments/{item['id']}/cancel", json={})
    assert before == await original(app, item["id"])
    value = (await client.get(f"/api/attachments/{item['id']}/transcript")).json()
    assert value["cleaned_text"] is None and value["attachment"]["transcript"]["status"] == "ready"
    # Also exercise cancellation before the task's first instruction.
    await launch(app, client, item["id"])
    await app.state.transcription.cancel(item["id"])
    assert app.state.transcription.jobs[item["id"]].closed
    assert before == await original(app, item["id"])
    count = len(runtime.state.captures)
    await app.state.store.execute(
        "UPDATE connections SET base_url=? WHERE id=?",
        ("https://example.org", app.state.test_connection),
    )
    response = await launch(app, client, item["id"])
    assert (
        response.status_code == 422
        and response.json()["error"]["code"] == "recording_requires_local"
    )
    assert len(runtime.state.captures) == count


async def test_twelve_chunks_yield_to_chat_and_split_labels(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI], monkeypatch: pytest.MonkeyPatch
) -> None:
    app, client, _ = chat_app
    item = await record(app, client, "\n\n".join("invented lantern ember " * 85 for _ in range(12)))
    request_started = asyncio.Event()
    calls: list[ChatRequest] = []
    adapter = await app.state.registry.adapter(app.state.test_connection)

    async def stream(req: ChatRequest) -> AsyncIterator[ProviderEvent]:
        calls.append(req)
        if req.messages[0].content.startswith("You are formatting"):
            assert req.reasoning == "off" and req.params["temperature"] == 0
            request_started.set()
            await asyncio.sleep(0.025)
            source = req.messages[0].content.split("<chunk>\n")[-1].split("\n</chunk>")[0]
            yield TextDelta(source + ".")
        else:
            yield TextDelta("Invented chat begins streaming.")
        yield Finish("stop")

    monkeypatch.setattr(adapter, "stream", stream)
    await launch(app, client, item["id"])
    await request_started.wait()
    response = await start(client, "Invented chat request", "fake-chat")
    run = await finish(app, response)
    assert run.message.status == "complete"
    job = app.state.transcription.jobs[item["id"]]
    assert not job.closed
    await job.task
    meta = (await attachments.attachment(app.state.store, item["id"])).transcript
    assert meta and meta.cleanup and meta.cleanup.chunks == 12
    position = next(i for i, r in enumerate(calls) if r.messages[0].role == "system")
    assert 0 < position < 12
    await app.state.store.execute(
        "UPDATE transcripts SET text=?,channels='split' WHERE attachment_id=?",
        ("Speaker 1: invented lantern\n\nSpeaker 2: invented ember", item["id"]),
    )
    await launch(app, client, item["id"])
    await app.state.transcription.jobs[item["id"]].task
    value = (await client.get(f"/api/attachments/{item['id']}/transcript")).json()
    assert value["cleaned_text"] == "Speaker 1: invented lantern.\n\nSpeaker 2: invented ember."
    assert all("Speaker " not in req.messages[0].content for req in calls[-2:])


async def test_glossary_validation_atomic_save_and_next_engine_prompt(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app, client, _ = chat_app
    glossary = tmp_path / "invented-glossary.txt"
    monkeypatch.setenv("FAKE_TRANSCRIBE_GLOSSARY", str(glossary))
    await upload(app, client)
    assert (await client.get("/api/transcription/glossary")).json() == {"text": "", "terms": []}
    response = await client.put(
        "/api/transcription/glossary",
        json={"text": "# Invented\r\nInvented Orion = invented orion\rInvented Ember"},
    )
    assert response.status_code == 200
    assert response.json()["terms"] == ["Invented Orion", "Invented Ember"]
    assert glossary.read_text() == "# Invented\nInvented Orion = invented orion\nInvented Ember\n"
    assert glossary.stat().st_mode & 0o777 == 0o600
    for text in ["nul\0", "x" * 65537, "\ud800"]:
        response = await client.put(
            "/api/transcription/glossary",
            content=json.dumps({"text": text}).encode(),
            headers={"content-type": "application/json"},
        )
        assert response.status_code == 422
    with pytest.raises(AppError):
        validate("x" * 65536)
    item = await ready(app, await upload(app, client))
    row = await app.state.store.one(
        "SELECT meta_json FROM transcripts WHERE attachment_id=?", (item["id"],)
    )
    assert "Invented Orion" in json.loads(row["meta_json"])["engine"]["prompt"]
    before = glossary.read_bytes()
    monkeypatch.setattr(
        "app.transcribe.glossary.os.replace", lambda *args: (_ for _ in ()).throw(OSError())
    )
    response = await client.put("/api/transcription/glossary", json={"text": "Invented changed"})
    assert response.status_code == 422 and glossary.read_bytes() == before
    assert not list(tmp_path.glob(".glossary-*.part"))
    glossary.write_bytes(b"\xff")
    assert (await client.get("/api/transcription/glossary")).status_code == 422


async def test_glossary_ui_save_survives_redeployment(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI], tmp_path: Path
) -> None:
    from app.transcribe.engine import Engine

    app, client, _ = chat_app
    source, target = tmp_path / "public-engine", tmp_path / "installed-engine"
    for folder in ("bin", "localtranscribe", "tests"):
        (source / folder).mkdir(parents=True)
    for name in (
        "README.md",
        "config.example.json",
        "glossary.example.txt",
        "install.sh",
        "uninstall.sh",
    ):
        (source / name).write_text("Invented public source")
    (source / "glossary.txt").write_text("Invented First\n")
    (source / "bin/transcribe").write_text("""#!/usr/bin/env python3
import json
from pathlib import Path
print(json.dumps({'ok':True,'version':'fake','checks':[],
 'paths':{'glossary':str(Path(__file__).resolve().parents[1]/'glossary.txt')},
 'audio_extensions':[]}))
""")
    (source / "bin/transcribe").chmod(0o700)
    module = deployment()
    module.install_engine(source, target)
    app.state.transcription.engine = Engine(target)
    response = await client.put(
        "/api/transcription/glossary", json={"text": "Invented Saved = invented variant"}
    )
    assert response.status_code == 200
    (source / "glossary.txt").write_text("Invented Source changed\n")
    module.install_engine(source, target)
    assert (await client.get("/api/transcription/glossary")).json()[
        "text"
    ] == "Invented Saved = invented variant\n"
    assert (target / "glossary.txt").stat().st_mode & 0o777 == 0o600


async def test_glossary_read_limits_and_unavailable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.transcribe.engine import Engine

    with pytest.raises(AppError):
        await GlossaryFile(Engine(None)).read()
    path = tmp_path / "invented.txt"
    monkeypatch.setenv("FAKE_TRANSCRIBE_GLOSSARY", str(path))
    file = GlossaryFile(Engine(FAKE))
    for data in (b"x" * 65537, b"bad\0term"):
        path.write_bytes(data)
        with pytest.raises(AppError):
            await file.read()
    path.write_bytes(b"")
    assert (await file.read()).terms == []
