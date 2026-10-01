import json
from urllib.parse import urlsplit

from ..errors import AppError
from ..schemas import (
    Attachment,
    ErrorDetail,
    Message,
    MessageModel,
    Source,
    Stats,
    WebInfo,
    WebRead,
)
from .core import Store


async def message(store: Store, identifier: str) -> Message:
    row = await store.one("SELECT * FROM messages WHERE id=?", (identifier,))
    if not row:
        raise AppError("not_found", "Message not found.", 404)
    attachments = [
        Attachment(**r)
        for r in await store.rows("SELECT * FROM attachments WHERE message_id=?", (identifier,))
    ]
    model = None
    if row["connection_id"] and row["model_id"]:
        pref = await store.one(
            "SELECT display_name FROM model_prefs WHERE connection_id=? AND model_id=?",
            (row["connection_id"], row["model_id"]),
        )
        model = MessageModel(
            connection_id=str(row["connection_id"]),
            model_id=str(row["model_id"]),
            display_name=str(
                pref["display_name"] if pref and pref["display_name"] else row["model_id"]
            ),
        )
    return Message(
        **{
            **row,
            "model": model,
            "attachments": attachments,
            "error": ErrorDetail(**json.loads(str(row["error_json"])))
            if row["error_json"]
            else None,
            "stats": Stats(**json.loads(str(row["stats_json"]))) if row["stats_json"] else None,
            "web": WebInfo(**json.loads(str(row["web_json"]))) if row["web_json"] else None,
        }
    )


async def list_messages(store: Store, chat_id: str) -> list[Message]:
    return [
        await message(store, str(r["id"]))
        for r in await store.rows(
            "SELECT id FROM messages WHERE chat_id=? ORDER BY created_at,id", (chat_id,)
        )
    ]


async def sources(store: Store, chat_id: str) -> dict[str, list[Source]]:
    out: dict[str, list[Source]] = {}
    for r in await store.rows(
        "SELECT message_sources.*,messages.created_at AS source_saved_at "
        "FROM message_sources JOIN messages ON message_i"
        "d=messages.id WHERE chat_id=? ORDER BY n",
        (chat_id,),
    ):
        cached = await store.one("SELECT fetched_at FROM page_cache WHERE url=?", (r["url"],))
        parsed = Source(
            **{
                **r,
                "domain": urlsplit(str(r["url"])).hostname or "",
                "fetched_at": str(cached["fetched_at"]) if cached else str(r["source_saved_at"]),
                "passages": json.loads(str(r["passages_json"])),
            }
        )
        out.setdefault(str(r["message_id"]), []).append(parsed)
    return out


async def reads(store: Store, chat_id: str) -> dict[str, list[WebRead]]:
    out: dict[str, list[WebRead]] = {}
    for r in await store.rows(
        "SELECT web_reads.* FROM web_reads JOIN messages ON message_id=messages.id WHERE chat_id=?",
        (chat_id,),
    ):
        out.setdefault(str(r["message_id"]), []).append(WebRead(**r))
    return out


async def save(store: Store, msg: Message, final: bool = False) -> None:
    from .connections import now

    statements: list[tuple[str, tuple[object, ...]]] = [
        (
            "UPDATE messages SET content=?,reasoning=?,status=?,error_json=?,stats_js"
            "on=?,web_json=?,updated_at=? WHERE id=?",
            (
                msg.content,
                msg.reasoning,
                msg.status,
                msg.error.model_dump_json() if msg.error else None,
                msg.stats.model_dump_json() if msg.stats else None,
                msg.web.model_dump_json() if msg.web else None,
                now(),
                msg.id,
            ),
        )
    ]
    if final:
        statements += [
            ("DELETE FROM chat_search WHERE message_id=?", (msg.id,)),
            (
                "INSERT INTO chat_search(chat_id,message_id,title,content) SELECT chat_id"
                ",id,(SELECT title FROM chats WHERE id=chat_id),content FROM messages WHE"
                "RE id=?",
                (msg.id,),
            ),
        ]
    await store.batch(statements)
