import base64
import json
import re
import sqlite3
from contextlib import AsyncExitStack
from urllib.parse import quote

from fastapi import APIRouter, Request
from fastapi.responses import Response

from ..db import attachments as records
from ..db import chats, messages, presets, settings
from ..db.connections import now, uid
from ..db.legacy import import_legacy
from ..errors import AppError
from ..runs.context import assemble, path
from ..schemas import (
    Chat,
    ChatCreate,
    ChatDetail,
    ChatList,
    ChatPatch,
    ContextInfo,
    DeleteChats,
    LegacyImport,
    LegacyStatus,
    RunResponse,
    Send,
)

router = APIRouter(prefix="/api/chats")


@router.get("/legacy-import")
async def legacy_status(request: Request) -> LegacyStatus:
    return LegacyStatus(available=request.app.state.config.legacy_db.expanduser().is_file())


@router.post("/legacy-import")
async def legacy_import(request: Request) -> LegacyImport:
    source = request.app.state.config.legacy_db
    if not source.expanduser().is_file():
        raise AppError(
            "legacy_unavailable", "No Chat & Web 0.5 database was found on this Mac.", 404
        )
    try:
        imported, skipped = await import_legacy(request.app.state.store, source)
    except (OSError, sqlite3.Error, ValueError):
        raise AppError(
            "legacy_import_failed", "Couldn't import the old chats. Existing chats were kept.", 422
        ) from None
    return LegacyImport(imported=imported, skipped=skipped)


@router.get("/export")
async def export_all(request: Request) -> Response:
    rows = await request.app.state.store.rows("SELECT id FROM chats ORDER BY created_at,id")
    exported = [(await detail(str(row["id"]), request)).model_dump(mode="json") for row in rows]
    return Response(
        json.dumps({"format": "workbench-chats", "version": 1, "chats": exported}, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": 'attachment; filename="workbench-chats.json"'},
    )


@router.delete("", status_code=204)
async def delete_all(body: DeleteChats, request: Request) -> None:
    store = request.app.state.store
    # Cancel and await generators before deleting their message rows.
    for run in list(request.app.state.runs.runs.values()):
        if not run.closed:
            await request.app.state.runs.cancel(run.id)
    await request.app.state.transcription.cancel_chat()
    files = await store.rows("SELECT path FROM attachments WHERE message_id IS NOT NULL")
    await store.batch([("DELETE FROM chat_search", ()), ("DELETE FROM chats", ())])
    request.app.state.runs.runs.clear()
    request.app.state.runs.chat_locks.clear()
    directory = request.app.state.config.data_dir.expanduser().resolve()
    for row in files:
        attachment = (directory / str(row["path"])).resolve()
        if attachment.is_relative_to(directory / "attachments"):
            attachment.unlink(missing_ok=True)


@router.get("")
async def listing(request: Request, q: str = "", cursor: str | None = None) -> ChatList:
    store = request.app.state.store
    params: list[object] = []
    sql = "SELECT * FROM chats WHERE EXISTS (SELECT 1 FROM messages WHERE chat_id=chats.id)"
    if q.strip():
        terms = re.findall(r"\w+", q)
        if terms:
            sql += " AND id IN (SELECT chat_id FROM chat_search WHERE chat_search MATCH ?)"
            params.append(" AND ".join('"' + term + '"' for term in terms))
    if cursor:
        try:
            position = json.loads(base64.urlsafe_b64decode(cursor))
            assert len(position) == 3
        except (ValueError, AssertionError):
            raise AppError("validation_error", "Invalid history cursor.", 422) from None
        sql += " AND (pinned,updated_at,id)<(?,?,?)"
        params.extend(position)
    sql += " ORDER BY pinned DESC,updated_at DESC,id DESC LIMIT 51"
    rows = await store.rows(sql, tuple(params))
    items = [await chats.chat(store, str(r["id"])) for r in rows[:50]]
    if q:
        for item in items:
            row = await store.one(
                "SELECT content FROM messages WHERE chat_id=? AND content LIKE ? LIMIT 1",
                (item.id, "%" + q + "%"),
            )
            item.snippet = str(row["content"])[:160] if row else None
    next_cursor = None
    if len(rows) > 50:
        r = rows[49]
        next_cursor = base64.urlsafe_b64encode(
            json.dumps([r["pinned"], r["updated_at"], r["id"]]).encode()
        ).decode()
    return ChatList(items=items, next_cursor=next_cursor)


@router.post("", status_code=201)
async def create(body: ChatCreate, request: Request) -> Chat:
    values = await settings.get(request.app.state.store)
    if not body.model_id:
        model = next(iter(await request.app.state.registry.models()), None)
        if model:
            body.connection_id = model.connection_id
            body.model_id = model.model_id
    if body.web_enabled is None:
        body.web_enabled = values["web.default_on"]
    identifier = (
        body.preset_id if "preset_id" in body.model_fields_set else values["default_preset_id"]
    )
    preset = await presets.get(request.app.state.store, identifier) if identifier else None
    return await chats.create(request.app.state.store, body, preset)


@router.get("/{identifier}")
async def detail(identifier: str, request: Request) -> ChatDetail:
    store = request.app.state.store
    return ChatDetail(
        chat=await chats.chat(store, identifier),
        messages=await messages.list_messages(store, identifier),
        sources=await messages.sources(store, identifier),
        reads=await messages.reads(store, identifier),
    )


@router.patch("/{identifier}")
async def patch(identifier: str, body: ChatPatch, request: Request) -> Chat:
    if body.model_id:
        current = await chats.chat(request.app.state.store, identifier)
        await request.app.state.registry.resolve(
            body.connection_id or current.connection_id, body.model_id
        )
    return await chats.patch(request.app.state.store, identifier, body)


@router.delete("/{identifier}", status_code=204)
async def delete(identifier: str, request: Request) -> None:
    store = request.app.state.store
    await chats.chat(store, identifier)
    for run in list(request.app.state.runs.runs.values()):
        if run.message.chat_id == identifier and not run.closed:
            await request.app.state.runs.cancel(run.id)
    await request.app.state.transcription.cancel_chat(identifier)
    files = await store.rows(
        "SELECT path FROM attachments WHERE message_id IN "
        "(SELECT id FROM messages WHERE chat_id=?)",
        (identifier,),
    )
    await store.batch(
        [
            ("DELETE FROM chat_search WHERE chat_id=?", (identifier,)),
            ("DELETE FROM chats WHERE id=?", (identifier,)),
        ]
    )
    for run in list(request.app.state.runs.runs.values()):
        if run.message.chat_id == identifier:
            request.app.state.runs.runs.pop(run.id, None)
    directory = request.app.state.config.data_dir.expanduser().resolve()
    for row in files:
        attachment = (directory / str(row["path"])).resolve()
        if attachment.is_relative_to(directory / "attachments"):
            attachment.unlink(missing_ok=True)


@router.get("/{identifier}/export")
async def export(identifier: str, request: Request, format: str = "md") -> Response:
    data = await detail(identifier, request)
    branch = path(data.messages, data.chat.current_leaf_id)
    if format == "json":
        text = data.model_copy(update={"messages": branch}).model_dump_json(indent=2)
        mime = "application/json"
    elif format == "md":
        text = (
            "# "
            + data.chat.title
            + "\n\n"
            + "\n\n".join("## " + m.role.title() + "\n\n" + m.content for m in branch)
        )
        mime = "text/markdown"
    else:
        raise AppError("validation_error", "Export format must be md or json.", 422)
    title = re.sub(r'[\x00-\x1f\x7f/\\:*?"<>|]', "-", data.chat.title).strip(" .")[:120]
    title = title or "Untitled chat"
    filename = f"{title}.{format}"
    fallback = filename.encode("ascii", "replace").decode().replace("?", "-")
    return Response(
        text,
        media_type=mime,
        headers={
            "Content-Disposition": (
                f"attachment; filename=\"{fallback}\"; filename*=UTF-8''{quote(filename, safe='')}"
            )
        },
    )


@router.get("/{identifier}/context")
async def context(identifier: str, request: Request, leaf: str | None = None) -> ContextInfo:
    data = await detail(identifier, request)
    model = await request.app.state.registry.resolve(data.chat.connection_id, data.chat.model_id)
    params = await request.app.state.registry.params(model, data.chat.params)
    assembled = await assemble(
        request.app.state.store,
        request.app.state.config.data_dir,
        data.chat,
        data.messages,
        leaf or data.chat.current_leaf_id,
        model,
        params,
        await settings.get(request.app.state.store),
    )
    return ContextInfo(
        used_tokens=assembled.used_tokens,
        context_length=model.context_length or 8192,
        dropped_message_count=assembled.dropped,
    )


@router.post("/{identifier}/messages", status_code=202)
async def send(identifier: str, body: Send, request: Request) -> RunResponse:
    async with request.app.state.runs.chat_lock(identifier), AsyncExitStack() as stack:
        for attachment_id in sorted(set(body.attachment_ids)):
            await stack.enter_async_context(request.app.state.transcription.lock(attachment_id))
        return await start_message(identifier, body, request)


async def start_message(identifier: str, body: Send, request: Request) -> RunResponse:
    store = request.app.state.store
    data = await detail(identifier, request)
    if any(r.chat_id == identifier for r in await request.app.state.runs.active()):
        raise AppError("run_active", "This chat is still generating.", 409)
    model = await request.app.state.registry.resolve(data.chat.connection_id, data.chat.model_id)
    parent = next((m for m in data.messages if m.id == body.parent_id), None)
    if body.parent_id and not parent:
        raise AppError("validation_error", "Parent belongs to another chat.", 422)
    if len(set(body.attachment_ids)) != len(body.attachment_ids):
        raise AppError("validation_error", "Duplicate attachment.", 422)
    attachments = []
    for attachment_id in body.attachment_ids:
        a = await store.one("SELECT * FROM attachments WHERE id=?", (attachment_id,))
        if not a or a["message_id"]:
            raise AppError("validation_error", "Attachment is missing or already sent.", 422)
        attachments.append(a)
    if sum(a["kind"] == "image" for a in attachments) > 4:
        raise AppError("validation_error", "At most four images per message.", 422)
    from ..schemas import Message

    user_id, assistant_id, date = uid(), uid(), now()
    assistant_date = now()
    user = Message(
        id=user_id,
        chat_id=identifier,
        parent_id=body.parent_id,
        role="user",
        content=body.content,
        status="complete",
        created_at=date,
        attachments=[await records.attachment(store, str(a["id"])) for a in attachments],
    )
    if any(
        a.kind == "audio" and (not a.transcript or a.transcript.status != "ready")
        for a in user.attachments
    ):
        raise AppError("transcript_not_ready", "Waiting for the transcript", 422)
    params = await request.app.state.registry.params(model, data.chat.params)
    assembled = await assemble(
        store,
        request.app.state.config.data_dir,
        data.chat,
        [*data.messages, user],
        user_id,
        model,
        params,
        await settings.get(store),
    )
    # Attachment content is assembled from unclaimed files before the transaction below.
    statements: list[tuple[str, tuple[object, ...]]] = [
        (
            "INSERT INTO messages(id,chat_id,parent_id,role,content,created_at,update"
            "d_at) VALUES (?,?,?,'user',?,?,?)",
            (user_id, identifier, body.parent_id, body.content, date, date),
        ),
        (
            "INSERT INTO messages(id,chat_id,parent_id,role,status,connection_id,mode"
            "l_id,params_json,created_at,updated_at) VALUES (?,?,?,'assistant','strea"
            "ming',?,?,?,?,?)",
            (
                assistant_id,
                identifier,
                user_id,
                model.connection_id,
                model.model_id,
                json.dumps(params),
                assistant_date,
                assistant_date,
            ),
        ),
        (
            "UPDATE chats SET current_leaf_id=?,title=CASE WHEN NOT EXISTS(SELECT 1 F"
            "ROM messages WHERE chat_id=? AND role='user' AND id!=?) THEN ? ELSE titl"
            "e END,updated_at=? WHERE id=?",
            (assistant_id, identifier, user_id, body.content[:60], date, identifier),
        ),
        (
            "INSERT INTO chat_search(chat_id,message_id,title,content) SELECT chat_id"
            ",id,(SELECT title FROM chats WHERE id=chat_id),content FROM messages WHE"
            "RE id=?",
            (user_id,),
        ),
    ]
    for a in attachments:
        statements.append(("UPDATE attachments SET message_id=? WHERE id=?", (user_id, a["id"])))
    if body.web is not None:
        statements.append(("UPDATE chats SET web_enabled=? WHERE id=?", (body.web, identifier)))
    await store.batch(statements)
    assistant = await messages.message(store, assistant_id)
    run = request.app.state.runs.start(assistant, model, assembled, params)
    return RunResponse(run_id=run.id, user_message=user, assistant_message=assistant)
