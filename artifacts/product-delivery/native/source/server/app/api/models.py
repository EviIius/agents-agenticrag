import json
from typing import cast

from fastapi import APIRouter, Request

from ..errors import AppError
from ..schemas import ModelAction, ModelInfo, ModelPrefs

router = APIRouter(prefix="/api/models")


@router.get("")
async def listing(
    request: Request, refresh: bool = False, include_hidden: bool = False
) -> list[ModelInfo]:
    return cast(list[ModelInfo], await request.app.state.registry.models(refresh, include_hidden))


@router.post("/load")
async def load(body: ModelAction, request: Request) -> dict[str, bool]:
    model = await request.app.state.registry.resolve(body.connection_id, body.model_id)
    limit = model.context_limit or model.context_max
    if body.context_length and limit and body.context_length > limit:
        raise AppError(
            "validation_error", "Context length exceeds this model’s configured limit.", 422
        )
    await (await request.app.state.registry.adapter(body.connection_id)).load(
        body.model_id, body.context_length or model.context_length
    )
    request.app.state.registry.updated = 0
    return {"ok": True}


@router.post("/unload")
async def unload(body: ModelAction, request: Request) -> dict[str, bool]:
    await (await request.app.state.registry.adapter(body.connection_id)).unload(body.model_id)
    request.app.state.registry.updated = 0
    return {"ok": True}


@router.put("/prefs")
async def prefs(body: ModelPrefs, request: Request) -> dict[str, bool]:
    store = request.app.state.store
    model = next(
        (
            m
            for m in await request.app.state.registry.models(include_hidden=True)
            if m.connection_id == body.connection_id and m.model_id == body.model_id
        ),
        None,
    )
    if model is None:
        raise AppError("model_not_found", "Choose an available Ollama model.", 422)
    limit = model.context_limit or model.context_max
    if body.context_length and limit and body.context_length > limit:
        raise AppError(
            "validation_error", "Context length exceeds this model’s configured limit.", 422
        )
    await store.execute(
        "INSERT OR IGNORE INTO model_prefs(connection_id,model_id) VALUES (?,?)",
        (body.connection_id, body.model_id),
    )
    values = body.model_dump(exclude_unset=True, exclude={"connection_id", "model_id"})
    if "params" in values:
        values["params_json"] = json.dumps(values.pop("params") or {})
    if values:
        await store.execute(
            "UPDATE model_prefs SET "
            + ",".join(k + "=?" for k in values)
            + " WHERE connection_id=? AND model_id=?",
            (*values.values(), body.connection_id, body.model_id),
        )
    request.app.state.registry.updated = 0
    return {"ok": True}
