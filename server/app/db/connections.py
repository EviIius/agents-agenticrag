from datetime import UTC, datetime
from uuid import uuid4

from ..schemas import Connection, ConnectionCreate
from .core import Store


def now() -> str:
    return datetime.now(UTC).isoformat()


def uid() -> str:
    return uuid4().hex


async def list_connections(store: Store) -> list[Connection]:
    return [
        Connection(**{**r, "has_api_key": bool(r["api_key"])})
        for r in await store.rows(
            "SELECT * FROM connections WHERE kind='ollama' ORDER BY created_at"
        )
    ]


async def create(store: Store, body: ConnectionCreate) -> Connection:
    identifier, date = uid(), now()
    await store.batch(
        [
            (
                "INSERT INTO connections(id,kind,name,base_url,api_key,created_at,updated"
                "_at) VALUES (?,?,?,?,?,?,?)",
                (
                    identifier,
                    "ollama",
                    body.name,
                    body.base_url.rstrip("/"),
                    body.api_key,
                    date,
                    date,
                ),
            ),
            (
                "INSERT INTO model_prefs(connection_id,model_id,hidden) VALUES (?,?,1)",
                (identifier, "llama3.3:70b-instruct-q4_K_M"),
            ),
        ]
    )
    return next(c for c in await list_connections(store) if c.id == identifier)
