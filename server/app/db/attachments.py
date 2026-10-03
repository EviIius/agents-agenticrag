"""One attachment projection, including transcript summaries without their content."""

import json
from typing import Any

from ..errors import AppError
from ..schemas import Attachment, CleanupInfo, Transcript, TranscriptInfo
from .core import Store


async def attachment(store: Store, identifier: str) -> Attachment:
    row = await store.one("SELECT * FROM attachments WHERE id=?", (identifier,))
    if not row:
        raise AppError("not_found", "Attachment not found.", 404)
    summary = None
    if row["kind"] == "audio":
        record = await store.one("SELECT * FROM transcripts WHERE attachment_id=?", (identifier,))
        if record:
            meta = json.loads(record["meta_json"] or "{}")
            text = record["cleaned_text"] if record["cleanup_status"] == "ready" else record["text"]
            processing = meta.get("processing", {})
            summary = TranscriptInfo(
                status=record["status"],
                channels=record["channels"],
                started_at=record["started_at"],
                error=json.loads(record["error_json"]) if record["error_json"] else None,
                duration_seconds=record["duration_seconds"],
                word_count=len(text.split()) if text is not None else None,
                token_estimate=round(len(text) * 0.3) if text is not None else None,
                elapsed_seconds=processing.get("elapsed_seconds"),
                speed_x_realtime=processing.get("speed_x_realtime"),
                engine_model=meta.get("engine", {}).get("model"),
                warnings=meta.get("warnings", []),
                correction_count=sum(
                    c.get("count", 0) for c in meta.get("glossary_corrections", [])
                ),
                cleanup=CleanupInfo(
                    **{
                        "status": record["cleanup_status"],
                        **json.loads(record["cleanup_json"] or "{}"),
                    }
                )
                if record["cleanup_status"]
                else None,
            )
    return Attachment(**row, transcript=summary)


async def transcript(store: Store, identifier: str) -> Transcript:
    item = await attachment(store, identifier)
    if not item.transcript or item.transcript.status != "ready":
        raise AppError("transcript_not_ready", "Waiting for the transcript", 409)
    row = await store.one("SELECT * FROM transcripts WHERE attachment_id=?", (identifier,))
    assert row is not None
    meta = json.loads(row["meta_json"] or "{}")
    return Transcript(
        attachment=item,
        text=row["text"] or "",
        raw_text=row["raw_text"] or "",
        cleaned_text=row["cleaned_text"],
        segments=json.loads(row["segments_json"] or "[]"),
        corrections=meta.get("glossary_corrections", []),
    )


async def best_text(store: Store, identifier: str) -> tuple[str, float]:
    value = await transcript(store, identifier)
    assert value.attachment.transcript is not None
    return (
        value.cleaned_text if value.cleaned_text is not None else value.text,
        value.attachment.transcript.duration_seconds or 0,
    )


def result_meta(result: dict[str, Any]) -> dict[str, Any]:
    return {
        key: result[key]
        for key in (
            "source",
            "engine",
            "processing",
            "warnings",
            "glossary_corrections",
            "channel_mode",
        )
        if key in result
    }
