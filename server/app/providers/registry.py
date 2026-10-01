import asyncio
import json
from time import monotonic

from ..db.connections import list_connections
from ..db.core import Store
from ..errors import AppError
from ..schemas import ModelInfo
from .ollama import Ollama


class Registry:
    def __init__(self, store: Store) -> None:
        self.store = store
        self.adapters: dict[str, Ollama] = {}
        self.cache: list[ModelInfo] = []
        self.updated = 0.0
        self.lock = asyncio.Lock()
        self.errors: dict[str, str] = {}
        self.latencies: dict[str, float] = {}

    async def adapter(self, connection_id: str) -> Ollama:
        connection = next(
            (c for c in await list_connections(self.store) if c.id == connection_id and c.enabled),
            None,
        )
        if not connection:
            raise AppError(
                "runtime_unreachable", "The Ollama connection is disabled or missing.", 422
            )
        old = self.adapters.get(connection_id)
        if old and old.base_url != connection.base_url:
            await old.close()
            old = None
        if not old:
            old = Ollama(connection.id, connection.base_url, connection.keep_alive)
            self.adapters[connection_id] = old
        old.keep_alive = connection.keep_alive
        return old

    async def models(self, refresh: bool = False, include_hidden: bool = False) -> list[ModelInfo]:
        async with self.lock:
            if refresh or monotonic() - self.updated > 10:
                out: list[ModelInfo] = []
                self.errors = {}
                for c in await list_connections(self.store):
                    if not c.enabled:
                        continue
                    started = monotonic()
                    try:
                        out.extend(await (await self.adapter(c.id)).list_models())
                    except AppError as exc:
                        self.errors[c.id] = exc.message
                    finally:
                        self.latencies[c.id] = (monotonic() - started) * 1000
                prefs = {
                    (r["connection_id"], r["model_id"]): r
                    for r in await self.store.rows("SELECT * FROM model_prefs")
                }
                for m in out:
                    pref = prefs.get((m.connection_id, m.model_id), {})
                    m.display_name = str(pref.get("display_name") or m.display_name)
                    m.context_length = (
                        int(str(pref["context_length"]))
                        if pref.get("context_length")
                        else m.context_length
                    )
                    if pref.get("vision_override") is not None:
                        m.vision = bool(pref["vision_override"])
                    m.hidden = bool(pref.get("hidden"))
                    m.params_defaults = json.loads(str(pref.get("params_json") or "{}"))
                self.cache = sorted(out, key=lambda m: (not m.loaded, m.display_name.casefold()))
                self.updated = monotonic()
            return [
                m.model_copy()
                for m in self.cache
                if include_hidden or (m.chat_capable and not m.hidden)
            ]

    async def resolve(self, connection_id: str | None, model_id: str | None) -> ModelInfo:
        models = await self.models()
        model = next(
            (m for m in models if m.connection_id == connection_id and m.model_id == model_id), None
        )
        if not model:
            if connection_id in self.errors:
                raise AppError("runtime_unreachable", self.errors[connection_id], 502)
            raise AppError("model_not_found", "Choose an available Ollama model.", 422)
        return model

    async def params(self, model: ModelInfo, chat_params: dict[str, object]) -> dict[str, object]:
        pref = await self.store.one(
            "SELECT params_json FROM model_prefs WHERE connection_id=? AND model_id=?",
            (model.connection_id, model.model_id),
        )
        return {
            k: v
            for k, v in {
                **(json.loads(str(pref["params_json"])) if pref else {}),
                **{k: v for k, v in chat_params.items() if v is not None},
            }.items()
            if v is not None
        }

    async def close(self) -> None:
        for adapter in self.adapters.values():
            await adapter.close()
