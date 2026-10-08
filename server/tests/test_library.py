import asyncio
import json
import shutil
from pathlib import Path
from typing import Any, cast

import httpx
import pytest
from fastapi import FastAPI

from app.errors import AppError
from app.library import ingest
from app.library.extract import extract, passages
from app.library.ingest import Library
from app.library.worker import extract as read_file
from tests.test_chat import finish, start

FIXTURES = Path(__file__).parent / "fixtures/documents"


async def select(app: FastAPI, client: httpx.AsyncClient, model: str = "fake-embedding") -> None:
    response = await client.post(
        "/api/library/embedding",
        json={
            "embedding": {
                "connection_id": app.state.test_connection,
                "model_id": model,
            }
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["embedding"]["dim"] == (16 if model.endswith("alt") else 8)


async def terminal(library: Library, identifier: str, status: str = "ready") -> dict[str, Any]:
    async with asyncio.timeout(10):
        async with library.changed:
            while True:
                row = await library.store.one(
                    "SELECT * FROM library_documents WHERE id=?", (identifier,)
                )
                if row and row["status"] in ("ready", "failed"):
                    assert row["status"] == status, row.get("error_json")
                    return row
                await library.changed.wait()


async def upload(
    client: httpx.AsyncClient,
    name: str = "Invented ledger.md",
    data: bytes = b"Invented lanterns are blue.",
) -> str:
    response = await client.post("/api/library/documents", files={"file": (name, data)})
    assert response.status_code == 201, response.text
    return str(response.json()["id"])


@pytest.mark.parametrize(
    "filename", ["two-pages.pdf", "table.docx", "Invented.md", "Invented.txt", "Invented.html"]
)
async def test_library_formats_pages_private_original_and_atomic_index(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
    filename: str,
) -> None:
    app, client, _ = chat_app
    await select(app, client)
    body = (
        (FIXTURES / filename).read_bytes()
        if (FIXTURES / filename).is_file()
        else (
            b"<html><body><p>Invented lanterns are blue and the orchard ledger "
            b"is violet.</p></body></html>"
        )
    )
    identifier = await upload(client, filename, body)
    row = await terminal(app.state.library, identifier)
    store = app.state.store
    chunks = await store.rows(
        "SELECT * FROM library_chunks WHERE document_id=? ORDER BY ord", (identifier,)
    )
    vectors = await store.rows("SELECT chunk_id FROM library_vectors")
    assert row["chunk_count"] == len(chunks) == len(vectors) > 0
    assert await store.rows(
        "SELECT rowid FROM library_chunks_fts WHERE library_chunks_fts MATCH 'lantern OR orchard'"
    )
    assert all("[Page " not in c["text"] for c in chunks)
    if filename.endswith("pdf"):
        assert {c["page_start"] for c in chunks} == {1, 2}
        assert all(c["page_start"] == c["page_end"] for c in chunks)
    else:
        assert all(c["page_start"] is None for c in chunks)
    response = await client.get(f"/api/library/documents/{identifier}/file")
    assert response.content == body
    assert response.headers["cache-control"] == "private, no-store"
    assert response.headers["content-disposition"].startswith(
        "inline" if filename.endswith("pdf") else "attachment"
    )
    assert "sandbox" in response.headers["content-security-policy"]
    assert (app.state.library.folder / Path(row["path"]).name).stat().st_mode & 0o777 == 0o600
    public = (await client.get("/api/library")).json()
    assert "path" not in public["documents"][0] and "sha256" not in public["documents"][0]
    opened = await client.get(f"/api/library/documents/{identifier}/text")
    assert (
        opened.json()["text"]
        == read_file(app.state.library.folder / Path(row["path"]).name, Path(filename).suffix).text
    )
    assert opened.headers["cache-control"] == "private, no-store"
    assert "extracted_text" not in public["documents"][0]
    assert (await client.get("/api/bootstrap")).json()["features"]["library"]


async def test_library_queue_duplicate_collection_delete_preserves_citation(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, _ = chat_app
    identifier = await upload(client)
    assert (await client.get("/api/library")).json()["counts"] == {"queued": 1}
    duplicate = await client.post(
        "/api/library/documents",
        files={"file": ("Different synthetic name.md", b"Invented lanterns are blue.")},
    )
    assert duplicate.status_code == 409 and duplicate.json()["error"]["document_id"] == identifier
    assert len(list(app.state.library.folder.iterdir())) == 1
    collection = (
        await client.post("/api/library/collections", json={"name": "Invented collection"})
    ).json()
    assert (
        await client.post("/api/library/collections", json={"name": "invented COLLECTION"})
    ).status_code == 409
    assert (
        await client.patch(
            f"/api/library/documents/{identifier}", json={"collection_id": collection["id"]}
        )
    ).status_code == 204
    assert (
        await client.patch(
            f"/api/library/collections/{collection['id']}", json={"name": "Invented renamed"}
        )
    ).status_code == 200
    assert (await client.delete(f"/api/library/collections/{collection['id']}")).status_code == 204
    await select(app, client)
    row = await terminal(app.state.library, identifier)
    assert row["collection_id"] is None
    run = await finish(app, await start(client, "Synthetic citation owner", "fake-chat"))
    await app.state.store.execute(
        "INSERT INTO message_library_sources(message_id,n,document_id,filename,passages_json) "
        "VALUES (?,1,?,'Invented ledger.md',?)",
        (run.message.id, identifier, '[{"text":"Invented saved passage"}]'),
    )
    assert (await client.delete(f"/api/library/documents/{identifier}")).status_code == 204
    assert not list(app.state.library.folder.iterdir())
    for table in ("library_documents", "library_chunks", "library_vectors"):
        assert not await app.state.store.rows("SELECT * FROM " + table)
    assert not await app.state.store.rows(
        "SELECT rowid FROM library_chunks_fts WHERE library_chunks_fts MATCH 'lanterns'"
    )
    source = await app.state.store.one("SELECT * FROM message_library_sources")
    assert (
        source["document_id"] is None
        and json.loads(source["passages_json"])[0]["text"] == "Invented saved passage"
    )
    assert (await client.get(f"/api/chats/{run.message.chat_id}")).status_code == 200


async def test_library_model_change_prefix_and_reindex_never_extracts_again(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app, client, runtime = chat_app
    await select(app, client)
    identifier = await upload(client)
    before = await terminal(app.state.library, identifier)

    async def forbidden(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("Reindex must use durable passages")

    monkeypatch.setattr(ingest, "extract", forbidden)
    await select(app, client, "fake-embedding-alt")
    assert (await client.get("/api/library")).json()["counts"] == {"stale": 1}
    assert not await app.state.store.rows("SELECT chunk_id FROM library_vectors")
    assert (
        await client.patch("/api/settings", json={"library.document_prefix": "Invented prefix: "})
    ).status_code == 200
    await client.post("/api/library/reindex")
    after = await terminal(app.state.library, identifier)
    assert after["chunk_count"] == before["chunk_count"]
    assert after["embedding_model"].endswith("fake-embedding-alt")
    captures = [c for c in runtime.state.captures if c.get("input")]
    assert captures[-1]["input"][0].startswith("Invented prefix: ")
    assert (await client.post(f"/api/library/documents/{identifier}/reindex")).status_code == 204
    await terminal(app.state.library, identifier)
    assert (
        await client.request("DELETE", "/api/library", json={"confirmation": "no"})
    ).status_code == 422
    assert (
        await client.request("DELETE", "/api/library", json={"confirmation": "DELETE"})
    ).status_code == 204
    assert not (await client.get("/api/library")).json()["documents"]
    assert (
        await client.post("/api/library/embedding", json={"embedding": None})
    ).status_code == 200


async def test_library_restart_mid_embedding_and_chat_capacity(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app, client, _ = chat_app
    await select(app, client)
    original = app.state.library.embed
    reached = asyncio.Event()
    release = asyncio.Event()
    count = 0

    async def paused(choice: dict[str, Any], texts: list[str], local_only: bool) -> list[bytes]:
        nonlocal count
        result = await original(choice, texts, local_only)
        count += 1
        if count == 1:
            reached.set()
            await release.wait()  # Runtime capacity was released before this next batch.
        return cast(list[bytes], result)

    monkeypatch.setattr(app.state.library, "embed", paused)
    body = "\n\n".join(
        f"# Invented section {i}\n" + "Invented ledger values are violet. " * 70 for i in range(40)
    ).encode()
    identifier = await upload(client, data=body)
    await asyncio.wait_for(reached.wait(), 10)
    run = await finish(app, await start(client, "Synthetic chat during indexing", "fake-chat"))
    assert run.message.status == "complete"
    assert await app.state.store.one("SELECT id FROM library_documents WHERE status='embedding'")
    assert not await app.state.store.rows("SELECT * FROM library_chunks")
    await app.state.library.close()
    other = Library(app.state.store, app.state.runs, app.state.config.data_dir)
    app.state.library = other
    await other.start()
    complete = await terminal(other, identifier)
    expected = passages(identifier, read_file(other.folder / (identifier + ".md"), ".md"))
    assert complete["chunk_count"] == len(expected) > 32
    assert len(await app.state.store.rows("SELECT * FROM library_vectors")) == len(expected)
    assert count == 1


@pytest.mark.parametrize(
    "fixture,code",
    [
        ("scanned.pdf", "document_no_text"),
        ("encrypted.pdf", "document_encrypted"),
        ("damaged.pdf", "document_unreadable"),
    ],
)
async def test_library_failed_pdf_safe_error_retry(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
    fixture: str,
    code: str,
) -> None:
    app, client, _ = chat_app
    await select(app, client)
    identifier = await upload(client, fixture, (FIXTURES / fixture).read_bytes())
    row = await terminal(app.state.library, identifier, "failed")
    assert json.loads(row["error_json"])["code"] == code
    assert fixture not in row["error_json"]
    await client.post(f"/api/library/documents/{identifier}/reindex")
    await terminal(app.state.library, identifier, "failed")


async def test_library_privacy_validation_model_metadata_and_missing_routes(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, _ = chat_app
    assert (
        await client.post(
            "/api/library/embedding",
            json={
                "embedding": {"connection_id": app.state.test_connection, "model_id": "fake-chat"}
            },
        )
    ).status_code == 422
    remote = (
        await client.post("/api/connections", json={"base_url": "http://example.org:11434"})
    ).json()
    assert (
        await client.post(
            "/api/library/embedding",
            json={"embedding": {"connection_id": remote["id"], "model_id": "fake-embedding"}},
        )
    ).json()["error"]["code"] == "library_requires_local"
    await client.patch("/api/settings", json={"library.requires_local": False})
    assert (
        await client.post(
            "/api/library/embedding",
            json={"embedding": {"connection_id": remote["id"], "model_id": "fake-embedding"}},
        )
    ).status_code == 200
    await client.patch("/api/settings", json={"library.requires_local": True})
    identifier = await upload(client)
    await terminal(app.state.library, identifier, "failed")
    invalid_settings: list[dict[str, Any]] = [
        {"library.embedding": {}},
        {"library.max_sources": 2},
        {"library.query_prefix": "x" * 1001},
    ]
    for body in invalid_settings:
        assert (await client.patch("/api/settings", json=body)).status_code == 422
    assert (
        await client.post("/api/library/documents", files={"file": ("Invented.exe", b"x")})
    ).status_code == 422
    for path, method in (
        ("/documents/missing", "DELETE"),
        ("/documents/missing/reindex", "POST"),
        ("/documents/missing/text", "GET"),
        ("/documents/missing/file", "GET"),
        ("/collections/missing", "DELETE"),
    ):
        assert (await client.request(method, "/api/library" + path)).status_code == 404
    assert (
        await client.patch("/api/library/documents/missing", json={"collection_id": None})
    ).status_code == 404
    assert (
        await client.patch("/api/library/collections/missing", json={"name": "Invented"})
    ).status_code == 404
    assert (await client.post("/api/library/collections", json={"name": "  "})).status_code == 422


async def test_library_events_resume_and_gap(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, _ = chat_app
    library = app.state.library
    await library.emit("document.queued", {"id": "fake"})
    first = (await library.snapshot())["event_id"]
    await library.emit("document.ready", {"id": "fake"})
    stream = library.events(first)
    event = await anext(stream)
    assert event["event"] == "document.ready" and int(event["id"]) > first
    await stream.aclose()
    await library.store.execute(
        "INSERT INTO library_events(id,kind,data_json) VALUES (?, 'document.ready','{}')",
        (first + 10,),
    )
    stream = library.events(first + 1)
    assert (await anext(stream))["event"] == "library.changed"
    assert (await anext(stream))["event"] == "document.ready"
    await stream.aclose()
    assert (
        await client.get("/api/library/events", headers={"Last-Event-ID": "bad"})
    ).status_code == 422


async def test_library_extraction_cancel_timeout_and_private_errors(tmp_path: Path) -> None:
    source = tmp_path / "Invented.txt"
    source.write_bytes(b"\xff\xfe")
    with pytest.raises(AppError):
        read_file(source, ".txt")
    source.write_text("Invented ledger")
    with pytest.raises(AppError) as caught:
        await extract(source, timeout=0.00001)
    assert caught.value.code == "document_timeout"
    assert not list(tmp_path.glob("*.result"))
    task = asyncio.create_task(extract(source))
    await asyncio.sleep(0.001)
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)
    assert not list(tmp_path.glob("*.result"))
    shutil.copyfile(FIXTURES / "table.docx", tmp_path / "Invented.docx")
    assert (await extract(tmp_path / "Invented.docx")).text


@pytest.mark.parametrize(
    "vectors", [[], [[0.0] * 8], [[float("nan")] * 8], [[1.0] * 7], [[1e40] * 8]]
)
async def test_library_rejects_invalid_vectors_atomically(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
    monkeypatch: pytest.MonkeyPatch,
    vectors: list[list[float]],
) -> None:
    app, client, _ = chat_app
    await select(app, client)
    adapter = await app.state.registry.adapter(app.state.test_connection)

    async def invalid(model_id: str, texts: list[str]) -> list[list[float]]:
        return vectors

    monkeypatch.setattr(adapter, "embed", invalid)
    identifier = await upload(client)
    await terminal(app.state.library, identifier, "failed")
    assert not await app.state.store.rows("SELECT * FROM library_chunks")
    assert not await app.state.store.rows("SELECT * FROM library_vectors")


async def test_library_guards_limits_active_and_collection_validation(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.api import library as api

    app, client, _ = chat_app
    monkeypatch.setattr(api, "LIMIT", 1)
    assert (
        await client.post("/api/library/documents", files={"file": ("Invented.md", b"xx")})
    ).status_code == 413
    monkeypatch.setattr(api, "LIMIT", 100 * 1024**2)
    assert (
        await client.post(
            "/api/library/documents",
            data={"collection_id": "missing"},
            files={"file": ("Invented.md", b"xx")},
        )
    ).status_code == 404
    identifier = await upload(client)
    assert (await client.post(f"/api/library/documents/{identifier}/reindex")).status_code == 409
    assert (
        await client.patch(
            f"/api/library/documents/{identifier}", json={"collection_id": "missing"}
        )
    ).status_code == 404
    assert (await client.get(f"/api/library/documents/{identifier}/text")).json()["text"] == ""
    (app.state.library.folder / (identifier + ".md")).unlink()
    assert (await client.get(f"/api/library/documents/{identifier}/file")).status_code == 404
    app.state.library.available = False
    assert (
        await client.post("/api/library/embedding", json={"embedding": None})
    ).status_code == 503
    assert (
        await client.post("/api/library/documents", files={"file": ("Invented.md", b"x")})
    ).status_code == 503
    assert (await client.get("/api/health")).status_code == 200
    assert not (await client.get("/api/bootstrap")).json()["features"]["library"]
    with pytest.raises(AppError):
        await app.state.library.vector_table(0)


async def test_library_settings_validate_before_interrupt_and_extension_disabled(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, _ = chat_app
    await select(app, client)
    await select(app, client)  # Selecting the same identity/dimension leaves the index intact.
    assert (
        await client.patch(
            "/api/settings",
            json={"library.query_prefix": "Invented query: ", "library.max_sources": 4},
        )
    ).status_code == 200
    values = (await client.get("/api/library")).json()
    assert values["query_prefix"] == "Invented query: "
    # Security: extension loading was turned off after loading the known pinned module.
    with pytest.raises(Exception, match="not authorized"):
        await app.state.store.db.load_extension("invented-untrusted-module")
    stream = app.state.library.events(values["event_id"])
    waiting = asyncio.create_task(anext(stream))
    await asyncio.sleep(0)
    await app.state.library.emit("library.changed", {})
    assert (await asyncio.wait_for(waiting, 1))["event"] == "library.changed"
    await stream.aclose()


def test_library_worker_bounded_utf8_and_private_protocol(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.library import worker
    from app.library.worker import main

    source = tmp_path / "Invented.txt"
    output = tmp_path / "Invented.result"
    source.write_text("Invented private test content")
    monkeypatch.setattr("sys.argv", ["worker", str(source), ".txt", str(output)])
    main()
    assert json.loads(output.read_text())["text"] == "Invented private test content"
    output.unlink()
    source.write_bytes(b"\xff")
    main()
    assert json.loads(output.read_text())["error"] == "document_unreadable"
    monkeypatch.setattr(worker, "TEXT_LIMIT", 2)
    source.write_bytes(b"0123456789")
    with pytest.raises(AppError) as caught:
        read_file(source, ".txt")
    assert caught.value.code == "document_too_large"
    source.write_text("xxx")
    with pytest.raises(AppError) as caught:
        read_file(source, ".txt")
    assert caught.value.code == "document_too_large"
    source.write_text(" ")
    with pytest.raises(AppError) as caught:
        read_file(source, ".txt")
    assert caught.value.code == "document_unreadable"
