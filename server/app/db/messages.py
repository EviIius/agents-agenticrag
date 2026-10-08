import json
from urllib.parse import urlsplit

from ..errors import AppError
from ..schemas import (
    ErrorDetail,
    LibraryInfo,
    Message,
    MessageModel,
    Passage,
    ResearchInfo,
    ResearchStep,
    Source,
    Stats,
    WebInfo,
    WebRead,
)
from .attachments import attachment
from .core import Store


async def message(store: Store, identifier: str) -> Message:
    row = await store.one("SELECT * FROM messages WHERE id=?", (identifier,))
    if not row:
        raise AppError("not_found", "Message not found.", 404)
    attachments = [
        await attachment(store, str(r["id"]))
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
            "research": ResearchInfo.model_validate_json(row["research_json"])
            if row["research_json"]
            else None,
            "activity": [
                ResearchStep.model_validate(s) for s in json.loads(row["activity_json"] or "[]")
            ],
            "attachments": attachments,
            "error": ErrorDetail(**json.loads(str(row["error_json"])))
            if row["error_json"]
            else None,
            "stats": Stats(**json.loads(str(row["stats_json"]))) if row["stats_json"] else None,
            "web": WebInfo(**json.loads(str(row["web_json"]))) if row["web_json"] else None,
            "library": LibraryInfo(**json.loads(row["library_json"]))
            if row["library_json"]
            else None,
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
    for r in await store.rows(
        "SELECT message_library_sources.*,messages.created_at AS source_saved_at "
        "FROM message_library_sources JOIN messages ON message_id=messages.id "
        "WHERE chat_id=? ORDER BY n",
        (chat_id,),
    ):
        parsed = Source(
            n=r["n"],
            title=r["filename"],
            site_name=r["filename"],
            domain="",
            fetched_at=r["source_saved_at"],
            kind="document",
            document_id=r["document_id"],
            page_start=r["page_start"],
            page_end=r["page_end"],
            cited=bool(r["cited"]),
            url=(
                f"/api/library/documents/{r['document_id']}/file"
                + (f"#page={r['page_start']}" if r["page_start"] else "")
            )
            if r["document_id"]
            else "",
            passages=[
                Passage.model_validate({"source_url": r["document_id"] or "", "ord": i, **p})
                for i, p in enumerate(json.loads(r["passages_json"]))
            ],
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
            "on=?,web_json=?,library_json=?,research_json=?,activity_json=?,updated_at=? "
            "WHERE id=?",
            (
                msg.content,
                msg.reasoning,
                msg.status,
                msg.error.model_dump_json() if msg.error else None,
                msg.stats.model_dump_json() if msg.stats else None,
                msg.web.model_dump_json() if msg.web else None,
                msg.library.model_dump_json() if msg.library else None,
                msg.research.model_dump_json() if msg.research else None,
                json.dumps([s.model_dump() for s in msg.activity]),
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
