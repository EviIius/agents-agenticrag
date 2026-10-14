"""Atomic chat image acceptance. Existing jobs remain the only execution state."""

import hashlib
import json

from fastapi import APIRouter, Request

from ..db import chats, messages
from ..db.connections import now, uid
from ..errors import AppError
from ..images.jobs import Images
from ..schemas import ChatImageCreate, ChatImageResponse, ChatImageRetry, ImageCreate, Message

router = APIRouter(prefix="/api/chats")


def title_from_prompt(prompt: str) -> str:
    text = " ".join(prompt.split())
    if len(text) <= 48:
        return text
    cut = text[:49].rsplit(" ", 1)[0]
    return cut[:48]


@router.post("/{identifier}/images", status_code=202)
async def create(identifier: str, body: ChatImageCreate, request: Request) -> ChatImageResponse:
    async with request.app.state.runs.chat_lock(identifier):
        return await accept(identifier, body, request)


async def accept(
    identifier: str, body: ChatImageCreate, request: Request, retry_id: str | None = None
) -> ChatImageResponse:
    store = request.app.state.store
    images: Images = request.app.state.images
    # Compare the explicit body, not a moving implicit current leaf.
    canonical = json.dumps({**body.model_dump(), "retry_id": retry_id}, sort_keys=True)
    async with images.lock:
        old = await store.one(
            "SELECT * FROM chat_image_requests WHERE request_key=?", (body.request_key,)
        )
        if old:
            if old["chat_id"] != identifier or old["input_json"] != canonical:
                raise AppError(
                    "request_conflict", "This request key belongs to different image inputs.", 409
                )
            return ChatImageResponse(
                user=await messages.message(store, old["user_id"]) if not retry_id else None,
                assistant=await messages.message(store, old["assistant_id"]),
            )
        chat = await chats.chat(store, identifier)
        if any(run.chat_id == identifier for run in await request.app.state.runs.active()):
            raise AppError("run_active", "This chat is still generating.", 409)
        parent = body.parent_id if "parent_id" in body.model_fields_set else chat.current_leaf_id
        if parent:
            row = await store.one(
                "SELECT id FROM messages WHERE id=? AND chat_id=?", (parent, identifier)
            )
            if not row:
                raise AppError("validation_error", "Parent belongs to another chat.", 422)
        user_id, assistant_id = (retry_id or uid()), uid()
        date = now()
        specs = [
            ImageCreate(
                request_key="chat-"
                + hashlib.sha256(f"{body.request_key}-{i}".encode()).hexdigest(),
                prompt=body.prompt,
                seed=seed,
                parent_id=body.source_job_id,
            )
            for i, seed in enumerate(body.seeds)
        ]
        prepared = await images.prepare(specs)
        statements: list[tuple[str, tuple[object, ...]]] = []
        if not retry_id:
            statements.append(
                (
                    "INSERT INTO messages(id,chat_id,parent_id,role,content,kind,"
                    "created_at,updated_at) "
                    "VALUES(?,?,?,'user',?,'image',?,?)",
                    (user_id, identifier, parent, body.prompt, date, date),
                )
            )
        statements += [
            (
                "INSERT INTO messages(id,chat_id,parent_id,role,content,kind,params_json,"
                "created_at,updated_at) "
                "VALUES(?,?,?,'assistant','','image',?,?,?)",
                (
                    assistant_id,
                    identifier,
                    user_id,
                    json.dumps(
                        {
                            "engine": images.engine.status().model,
                            "count": body.count,
                            "seeds": body.seeds,
                            "source_job_id": body.source_job_id,
                        }
                    ),
                    now(),
                    date,
                ),
            ),
            (
                "INSERT INTO chat_image_requests VALUES(?,?,?,?,?)",
                (body.request_key, identifier, user_id, assistant_id, canonical),
            ),
        ]
        for position, (job_id, rows) in enumerate(prepared):
            statements.extend(rows)
            statements.extend(
                [
                    ("INSERT INTO message_images VALUES(?,?,?)", (assistant_id, position, job_id)),
                    ("INSERT INTO chat_image_origins VALUES(?,?)", (job_id, body.request_key)),
                ]
            )
        statements += [
            (
                "UPDATE chats SET current_leaf_id=?,title=CASE WHEN title_source='fallback' AND "
                "NOT EXISTS(SELECT 1 FROM messages WHERE chat_id=? AND id NOT IN (?,?)) "
                "THEN ? ELSE title END,updated_at=? WHERE id=?",
                (
                    assistant_id,
                    identifier,
                    user_id,
                    assistant_id,
                    title_from_prompt(body.prompt),
                    date,
                    identifier,
                ),
            ),
            ("DELETE FROM chat_search WHERE chat_id=?", (identifier,)),
            (
                "INSERT INTO chat_search(chat_id,message_id,title,content) SELECT chat_id,id,"
                "(SELECT title FROM chats WHERE id=chat_id),content FROM messages WHERE chat_id=?",
                (identifier,),
            ),
        ]
        try:
            await store.batch(statements)
        except BaseException:
            images.discard(prepared)
            raise
        # Never expose/schedule a partially accepted turn.
        for job_id, _ in prepared:
            images.schedule(job_id)
            await images.emit(job_id)
        return ChatImageResponse(
            user=await messages.message(store, user_id) if not retry_id else None,
            assistant=await messages.message(store, assistant_id),
        )


@router.post("/{identifier}/messages/{message_id}/images/retry", status_code=202)
async def retry(
    identifier: str, message_id: str, body: ChatImageRetry, request: Request
) -> ChatImageResponse:
    async with request.app.state.runs.chat_lock(identifier):
        old = await image_message(identifier, message_id, request)
        if len(body.seeds) != len(old.images or []):
            raise AppError("validation_error", "Provide one seed for each image.", 422)
        user = await messages.message(request.app.state.store, old.parent_id or "")
        params = await request.app.state.store.one(
            "SELECT params_json FROM messages WHERE id=?", (message_id,)
        )
        source = json.loads(params["params_json"])["source_job_id"] if params else None
        return await accept(
            identifier,
            ChatImageCreate(
                request_key=body.request_key,
                prompt=user.content,
                count=len(body.seeds),
                seeds=body.seeds,
                parent_id=user.parent_id,
                source_job_id=source,
            ),
            request,
            retry_id=user.id,
        )


async def image_message(identifier: str, message_id: str, request: Request) -> Message:
    msg = await messages.message(request.app.state.store, message_id)
    if msg.chat_id != identifier or msg.kind != "image" or msg.role != "assistant":
        raise AppError("not_found", "Image turn not found.", 404)
    return msg


@router.post("/{identifier}/messages/{message_id}/images/cancel")
async def cancel(identifier: str, message_id: str, request: Request) -> ChatImageResponse:
    async with request.app.state.runs.chat_lock(identifier):
        msg = await image_message(identifier, message_id, request)
        for job in msg.images or []:
            await request.app.state.images.cancel(job.id)
        return ChatImageResponse(
            assistant=await messages.message(request.app.state.store, message_id)
        )
