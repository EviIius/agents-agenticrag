import json

from ..errors import AppError
from ..schemas import Chat, ChatCreate, ChatPatch, Preset
from .connections import now, uid
from .core import Store


async def chat(store: Store, identifier: str) -> Chat:
    row = await store.one("SELECT * FROM chats WHERE id=?", (identifier,))
    if not row:
        raise AppError("not_found", "Chat not found.", 404)
    return Chat(**{**row, "params": json.loads(str(row["params_json"]))})


async def create(store: Store, body: ChatCreate, preset: Preset | None = None) -> Chat:
    identifier, date = uid(), now()
    await store.execute(
        "INSERT INTO chats(id,connection_id,model_id,web_enabled,created_at,updat"
        "ed_at,system_prompt,params_json) VALUES (?,?,?,?,?,?,?,?)",
        (
            identifier,
            body.connection_id,
            body.model_id,
            bool(body.web_enabled),
            date,
            date,
            preset.system_prompt if preset else None,
            json.dumps(preset.params if preset else {}),
        ),
    )
    return await chat(store, identifier)


async def patch(store: Store, identifier: str, body: ChatPatch) -> Chat:
    await chat(store, identifier)
    values = body.model_dump(exclude_unset=True)
    if "current_leaf_id" in values and values["current_leaf_id"]:
        leaf = await store.one(
            "SELECT id FROM messages WHERE id=? AND chat_id=?",
            (values["current_leaf_id"], identifier),
        )
        if not leaf:
            raise AppError("validation_error", "Branch belongs to another chat.", 422)
    if "title" in values:
        values["title_source"] = "user"
    if "params" in values:
        values["params_json"] = json.dumps(values.pop("params") or {})
    values["updated_at"] = now()
    await store.execute(
        "UPDATE chats SET " + ",".join(k + "=?" for k in values) + " WHERE id=?",
        (*values.values(), identifier),
    )
    if "title" in values:
        await store.execute(
            "UPDATE chat_search SET title=? WHERE chat_id=?", (values["title"], identifier)
        )
    return await chat(store, identifier)
