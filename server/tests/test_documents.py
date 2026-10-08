import asyncio
import json
import logging
import shutil
import sys
from pathlib import Path
from typing import Any
from zipfile import ZipFile

import aiosqlite
import httpx
import pytest
from fastapi import FastAPI
from pypdf import PdfWriter

from app.api import attachments as upload_api
from app.db.core import MIGRATIONS, migrate
from app.documents import extract as extraction
from app.documents.extract import ERRORS, extract
from app.documents.service import Extractor
from app.documents.worker import main as worker
from app.errors import AppError
from tests.test_chat import finish
from tests.test_phase4_guards import snapshot

FIXTURES = Path(__file__).parent / "fixtures/documents"


def test_pdf_pages_and_word_order() -> None:
    pdf = extract(FIXTURES / "two-pages.pdf", ".pdf")
    assert pdf.pages == 2 and pdf.chars == len(pdf.text)
    assert (
        pdf.text.index("[Page 1]") < pdf.text.index("silver orchard") < pdf.text.index("[Page 2]")
    )
    word = extract(FIXTURES / "table.docx", ".docx")
    assert word.pages is None and word.chars == len(word.text)
    assert (
        word.text == "Invented orchard ledger\nLantern\tMeadow\nViolet\tCopper\n"
        "Invented final paragraph.\tFin.\nEnd."
    )
    assert "Deleted" not in word.text and "header" not in word.text and "comment" not in word.text


@pytest.mark.parametrize(
    "fixture,code",
    [
        ("scanned.pdf", "document_no_text"),
        ("encrypted.pdf", "document_encrypted"),
        ("damaged.pdf", "document_unreadable"),
        ("table.docx", "document_unreadable"),
    ],
)
def test_invalid_documents(fixture: str, code: str) -> None:
    with pytest.raises(AppError) as caught:
        extract(FIXTURES / fixture, ".pdf")
    assert caught.value.code == code and caught.value.message == ERRORS[code]


async def test_upload_send_preserves_name_pages_table_and_only_text(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, runtime = chat_app
    items = []
    for name in ("two-pages.pdf", "table.docx"):
        response = await client.post(
            "/api/attachments", files={"file": (name, (FIXTURES / name).read_bytes())}
        )
        assert response.status_code == 201, response.text
        item = response.json()
        items.append(item)
        assert item["kind"] == "text" and item["document"]["source"] == Path(name).suffix[1:]
        content = (await client.get(f"/api/attachments/{item['id']}/text")).json()["text"]
        assert item["bytes"] == len(content.encode())
        assert item["document"]["chars"] == len(content)
        assert item["document"]["token_estimate"] == round(len(content) * 0.3)
        assert (await client.get(f"/api/attachments/{item['id']}/info")).json() == item
        download = await client.get(f"/api/attachments/{item['id']}")
        assert download.text == content and download.headers["content-type"].startswith(
            "text/plain"
        )
    paths = list((app.state.config.data_dir / "attachments").iterdir())
    assert len(paths) == 2 and all(
        p.suffix == ".txt" and p.stat().st_mode & 0o777 == 0o600 for p in paths
    )
    chat = (
        await client.post(
            "/api/chats", json={"connection_id": app.state.test_connection, "model_id": "fake-chat"}
        )
    ).json()
    sent = await client.post(
        f"/api/chats/{chat['id']}/messages",
        json={"content": "Invented document question", "attachment_ids": [a["id"] for a in items]},
    )
    assert sent.status_code == 202
    await finish(app, sent.json())
    captured = next(c for c in reversed(runtime.state.captures) if c.get("messages"))["messages"][
        -1
    ]["content"]
    assert (
        '<file name="two-pages.pdf">' in captured
        and "[Page 1]" in captured
        and "[Page 2]" in captured
    )
    assert '<file name="table.docx">' in captured and "Lantern\tMeadow" in captured
    detail = (await client.get(f"/api/chats/{chat['id']}")).json()
    assert detail["messages"][0]["attachments"][0]["document"] == items[0]["document"]


@pytest.mark.parametrize(
    "name,code",
    [
        ("scanned.pdf", "document_no_text"),
        ("encrypted.pdf", "document_encrypted"),
        ("damaged.pdf", "document_unreadable"),
    ],
)
async def test_failed_upload_leaves_no_file_or_row(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI], name: str, code: str
) -> None:
    app, client, _ = chat_app
    response = await client.post(
        "/api/attachments", files={"file": (name, (FIXTURES / name).read_bytes())}
    )
    assert response.status_code == 422 and response.json()["error"] == {
        "code": code,
        "message": ERRORS[code],
    }
    assert list((app.state.config.data_dir / "attachments").iterdir()) == []
    assert await app.state.store.rows("SELECT * FROM attachments") == []


async def test_upload_size_timeout_and_remove_cleanup(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI], monkeypatch: pytest.MonkeyPatch
) -> None:
    app, client, _ = chat_app
    monkeypatch.setattr(upload_api, "UPLOAD_LIMIT", 20)
    response = await client.post("/api/attachments", files={"file": ("two-pages.pdf", b"x" * 21)})
    assert response.status_code == 413 and response.json()["error"]["code"] == "document_too_large"
    monkeypatch.setattr(upload_api, "UPLOAD_LIMIT", 50 * 1024**2)
    app.state.documents.timeout = 0.001
    response = await client.post(
        "/api/attachments",
        files={"file": ("two-pages.pdf", (FIXTURES / "two-pages.pdf").read_bytes())},
    )
    assert response.json()["error"]["code"] == "document_timeout"
    assert list((app.state.config.data_dir / "attachments").iterdir()) == []
    assert not app.state.documents.processes
    app.state.documents.timeout = 30
    item = (
        await client.post(
            "/api/attachments",
            files={"file": ("two-pages.pdf", (FIXTURES / "two-pages.pdf").read_bytes())},
        )
    ).json()
    assert (await client.delete(f"/api/attachments/{item['id']}")).status_code == 204
    assert list((app.state.config.data_dir / "attachments").iterdir()) == []
    assert (await client.get(f"/api/attachments/{item['id']}/text")).status_code == 404
    text = (
        await client.post("/api/attachments", files={"file": ("invented.swift", b"invented text")})
    ).json()
    assert (await client.get(f"/api/attachments/{text['id']}/text")).status_code == 422


def test_extraction_limits(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(extraction, "UPLOAD_LIMIT", 10)
    with pytest.raises(AppError, match="50 MB"):
        extract(FIXTURES / "two-pages.pdf", ".pdf")
    monkeypatch.setattr(extraction, "UPLOAD_LIMIT", 50 * 1024**2)
    monkeypatch.setattr(extraction, "PAGE_LIMIT", 1)
    with pytest.raises(AppError, match="1,500 pages"):
        extract(FIXTURES / "two-pages.pdf", ".pdf")
    monkeypatch.setattr(extraction, "PAGE_LIMIT", 1500)
    monkeypatch.setattr(extraction, "TEXT_LIMIT", 10)
    for name in ("two-pages.pdf", "table.docx"):
        with pytest.raises(AppError, match="50 MB"):
            extract(FIXTURES / name, Path(name).suffix)
    monkeypatch.setattr(extraction, "TEXT_LIMIT", 2_000_000)
    for key, limit in [("XML_LIMIT", 1), ("EXPANDED_LIMIT", 1), ("ENTRY_LIMIT", 1)]:
        with monkeypatch.context() as patch:
            patch.setattr(extraction, key, limit)
            with pytest.raises(AppError, match="50 MB"):
                extract(FIXTURES / "table.docx", ".docx")
    with monkeypatch.context() as patch:
        patch.setattr(extraction, "XML_LIMIT", 1)
        with pytest.raises(AppError, match="50 MB"):
            extract(FIXTURES / "two-pages.pdf", ".pdf")
    with pytest.raises(AppError, match="damaged"):
        extract(tmp_path / "missing.docx", ".docx")
    with pytest.raises(AppError, match="damaged"):
        extract(FIXTURES / "table.docx", ".unsupported")


@pytest.mark.parametrize(
    "xml",
    [
        b'<!DOCTYPE x [<!ENTITY x "bad">]><x/>',
        b"<broken>",
        b"<x/>",
        b'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body/></w:document>',
    ],
)
def test_word_invalid_xml(tmp_path: Path, xml: bytes) -> None:
    target = tmp_path / "bad.docx"
    with ZipFile(target, "w") as archive:
        archive.writestr("word/document.xml", xml)
    with pytest.raises(AppError, match="damaged"):
        extract(target, ".docx")


def test_zero_page_pdf(tmp_path: Path) -> None:
    target = tmp_path / "empty.pdf"
    PdfWriter().write(target)
    with pytest.raises(AppError, match="selectable"):
        extract(target, ".pdf")


async def test_worker_protocol(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    output = tmp_path / "result"
    for name in ("two-pages.pdf", "damaged.pdf"):
        monkeypatch.setattr(sys, "argv", ["worker", str(FIXTURES / name), ".pdf", str(output)])
        logging_level = logging.root.manager.disable
        try:
            worker()
        finally:
            logging.disable(logging_level)
        result = json.loads(output.read_text())
        assert (
            "text" in result
            if name == "two-pages.pdf"
            else result["error"] == "document_unreadable"
        )
        assert output.stat().st_mode & 0o777 == 0o600
        output.unlink()


async def test_cancelled_workers_hold_capacity_until_exit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    actual = asyncio.create_subprocess_exec
    peak = 0
    processes = []

    async def slow(*args: Any, **kwargs: Any) -> asyncio.subprocess.Process:
        nonlocal peak
        process = await actual(sys.executable, "-c", "import time; time.sleep(60)", **kwargs)
        processes.append(process)
        peak = max(peak, sum(p.returncode is None for p in processes))
        return process

    monkeypatch.setattr(asyncio, "create_subprocess_exec", slow)
    service = Extractor(concurrency=1, timeout=10)
    tasks = [asyncio.create_task(service.extract(tmp_path / f"{i}.part", ".pdf")) for i in range(3)]
    while not service.processes:
        await asyncio.sleep(0.01)
    tasks[0].cancel()
    await asyncio.gather(tasks[0], return_exceptions=True)
    assert processes[0].returncode is not None
    while len(processes) < 2:
        await asyncio.sleep(0.01)
    # Shutdown kills a live worker; queued tasks can be cancelled without capacity leaks.
    tasks[2].cancel()
    await service.close()
    await asyncio.gather(*tasks, return_exceptions=True)
    assert peak == 1 and all(p.returncode is not None for p in processes)
    assert not service.processes and not list(tmp_path.iterdir())


async def test_cancelled_upload_cleans_source(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI], monkeypatch: pytest.MonkeyPatch
) -> None:
    app, client, _ = chat_app
    entered = asyncio.Event()

    async def cancelled(*args: Any) -> Any:
        entered.set()
        await asyncio.sleep(60)

    monkeypatch.setattr(app.state.documents, "extract", cancelled)
    task = asyncio.create_task(
        client.post(
            "/api/attachments",
            files={"file": ("two-pages.pdf", (FIXTURES / "two-pages.pdf").read_bytes())},
        )
    )
    await entered.wait()
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)
    assert list((app.state.config.data_dir / "attachments").iterdir()) == []
    assert await app.state.store.rows("SELECT * FROM attachments") == []


async def test_phase5a_rows_and_meta_nullable_survive_migration(tmp_path: Path) -> None:
    target = tmp_path / "phase5a.db"
    shutil.copyfile(Path(__file__).parent / "fixtures/db/phase3.db", target)
    async with aiosqlite.connect(target) as db:
        await db.executescript(
            (MIGRATIONS / "005_presets.sql").read_text() + "PRAGMA user_version=5;"
        )
        await db.execute(
            "INSERT INTO presets VALUES ('fake','Invented preset',NULL,'{}',0,"
            "'2026-10-05','2026-10-05')"
        )
        await db.commit()
    columns, before = snapshot(target)
    async with aiosqlite.connect(target) as db:
        await migrate(db)
        version = await (await db.execute("PRAGMA user_version")).fetchone()
        assert version and version[0] == 8
        assert all(
            row[0] is None
            for row in await (await db.execute("SELECT meta_json FROM attachments")).fetchall()
        )
    assert snapshot(target, columns)[1] == before


async def test_bootstrap_extensions_are_the_upload_list(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    _, client, _ = chat_app
    extensions = (await client.get("/api/bootstrap")).json()["attachment_extensions"]
    assert extensions == {"text": sorted(upload_api.TEXT), "document": sorted(upload_api.DOCUMENT)}
    for suffix in (
        ".jsx",
        ".xml",
        ".toml",
        ".ini",
        ".go",
        ".rs",
        ".java",
        ".c",
        ".cpp",
        ".h",
        ".rb",
        ".swift",
        ".kt",
        ".tex",
        ".srt",
        ".vtt",
    ):
        assert suffix in extensions["text"]
        assert (
            await client.post(
                "/api/attachments", files={"file": ("invented" + suffix, b"Invented file text")}
            )
        ).status_code == 201


def test_recovery_only_removes_interrupted_document_files(tmp_path: Path) -> None:
    for name in (
        "fake.pdf.part",
        "fake.docx.part",
        "fake.pdf.result",
        "fake.docx.result",
        "fake.txt.part",
        "kept.txt",
        "kept.wav",
        "kept.wav.part",
    ):
        (tmp_path / name).write_text("Invented")
    Extractor().recover(tmp_path)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["kept.txt", "kept.wav", "kept.wav.part"]


def test_word_table_retains_empty_edge_cells(tmp_path: Path) -> None:
    target = tmp_path / "invented.docx"
    xml = (
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body><w:tbl><w:tr><w:tc><w:p/></w:tc>"
        "<w:tc><w:p><w:r><w:t>Invented cell</w:t></w:r></w:p></w:tc>"
        "<w:tc><w:p/></w:tc></w:tr></w:tbl></w:body></w:document>"
    )
    with ZipFile(target, "w") as archive:
        archive.writestr("word/document.xml", xml)
    assert extract(target, ".docx").text == "\tInvented cell\t"
