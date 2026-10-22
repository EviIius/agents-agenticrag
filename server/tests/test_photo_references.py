"""PE1-A synthetic storage/API tests. No Pillow/native runtime needed here."""

import asyncio
import hashlib
import json
import shutil
import sqlite3
import struct
import zlib
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import aiosqlite
import httpx
import pytest
from fastapi import FastAPI

from app.backup import Backups
from app.db.core import MIGRATIONS, migrate
from app.images.backup import restore
from app.images.engine import EDIT_DIGEST, Engine
from app.images.files import atomic_json, sanitize_export, validate
from app.images.reference_files import BROWSER_RECIPE, RECIPE, digest
from app.schemas import ImageStatus
from tests.test_chat import chat_app as chat_app
from tests.test_chat_images import inputs, new
from tests.test_images import FakeEngine, png
from tests.test_phase4_guards import snapshot


class EditFake(FakeEngine):
    def status(self) -> ImageStatus:
        return ImageStatus(available=True, editing_available=True)

    async def run_edit(self, manifest: Path, scratch: Path, progress: Any) -> int:
        return await self.run(manifest, scratch, progress)


class FakeCodec:
    async def normalize(self, folder: Path) -> dict[str, Any]:
        original = (folder / "original").read_bytes()
        working = png()
        (folder / "reference.png").write_bytes(working)
        (folder / "reference.png").chmod(0o600)
        meta: dict[str, Any] = {
            "original_sha256": hashlib.sha256(original).hexdigest(),
            "original_bytes": len(original),
            "original_format": "PNG",
            "original_dimensions": [1024, 1024],
            "exif_orientation": 1,
            "sha256": hashlib.sha256(working).hexdigest(),
            "bytes": len(working),
            "dimensions": [1024, 1024],
            "normalization": RECIPE,
        }
        if (folder / "decoded.json").exists():
            props = json.loads((folder / "decoded.json").read_text())
            meta.update(
                original_format="HEIF",
                exif_orientation=None,
                original_dimensions=props["dimensions"],
            )
            if props.get("source") == "browser":
                meta["normalization"] = BROWSER_RECIPE
                if original.startswith(b"\x89PNG\r\n\x1a\n"):
                    meta["original_format"] = "PNG"
                elif original.startswith(b"\xff\xd8\xff"):
                    meta["original_format"] = "JPEG"
        atomic_json(folder / "reference.json", meta)
        return meta

    async def close(self) -> None:
        pass


async def setup(app: FastAPI, client: httpx.AsyncClient) -> tuple[str, dict[str, Any]]:
    app.state.images.engine = EditFake()
    app.state.images.references.codec = FakeCodec()
    cid = await new(client)
    result = await client.post(
        f"/api/chats/{cid}/image-references", files={"file": ("synthetic.png", png(), "image/png")}
    )
    assert result.status_code == 201, result.text
    return cid, result.json()


async def edit(
    client: httpx.AsyncClient, cid: str, reference: dict[str, Any], **changes: Any
) -> httpx.Response:
    return await client.post(
        f"/api/chats/{cid}/images", json=inputs(1, reference_id=reference["id"], **changes)
    )


async def test_owned_upload_dedup_preview_and_private_original(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, _ = chat_app
    cid, reference = await setup(app, client)
    again = await client.post(
        f"/api/chats/{cid}/image-references", files={"file": ("different-name.jpg", png())}
    )
    assert again.json()["id"] == reference["id"]
    other = await new(client)
    copied = await client.post(
        f"/api/chats/{other}/image-references", files={"file": ("synthetic.png", png())}
    )
    assert copied.json()["id"] != reference["id"]
    assert (
        await client.get(f"/api/chats/{other}/image-references/{reference['id']}")
    ).status_code == 404
    assert (await edit(client, other, reference)).status_code == 404
    preview = await client.get(f"/api/chats/{cid}/image-references/{reference['id']}/preview")
    assert preview.content == png() and preview.headers["cache-control"] == "no-store"
    folder = app.state.images.references.path(reference["id"])
    assert (folder / "original").read_bytes() == png()
    assert all(
        (folder / name).stat().st_mode & 0o777 == 0o600
        for name in ("original", "reference.png", "reference.json")
    )
    assert (
        await client.post(
            "/api/images/jobs",
            json={
                "request_key": uuid4().hex,
                "prompt": "Synthetic generic image",
                "seed": 42,
                "reference_id": reference["id"],
            },
        )
    ).status_code == 422
    bad = await client.post(
        f"/api/chats/{cid}/image-references", files={"file": ("synthetic.png", b"not an image")}
    )
    assert bad.status_code == 422


async def test_edit_acceptance_retry_pins_and_original_integrity(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, runtime = chat_app
    cid, ref = await setup(app, client)
    body = inputs(1, reference_id=ref["id"])
    url = f"/api/chats/{cid}/images"
    first = await client.post(url, json=body)
    assert first.status_code == 202, first.text
    result = first.json()
    assert (await client.post(url, json=body)).json()["assistant"]["id"] == result["assistant"][
        "id"
    ]
    item = result["assistant"]["images"][0]
    assert item["mode"] == "edit" and item["reference"]["id"] == ref["id"]
    folder = app.state.images.path(item["id"])
    manifest = json.loads((folder / "input.json").read_text())
    assert manifest["mode"] == "edit" and "reference" in manifest
    original = app.state.images.references.path(ref["id"]) / "original"
    assert original.stat().st_ino == (folder / "inputs/original").stat().st_ino
    assert (
        await client.post("/api/images/references/clear", json={"confirm": True})
    ).status_code == 409
    app.state.images.engine.release.set()
    await asyncio.gather(*list(app.state.images.tasks.values()))
    job = await app.state.images.get(item["id"])
    assert job.state == "complete" and job.export_bytes > 0
    assert (await client.get(f"/api/images/jobs/{job.id}/output/png")).content == png()
    assert digest(original) == hashlib.sha256(png()).hexdigest()
    retry = await client.post(
        f"/api/chats/{cid}/messages/{result['assistant']['id']}/images/retry",
        json={"request_key": uuid4().hex, "seeds": [56]},
    )
    assert retry.status_code == 202, retry.text
    await asyncio.gather(*list(app.state.images.tasks.values()))
    second = retry.json()["assistant"]["images"][0]
    assert second["reference"]["id"] == ref["id"]
    assert (await app.state.images.storage()).references == 1
    assert not [capture for capture in runtime.state.captures if capture.get("messages")]


async def test_queued_edit_preserves_sampling_budget_until_capacity(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI], monkeypatch: pytest.MonkeyPatch
) -> None:
    app, client, _ = chat_app
    cid, ref = await setup(app, client)
    images = app.state.images
    queued, release, sampling = asyncio.Event(), asyncio.Event(), asyncio.Event()

    @asynccontextmanager
    async def lease(*, background: bool = False) -> AsyncIterator[None]:
        assert background
        queued.set()
        await release.wait()
        yield

    async def sample(meter: Any) -> None:
        sampling.set()
        await asyncio.Event().wait()

    monkeypatch.setattr(images.capacity, "lease", lease)
    monkeypatch.setattr(type(images.references), "sample", staticmethod(sample))
    response = await edit(client, cid, ref)
    assert response.status_code == 202
    await asyncio.wait_for(queued.wait(), 1)
    assert not sampling.is_set()
    images.engine.release.set()
    release.set()
    await asyncio.gather(*list(images.tasks.values()))
    assert sampling.is_set()
    job = response.json()["assistant"]["images"][0]
    assert (await images.get(job["id"])).state == "complete"
    report = json.loads((images.path(job["id"]) / "storage.json").read_text())
    assert len(report["samples"]) >= 3


async def test_atomic_acceptance_rollback_retains_unclaimed_reference(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI], monkeypatch: pytest.MonkeyPatch
) -> None:
    app, client, _ = chat_app
    cid, ref = await setup(app, client)
    batch = app.state.store.batch

    async def fail(rows: Any) -> None:
        if any("INSERT INTO chat_image_requests" in sql for sql, _ in rows):
            rows = [*rows, ("INSERT INTO message_images VALUES('missing',0,'missing')", ())]
        await batch(rows)

    monkeypatch.setattr(app.state.store, "batch", fail)
    with pytest.raises(Exception, match="FOREIGN KEY"):
        await edit(client, cid, ref)
    assert not await app.state.store.rows("SELECT * FROM image_job_references")
    assert not await app.state.store.rows("SELECT * FROM image_jobs")
    assert not list(app.state.images.folder.iterdir())
    assert (await app.state.images.references.get(ref["id"], cid)).id == ref["id"]


async def test_tampered_reference_stops_before_scheduling(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, _ = chat_app
    cid, ref = await setup(app, client)
    (app.state.images.references.path(ref["id"]) / "reference.png").write_bytes(b"changed")
    response = await edit(client, cid, ref)
    assert response.status_code == 409
    assert not app.state.images.tasks and not await app.state.store.rows("SELECT * FROM image_jobs")


async def test_clear_keeps_outputs_and_refuses_retry_until_reattached(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, _ = chat_app
    cid, ref = await setup(app, client)
    app.state.images.engine.release.set()
    accepted = (await edit(client, cid, ref)).json()
    await asyncio.gather(*list(app.state.images.tasks.values()))
    job = accepted["assistant"]["images"][0]
    before = await app.state.images.get(job["id"])
    assert (
        await client.post("/api/images/references/clear", json={"confirm": True})
    ).status_code == 200
    assert (await client.get(f"/api/images/jobs/{job['id']}/output/png")).status_code == 200
    detail = (await client.get(f"/api/images/jobs/{job['id']}")).json()
    assert detail["reference"]["available"] is False
    assert detail["updated_at"] > before.updated_at
    assert (await app.state.images.storage()).reference_bytes == 0
    response = await client.post(
        f"/api/chats/{cid}/messages/{accepted['assistant']['id']}/images/retry",
        json={"request_key": uuid4().hex, "seeds": [2]},
    )
    assert response.status_code == 409
    reattached = await client.post(
        f"/api/chats/{cid}/image-references", files={"file": ("synthetic.png", png())}
    )
    assert reattached.status_code == 201 and reattached.json()["id"] == ref["id"]
    latest = (await client.get(f"/api/images/jobs/{job['id']}")).json()
    assert latest["reference"]["available"] and latest["updated_at"] > detail["updated_at"]
    event = await app.state.store.one("SELECT data_json FROM image_events ORDER BY id DESC LIMIT 1")
    assert event and json.loads(event["data_json"])["job"]["reference"]["available"] is True


async def test_generated_output_is_explicit_new_owned_reference(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, _ = chat_app
    cid, ref = await setup(app, client)
    app.state.images.engine.release.set()
    response = await client.post(f"/api/chats/{cid}/images", json=inputs(1))
    await asyncio.gather(*list(app.state.images.tasks.values()))
    job = response.json()["assistant"]["images"][0]
    assert job["mode"] == "generate" and job["reference"] is None
    canonical = await app.state.store.one(
        "SELECT input_json FROM chat_image_requests ORDER BY rowid DESC LIMIT 1"
    )
    assert canonical and "reference_id" not in json.loads(canonical["input_json"])
    other = await new(client)
    copied = await client.post(
        f"/api/chats/{other}/image-references/from-job", json={"source_job_id": job["id"]}
    )
    assert copied.status_code == 201 and copied.json()["chat_id"] == other
    assert copied.json()["id"] != ref["id"]


async def test_backup_pending_inputs_restore_and_missing_blob_rollback(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI], tmp_path: Path
) -> None:
    app, client, _ = chat_app
    cid, ref = await setup(app, client)
    images = app.state.images
    images.engine.fail = True
    images.engine.release.set()
    failed = (await edit(client, cid, ref)).json()["assistant"]["images"][0]
    await asyncio.gather(*list(images.tasks.values()))
    assert (await images.get(failed["id"])).state == "failed"
    images.engine.fail = False
    images.engine.release.clear()
    async with images.capacity.lease():
        cancelled = (await edit(client, cid, ref)).json()["assistant"]["images"][0]
        await images.cancel(cancelled["id"])
        queued = (await edit(client, cid, ref)).json()["assistant"]["images"][0]
        backups = Backups(
            images.store,
            images.data,
            clock=lambda: datetime(2026, 10, 19, tzinfo=UTC),
            images=images,
        )
        status = await backups.make()
        assert status.warning is None
        database = next(backups.folder.glob("auto-20261019-0000-*.db"))
        manifest = json.loads((database.parent / "images" / (database.stem + ".json")).read_text())
        assert manifest["version"] == 2 and len(manifest["references"]) == 1
        assert not manifest["images"]
        assert len(manifest["reference_jobs"]) == 3
        target = tmp_path / "restored"
        assert restore(database, target) == 0
        assert (target / "image-references" / ref["id"] / "original").read_bytes() == png()
        assert (target / "images" / queued["id"] / "inputs/original").is_file()
        with sqlite3.connect(target / "workbench.db") as db:
            assert sorted(row[0] for row in db.execute("SELECT state FROM image_jobs")) == [
                "cancelled",
                "failed",
                "queued",
            ]
        key = manifest["references"][0]["files"]["original"]
        blob = database.parent / "images/blobs" / key
        blob.unlink()
        with pytest.raises((OSError, ValueError)):
            restore(database, tmp_path / "broken")
        assert not (tmp_path / "broken").exists()
        await images.cancel(queued["id"])


async def test_migration_preserves_all_populated_v13_columns(tmp_path: Path) -> None:
    target = tmp_path / "synthetic-v13.db"
    shutil.copyfile(Path(__file__).parent / "fixtures/db/phase3.db", target)
    with sqlite3.connect(target) as db:
        for path in sorted(MIGRATIONS.glob("*.sql")):
            version = int(path.name.split("_")[0])
            if 4 < version <= 13:
                db.executescript(path.read_text() + f"\nPRAGMA user_version={version};")
        db.execute(
            "INSERT INTO image_jobs VALUES(?,?,NULL,?,'cancelled','Cancelled',0,NULL,?,?)",
            (
                "a" * 32,
                "synthetic-legacy-key",
                json.dumps({"prompt": "Synthetic prior image", "seed": 42}),
                "2026-10-18",
                "2026-10-18",
            ),
        )
        db.execute("INSERT INTO image_steps(job_id) VALUES(?)", ("a" * 32,))
        db.commit()
    columns, before = snapshot(target)
    async with aiosqlite.connect(target) as db:
        await db.execute("PRAGMA foreign_keys=ON")
        await migrate(db)
        await migrate(db)
        assert await (await db.execute("PRAGMA user_version")).fetchone() == (14,)
        assert not await (await db.execute("PRAGMA foreign_key_check")).fetchall()
        assert await (await db.execute("PRAGMA integrity_check")).fetchone() == ("ok",)
    assert snapshot(target, columns)[1] == before


async def test_heif_raw_original_survives_copy_conversion(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI], monkeypatch: pytest.MonkeyPatch
) -> None:
    app, client, _ = chat_app
    cid, _ = await setup(app, client)
    raw = b"\x00\x00\x00\x18ftypheic\x00\x00\x00\x00heicmif1"

    async def convert(
        data: bytes, folder: Path, *, properties: dict[str, int] | None = None
    ) -> bytes:
        assert data == raw
        assert properties is not None
        properties.update(width=3024, height=4032)
        return png()

    monkeypatch.setattr(app.state.images.references.uploads, "convert", convert)
    result = await client.post(
        f"/api/chats/{cid}/image-references", files={"file": ("synthetic.png", raw)}
    )
    assert result.status_code == 201, result.text
    ref = result.json()
    assert ref["original_format"] == "HEIF"
    folder = app.state.images.references.path(ref["id"])
    assert (folder / "original").read_bytes() == raw
    assert (folder / "reference.png").read_bytes() == png()
    assert not (folder / "decoded.png").exists()


async def test_upload_is_bounded_before_multipart_consumes_large_body(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    _, client, _ = chat_app
    cid = await new(client)
    result = await client.post(
        f"/api/chats/{cid}/image-references",
        content=b"",
        headers={"content-length": str(41 * 1024**2)},
    )
    assert result.status_code == 413


async def test_chunked_edit_upload_stops_at_body_limit(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, _ = chat_app
    cid = await new(client)
    yielded = 0

    async def chunks() -> AsyncIterator[bytes]:
        nonlocal yielded
        yield (
            b"--fake-boundary\r\nContent-Disposition: form-data; "
            b'name="file"; filename="synthetic.png"\r\nContent-Type: image/png\r\n\r\n'
        )
        for _ in range(42):
            yielded += 1
            yield b"x" * 1024**2
        yield b"\r\n--fake-boundary--\r\n"

    result = await client.post(
        f"/api/chats/{cid}/image-references",
        content=chunks(),
        headers={"content-type": "multipart/form-data; boundary=fake-boundary"},
    )
    assert result.status_code == 413, result.text
    assert yielded < 42
    assert not await app.state.store.rows("SELECT * FROM image_references")


async def test_browser_conversion_retains_original_and_edit_binding(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI], monkeypatch: pytest.MonkeyPatch
) -> None:
    app, client, _ = chat_app
    cid, _ = await setup(app, client)
    raw = b"\x00\x00\x00\x18ftypheic\x00\x00\x00\x00heicmif1"

    async def unavailable(*args: Any, **kwargs: Any) -> bytes:
        raise AssertionError("Browser conversion must not run the failed HEIC decoder again")

    monkeypatch.setattr(app.state.images.references.uploads, "convert", unavailable)
    response = await client.post(
        f"/api/chats/{cid}/image-references",
        files={"file": ("photo", raw), "browser_preview": ("preview.png", png(), "image/png")},
        data={"original_width": "4032", "original_height": "3024"},
    )
    assert response.status_code == 201, response.text
    reference = response.json()
    folder = app.state.images.references.path(reference["id"])
    assert (folder / "original").read_bytes() == raw
    receipt = json.loads((folder / "reference.json").read_text())
    assert receipt["normalization"] == BROWSER_RECIPE
    assert receipt["original_dimensions"] == [4032, 3024]
    assert receipt["exif_orientation"] is None
    assert not (folder / "decoded.png").exists()
    app.state.images.engine.release.set()
    accepted = await edit(client, cid, reference)
    assert accepted.status_code == 202
    await asyncio.gather(*list(app.state.images.tasks.values()))
    job = accepted.json()["assistant"]["images"][0]
    assert job["mode"] == "edit" and job["reference"]["id"] == reference["id"]
    assert (app.state.images.path(job["id"]) / "inputs/original").read_bytes() == raw


@pytest.mark.parametrize(
    ("preview", "dimensions"),
    [
        (b"not a PNG", {"original_width": "100", "original_height": "200"}),
        (png(), {}),
        (png(), {"original_width": "100"}),
        (png(), {"original_width": "0", "original_height": "200"}),
        (png(), {"original_width": "100001", "original_height": "100001"}),
    ],
)
async def test_browser_conversion_rejects_invalid_input_without_saving(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
    preview: bytes,
    dimensions: dict[str, str],
) -> None:
    app, client, _ = chat_app
    cid = await new(client)
    result = await client.post(
        f"/api/chats/{cid}/image-references",
        files={"file": ("photo", png()), "browser_preview": ("preview.png", preview)},
        data=dimensions,
    )
    assert result.status_code == 422
    assert not await app.state.store.rows("SELECT * FROM image_references")
    assert not list(app.state.images.references.folder.iterdir())


async def test_original_file_limit_stays_20mb_with_browser_preview(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    _, client, _ = chat_app
    cid = await new(client)
    result = await client.post(
        f"/api/chats/{cid}/image-references",
        files={
            "file": ("photo", b"x" * (20 * 1024**2 + 1)),
            "browser_preview": ("preview.png", png()),
        },
        data={"original_width": "100", "original_height": "200"},
    )
    assert result.status_code == 413


async def test_removing_ordinary_upload_does_not_unpin_admitted_edit(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, _ = chat_app
    cid, ref = await setup(app, client)
    upload = (
        await client.post("/api/attachments", files={"file": ("synthetic.png", png())})
    ).json()
    accepted = (await edit(client, cid, ref)).json()
    assert (await client.delete(f"/api/attachments/{upload['id']}")).status_code == 204
    assert (await app.state.images.references.get(ref["id"])).id == ref["id"]
    app.state.images.engine.release.set()
    await asyncio.gather(*list(app.state.images.tasks.values()))
    job = accepted["assistant"]["images"][0]
    assert (await app.state.images.get(job["id"])).state == "complete"


async def test_recovery_keeps_pinned_failed_inputs_and_damaged_original(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, _ = chat_app
    cid, ref = await setup(app, client)
    images = app.state.images
    images.engine.fail = True
    images.engine.release.set()
    result = (await edit(client, cid, ref)).json()
    await asyncio.gather(*list(images.tasks.values()))
    job = result["assistant"]["images"][0]
    assert (await images.get(job["id"])).state == "failed"
    await images.store.execute("UPDATE image_references SET created_at='2026-01-01T00:00:00+00:00'")
    await images.recover()
    folder = images.references.path(ref["id"])
    assert (await images.references.get(ref["id"])).id == ref["id"]
    (folder / "reference.png").unlink()
    await images.recover()
    await images.recover()
    assert (folder / "original").read_bytes() == png()
    assert (await images.storage()).reference_bytes >= len(png())
    assert (
        await client.post("/api/images/references/clear", json={"confirm": True})
    ).status_code == 200
    assert not folder.exists()


async def test_photo_backup_failure_preserves_prior_valid_pair(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI], tmp_path: Path
) -> None:
    app, client, _ = chat_app
    cid, ref = await setup(app, client)
    images = app.state.images
    images.engine.release.set()
    await edit(client, cid, ref)
    await asyncio.gather(*list(images.tasks.values()))
    backups = Backups(
        images.store, images.data, clock=lambda: datetime(2026, 10, 19, tzinfo=UTC), images=images
    )
    assert (await backups.make()).warning is None
    paired = next(backups.folder.glob("auto-20261019-0000-*.db"))
    before = paired.read_bytes()
    (images.references.path(ref["id"]) / "reference.png").write_bytes(b"damaged")
    assert (await backups.make()).warning is not None
    assert list(backups.folder.glob("auto-20261019-0000-*.db")) == [paired]
    assert paired.read_bytes() == before
    assert restore(paired, tmp_path / "previous-valid-restore") == 1


def test_exports_strip_metadata_without_changing_encoded_pixels(tmp_path: Path) -> None:
    from tests.test_images import output

    expected = {"prompt": "Synthetic export", "seed": 42}
    output(tmp_path, expected)
    base = (tmp_path / "image.png").read_bytes()
    text = b"Comment\x00synthetic EXIF-like note"
    chunk = (
        struct.pack(">I", len(text))
        + b"tEXt"
        + text
        + struct.pack(">I", zlib.crc32(b"tEXt" + text))
    )
    raw = base[:-12] + chunk + base[-12:]
    (tmp_path / "image.png").write_bytes(raw)
    meta = json.loads((tmp_path / "metadata.json").read_text())
    meta["sha256"] = hashlib.sha256(raw).hexdigest()
    (tmp_path / "metadata.json").write_text(json.dumps(meta))
    validate(tmp_path, expected)
    export_hash, size = sanitize_export(tmp_path)
    assert (tmp_path / "export.png").read_bytes() == base
    assert size == len(base) and export_hash == hashlib.sha256(base).hexdigest()
    assert (tmp_path / "image.png").read_bytes() == raw


@pytest.mark.parametrize(
    "models",
    [
        [{"digest": EDIT_DIGEST, "context_length": 65536, "size_vram": 100}],
        [{"digest": "other", "context_length": 32768, "size_vram": 100}],
    ],
)
async def test_edit_admission_refuses_unmeasured_residency(
    models: list[dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = Engine(None)

    async def loaded() -> list[dict[str, Any]]:
        return models

    monkeypatch.setattr(engine, "loaded", loaded)
    with pytest.raises(Exception, match="tested 32K"):
        await engine.admit_edit()


@pytest.mark.parametrize(
    "models", [[], [{"digest": EDIT_DIGEST, "context_length": 32768, "size_vram": 100}]]
)
async def test_edit_admission_allows_only_native_qualified_arrangements(
    models: list[dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = Engine(None)

    async def loaded() -> list[dict[str, Any]]:
        return models

    monkeypatch.setattr(engine, "loaded", loaded)
    await engine.admit_edit()


@pytest.mark.parametrize(
    "models",
    [
        [{"digest": EDIT_DIGEST, "context_length": 32768, "size_vram": True}],
        [{"digest": EDIT_DIGEST, "context_length": 32768, "size_vram": 21827095101}],
        [{"digest": EDIT_DIGEST, "context_length": 32768, "size_vram": 100}] * 2,
    ],
)
def test_edit_admission_keeps_strict_resident_memory_and_identity_bounds(
    models: list[dict[str, Any]],
) -> None:
    assert not Engine.qualified_edit(models)
