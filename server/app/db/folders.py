from ..errors import AppError
from ..schemas import Folder, FolderCreate, FolderPatch
from .connections import now, uid
from .core import Store


async def get(store: Store, identifier: str) -> Folder:
    row = await store.one(
        "SELECT folders.*, (SELECT COUNT(*) FROM chats WHERE folder_id=folders.id "
        "AND EXISTS (SELECT 1 FROM messages WHERE chat_id=chats.id)) AS count "
        "FROM folders WHERE id=?",
        (identifier,),
    )
    if not row:
        raise AppError("not_found", "Folder not found.", 404)
    return Folder(**row)


async def listing(store: Store) -> list[Folder]:
    rows = await store.rows("SELECT id FROM folders ORDER BY position,created_at,id")
    return [await get(store, str(row["id"])) for row in rows]


def name(value: str | None) -> str:
    if not value or not value.strip():
        raise AppError("validation_error", "Enter a folder name.", 422)
    return value.strip()


async def create(store: Store, body: FolderCreate) -> Folder:
    identifier, date = uid(), now()
    await store.execute(
        "INSERT INTO folders(id,name,position,created_at,updated_at) "
        "VALUES (?,?,(SELECT COALESCE(MAX(position),-1)+1 FROM folders),?,?)",
        (identifier, name(body.name), date, date),
    )
    return await get(store, identifier)


async def patch(store: Store, identifier: str, body: FolderPatch) -> Folder:
    await get(store, identifier)
    values = body.model_dump(exclude_unset=True)
    if "name" in values:
        values["name"] = name(values["name"])
    if "position" in values and values["position"] is None:
        raise AppError("validation_error", "Enter a folder position.", 422)
    values["updated_at"] = now()
    await store.execute(
        "UPDATE folders SET " + ",".join(k + "=?" for k in values) + " WHERE id=?",
        (*values.values(), identifier),
    )
    return await get(store, identifier)


async def delete(store: Store, identifier: str) -> None:
    await get(store, identifier)
    await store.execute("DELETE FROM folders WHERE id=?", (identifier,))
