"""Named copies of user-authored prompts and explicitly set sampling values."""

import json
import sqlite3

from ..errors import AppError
from ..schemas import Parameters, Preset, PresetCreate, PresetPatch
from .connections import now, uid
from .core import Store


def sampling(params: Parameters) -> dict[str, object]:
    if params.reasoning is not None:
        raise AppError("validation_error", "Presets do not store reasoning or context length.", 422)
    return params.model_dump(exclude_none=True, exclude={"reasoning"})


def name(value: str | None) -> str:
    if value is None or not value.strip():
        raise AppError("validation_error", "Enter a preset name.", 422)
    return value.strip()


def record(row: dict[str, object]) -> Preset:
    return Preset(**{**row, "params": json.loads(str(row["params_json"]))})


async def get(store: Store, identifier: str) -> Preset:
    row = await store.one("SELECT * FROM presets WHERE id=?", (identifier,))
    if not row:
        raise AppError("not_found", "Preset not found.", 404)
    return record(row)


async def listing(store: Store) -> list[Preset]:
    return [record(row) for row in await store.rows("SELECT * FROM presets ORDER BY position,name")]


async def create(store: Store, body: PresetCreate) -> Preset:
    identifier, date = uid(), now()
    try:
        await store.execute(
            "INSERT INTO presets(id,name,system_prompt,params_json,position,created_at,updated_at) "
            "VALUES (?,?,?,?,(SELECT COALESCE(MAX(position),-1)+1 FROM presets),?,?)",
            (
                identifier,
                name(body.name),
                body.system_prompt,
                json.dumps(sampling(body.params)),
                date,
                date,
            ),
        )
    except sqlite3.IntegrityError:
        raise AppError(
            "preset_name_taken", "A preset with this name already exists.", 409
        ) from None
    return await get(store, identifier)


async def patch(store: Store, identifier: str, body: PresetPatch) -> Preset:
    await get(store, identifier)
    values = body.model_dump(exclude_unset=True)
    if "name" in values:
        values["name"] = name(body.name)
    if "params" in values:
        values.pop("params")
        values["params_json"] = json.dumps(sampling(body.params or Parameters.model_validate({})))
    if "position" in values and values["position"] is None:
        raise AppError("validation_error", "Position must be a non-negative integer.", 422)
    values["updated_at"] = now()
    try:
        await store.execute(
            "UPDATE presets SET " + ",".join(k + "=?" for k in values) + " WHERE id=?",
            (*values.values(), identifier),
        )
    except sqlite3.IntegrityError:
        raise AppError(
            "preset_name_taken", "A preset with this name already exists.", 409
        ) from None
    return await get(store, identifier)


async def delete(store: Store, identifier: str) -> None:
    await get(store, identifier)
    await store.batch(
        [
            (
                "UPDATE settings SET value_json='null' WHERE key='default_preset_id' "
                "AND value_json=?",
                (json.dumps(identifier),),
            ),
            ("DELETE FROM presets WHERE id=?", (identifier,)),
        ]
    )
