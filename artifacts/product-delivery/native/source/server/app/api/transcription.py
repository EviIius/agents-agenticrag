"""Local transcript lifecycle and content. Never include content in logs."""

import json
from collections.abc import AsyncIterator
from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, Request
from fastapi.responses import Response
from sse_starlette import EventSourceResponse

from ..db import attachments
from ..errors import AppError
from ..schemas import (
    Attachment,
    AudioStorage,
    CleanupRequest,
    Glossary,
    GlossaryRequest,
    TranscribeRequest,
    Transcript,
    TranscriptionEvent,
    TranscriptionStatus,
)
from ..transcribe.cleanup import Cleanups
from ..transcribe.glossary import GlossaryFile
from ..transcribe.jobs import Job, TranscriptionManager

router = APIRouter(prefix="/api")


@router.get("/transcription/status")
async def status(request: Request, refresh: bool = False) -> TranscriptionStatus:
    manager: TranscriptionManager = request.app.state.transcription
    return await manager.engine.status(refresh)


@router.get("/transcription/audio-storage")
async def audio_storage(request: Request) -> AudioStorage:
    manager: TranscriptionManager = request.app.state.transcription
    return await manager.audio_storage()


@router.delete("/transcription/audio-storage")
async def clear_audio(request: Request) -> AudioStorage:
    manager: TranscriptionManager = request.app.state.transcription
    return await manager.clear_audio()


@router.get("/_schema/transcription-event", response_model=TranscriptionEvent)
async def schema() -> TranscriptionEvent:
    return TranscriptionEvent.model_validate({"type": "stream.closed", "data": {}})


@router.get("/attachments/{identifier}/events")
async def events(identifier: str, request: Request) -> EventSourceResponse:
    manager: TranscriptionManager = request.app.state.transcription
    item = await attachments.attachment(manager.store, identifier)
    if item.kind != "audio":
        raise AppError("unsupported_type", "This attachment is not a recording.", 422)
    job = manager.jobs.get(identifier)
    try:
        after = int(request.headers.get("last-event-id", "0"))
    except ValueError:
        after = 0
    if job is None:
        job = Job(identifier)
        state = item.transcript.status if item.transcript else "failed"
        event = "done" if state == "ready" else "cancelled" if state == "cancelled" else "failed"
        if item.transcript and item.transcript.cleanup:
            event = (
                "cleanup.done" if item.transcript.cleanup.status == "ready" else "cleanup.failed"
            )
        else:
            event = "transcription." + event
        await job.emit(event, {"attachment": item.model_dump()})
        await job.emit("stream.closed", {})
        after = 0  # This new snapshot has its own sequence.

    async def stream() -> AsyncIterator[dict[str, str]]:
        async for seq, event in job.tail(after):
            yield {"id": str(seq), "event": event.type, "data": json.dumps(event.data)}

    return EventSourceResponse(
        stream(), ping=15, headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )


@router.get("/attachments/{identifier}/transcript")
async def transcript(identifier: str, request: Request) -> Transcript:
    return await attachments.transcript(request.app.state.store, identifier)


@router.post("/attachments/{identifier}/transcribe", status_code=202)
async def retry(identifier: str, body: TranscribeRequest, request: Request) -> Attachment:
    manager: TranscriptionManager = request.app.state.transcription
    return await manager.start(identifier, body.channels)


@router.post("/attachments/{identifier}/cancel", status_code=202)
async def cancel(identifier: str, request: Request) -> dict[str, bool]:
    await attachments.attachment(request.app.state.store, identifier)
    await request.app.state.transcription.cancel(identifier)
    return {"ok": True}


@router.post("/attachments/{identifier}/cleanup", status_code=202)
async def cleanup(identifier: str, body: CleanupRequest, request: Request) -> Attachment:
    manager: Cleanups = request.app.state.cleanup
    return await manager.start(identifier, body.connection_id, body.model_id)


@router.delete("/attachments/{identifier}/cleanup", status_code=204)
async def discard(identifier: str, request: Request) -> Response:
    await request.app.state.cleanup.discard(identifier)
    return Response(status_code=204)


@router.get("/transcription/glossary")
async def glossary(request: Request) -> Glossary:
    return await GlossaryFile(request.app.state.transcription.engine).read()


@router.put("/transcription/glossary")
async def save_glossary(body: GlossaryRequest, request: Request) -> Glossary:
    return await GlossaryFile(request.app.state.transcription.engine).write(body.text)


def stamp(value: float) -> str:
    millis = max(0, round(value * 1000))
    return (
        f"{millis // 3600000:02}:{millis // 60000 % 60:02}:"
        f"{millis // 1000 % 60:02},{millis % 1000:03}"
    )


@router.get("/attachments/{identifier}/transcript/download")
async def download(
    identifier: str, request: Request, format: str = "txt", variant: str = "best"
) -> Response:
    value = await attachments.transcript(request.app.state.store, identifier)
    if format not in ("txt", "srt", "json") or variant not in ("best", "original", "raw"):
        raise AppError(
            "validation_error", "Choose txt, srt or json and best, original or raw.", 422
        )
    text = value.raw_text if variant == "raw" else value.text
    if variant == "best" and value.cleaned_text is not None:
        text = value.cleaned_text
    if format == "srt":
        if variant == "best" and value.cleaned_text is not None:
            raise AppError(
                "validation_error", "Subtitles use the original timestamped transcript.", 422
            )
        text = (
            "\n\n".join(
                f"{i}\n{stamp(segment.start)} --> {stamp(segment.end)}\n"
                f"{segment.raw_text if variant == 'raw' else segment.text}"
                for i, segment in enumerate(value.segments, 1)
            )
            + "\n"
        )
    if format == "json":
        row = await request.app.state.store.one(
            "SELECT meta_json FROM transcripts WHERE attachment_id=?", (identifier,)
        )
        text = json.dumps(
            {
                **json.loads(row["meta_json"] or "{}"),
                "text": text,
                "raw_text": value.raw_text,
                "segments": [s.model_dump() for s in value.segments],
            },
            ensure_ascii=False,
            indent=2,
        )
    name = Path(value.attachment.filename).stem
    name = (
        "".join(c if c.isalnum() or c in " ._-" else "-" for c in name).strip(" .")[:120]
        or "Transcript"
    )
    filename = name + "." + format
    return Response(
        text,
        media_type={"txt": "text/plain", "srt": "application/x-subrip", "json": "application/json"}[
            format
        ],
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename, safe='')}"},
    )
