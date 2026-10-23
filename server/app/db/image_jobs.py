"""Read durable image state without constructing or scheduling a worker."""

import json
from datetime import datetime

from ..errors import AppError
from ..schemas import ImageJob, ImageOrigin
from .core import Store


async def image_job(store: Store, identifier: str) -> ImageJob:
    row = await store.one(
        "SELECT j.*,a.sha256,a.bytes,a.metadata_bytes,r.chat_id,r.assistant_id,"
        "c.title,t.started_at,t.finished_at FROM image_jobs j "
        "LEFT JOIN image_artifacts a ON a.job_id=j.id "
        "LEFT JOIN image_steps t ON t.job_id=j.id "
        "LEFT JOIN chat_image_origins o ON o.job_id=j.id "
        "LEFT JOIN chat_image_requests r ON r.request_key=o.request_key "
        "LEFT JOIN chats c ON c.id=r.chat_id WHERE j.id=?",
        (identifier,),
    )
    if not row:
        raise AppError("not_found", "Image job not found.", 404)
    spec = json.loads(row["input_json"])
    reference_row = await store.one(
        "SELECT r.*,p.export_bytes FROM image_job_references p JOIN "
        "image_references r ON r.id=p.reference_id WHERE p.job_id=?",
        (identifier,),
    )
    from ..images.references import projection

    return ImageJob(
        **{
            key: row[key]
            for key in (
                "id",
                "parent_id",
                "state",
                "stage",
                "completed_steps",
                "error",
                "created_at",
                "updated_at",
                "sha256",
            )
        },
        prompt=spec["prompt"],
        seed=spec["seed"],
        mode=spec.get("mode", "generate"),
        reference=projection(reference_row) if reference_row else None,
        export_bytes=reference_row["export_bytes"] if reference_row else 0,
        selection=spec.get("selection"),
        width=spec["reference"]["dimensions"][0] if spec.get("selection") else 1024,
        height=spec["reference"]["dimensions"][1] if spec.get("selection") else 1024,
        image_bytes=row["bytes"] or 0,
        metadata_bytes=row["metadata_bytes"] or 0,
        elapsed_seconds=max(
            0,
            (
                datetime.fromisoformat(row["finished_at"])
                - datetime.fromisoformat(row["started_at"])
            ).total_seconds(),
        )
        if row["started_at"] and row["finished_at"]
        else None,
        origin=ImageOrigin(
            chat_id=row["chat_id"],
            message_id=row["assistant_id"],
            title=row["title"],
            deleted=row["title"] is None,
        )
        if row["chat_id"]
        else None,
    )
