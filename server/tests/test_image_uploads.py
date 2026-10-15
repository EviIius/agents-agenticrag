import asyncio
import struct
import sys
from pathlib import Path
from typing import Any

import httpx
import pytest
from fastapi import FastAPI

from app.errors import AppError
from app.images.uploads import ImageUploads, is_heif
from tests.test_chat import chat_app as chat_app

FIXTURES = Path(__file__).parent / "fixtures/images"


@pytest.mark.parametrize(
    ("filename", "mime"),
    [
        ("fake-renamed.png", "image/png"),
        ("fake-photo.heic", "image/heic"),
        ("fake-photo.HEIF", "application/octet-stream"),
    ],
)
async def test_heic_upload_is_actually_converted_and_temporary_source_removed(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI], filename: str, mime: str
) -> None:
    app, client, _ = chat_app
    response = await client.post(
        "/api/attachments",
        files={"file": (filename, (FIXTURES / "fake-synthetic.heic").read_bytes(), mime)},
    )
    assert response.status_code == 201
    item = response.json()
    assert item["kind"] == "image" and item["mime_type"] == "image/png"
    assert item["filename"] == Path(filename).with_suffix(".png").name
    content = (await client.get("/api/attachments/" + item["id"])).content
    assert content.startswith(b"\x89PNG\r\n\x1a\n") and not is_heif(content)
    assert struct.unpack(">II", content[16:24]) == (32, 16)
    assert not list((app.state.config.data_dir / "attachments").glob(".image-convert-*"))


async def test_regular_image_and_text_uploads_keep_original_bytes(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    _, client, _ = chat_app
    for filename, raw, mime in [
        ("fake.png", (FIXTURES / "fake-synthetic.png").read_bytes(), "image/png"),
        ("fake.txt", b"Synthetic plain text", "text/plain"),
    ]:
        response = await client.post("/api/attachments", files={"file": (filename, raw, mime)})
        assert response.status_code == 201
        assert (await client.get("/api/attachments/" + response.json()["id"])).content == raw


async def test_unreadable_heic_is_actionable_and_leaves_no_file(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, _ = chat_app
    for raw in [b"not an image", b"\0\0\0\x18ftypheic\0\0\0\0heicmif1broken"]:
        response = await client.post(
            "/api/attachments", files={"file": ("fake.heic", raw, "image/heic")}
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "image_unreadable"
        assert "JPEG or PNG" in response.json()["error"]["message"]
    assert not await app.state.store.rows("SELECT id FROM attachments")
    assert not list((app.state.config.data_dir / "attachments").glob(".image-convert-*"))


def test_heif_brand_detection_uses_file_bytes_not_filename() -> None:
    assert is_heif((FIXTURES / "fake-synthetic.heic").read_bytes())
    assert not is_heif((FIXTURES / "fake-synthetic.png").read_bytes())
    assert not is_heif(b"ftypheic")
    assert not is_heif(b"\0\0\0\x18ftypavif\0\0\0\0mif1avif")


@pytest.mark.parametrize("cancel", [False, True])
async def test_codec_timeout_and_cancellation_reap_owned_process(
    monkeypatch: pytest.MonkeyPatch, cancel: bool
) -> None:
    original = asyncio.create_subprocess_exec
    children: list[asyncio.subprocess.Process] = []

    async def spawn(*args: Any, **kwargs: Any) -> asyncio.subprocess.Process:
        child = await original(sys.executable, "-c", "import time; time.sleep(30)", **kwargs)
        children.append(child)
        return child

    monkeypatch.setattr(asyncio, "create_subprocess_exec", spawn)
    converter = ImageUploads(timeout=0.05 if not cancel else 30)
    task = asyncio.create_task(converter.command("unused"))
    if cancel:
        while not children:
            await asyncio.sleep(0.001)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    else:
        with pytest.raises(AppError, match="Couldn't open"):
            await task
    assert len(children) == 1 and children[0].returncode is not None
    assert not converter.processes


async def test_conversion_limits_and_recovery(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    converter = ImageUploads()
    with pytest.raises(AppError, match="20 MB"):
        await converter.convert(b"x" * (20 * 1024**2 + 1), tmp_path)

    async def properties(*args: str) -> bytes:
        return b"pixelWidth: 200000\npixelHeight: 200000\n"

    monkeypatch.setattr(converter, "command", properties)
    with pytest.raises(AppError, match="too large"):
        await converter.convert(b"fake", tmp_path)
    assert not list(tmp_path.glob(".image-convert-*"))
    stale = tmp_path / ".image-convert-fake"
    stale.mkdir()
    (stale / "source.heic").write_bytes(b"fake")
    complete = tmp_path / "fake-completed.png"
    complete.write_bytes(b"keep")
    converter.recover(tmp_path)
    assert not stale.exists() and complete.read_bytes() == b"keep"
