import json

from fastapi import APIRouter, Request

from ..db import chats, messages, settings
from ..db.connections import now, uid
from ..errors import AppError
from ..runs.context import assemble
from ..schemas import Regenerate, RunResponse

router = APIRouter(prefix="/api/messages")


@router.post("/{identifier}/regenerate", status_code=202)
async def regenerate(identifier: str, body: Regenerate, request: Request) -> RunResponse:
    old = await messages.message(request.app.state.store, identifier)
    async with request.app.state.runs.chat_lock(old.chat_id):
        return await start_regeneration(identifier, body, request)


async def start_regeneration(identifier: str, body: Regenerate, request: Request) -> RunResponse:
    store = request.app.state.store
    old = await messages.message(store, identifier)
    if old.role != "assistant":
        raise AppError("validation_error", "Only assistant messages can be regenerated.", 422)
    if any(r.chat_id == old.chat_id for r in await request.app.state.runs.active()):
        raise AppError("run_active", "This chat is still generating.", 409)
    chat = await chats.chat(store, old.chat_id)
    model = await request.app.state.registry.resolve(
        body.connection_id or chat.connection_id, body.model_id or chat.model_id
    )
    params = await request.app.state.registry.params(model, chat.params)
    assembled = await assemble(
        store,
        request.app.state.config.data_dir,
        chat,
        await messages.list_messages(store, chat.id),
        old.parent_id,
        model,
        params,
        await settings.get(store),
    )
    new_id, date = uid(), now()
    await store.batch(
        [
            (
                "INSERT INTO messages(id,chat_id,parent_id,role,status,connection_id,mode"
                "l_id,params_json,created_at,updated_at) VALUES (?,?,?,'assistant','strea"
                "ming',?,?,?,?,?)",
                (
                    new_id,
                    old.chat_id,
                    old.parent_id,
                    model.connection_id,
                    model.model_id,
                    json.dumps(params),
                    date,
                    date,
                ),
            ),
            (
                "UPDATE chats SET current_leaf_id=?,connection_id=?,model_id=?,updated_at"
                "=? WHERE id=?",
                (new_id, model.connection_id, model.model_id, date, chat.id),
            ),
        ]
    )
    assistant = await messages.message(store, new_id)
    run = request.app.state.runs.start(assistant, model, assembled, params, body.force_web)
    return RunResponse(run_id=run.id, assistant_message=assistant)
