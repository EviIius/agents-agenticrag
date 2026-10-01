import asyncio
import re

from ..db import settings
from ..db.connections import now
from ..providers.base import ChatRequest, ProviderMessage, TextDelta
from ..schemas import ModelInfo
from .manager import Run, RunManager


async def title(manager: RunManager, run: Run, model: ModelInfo) -> None:
    store = manager.store
    values = await settings.get(store)
    chat = await store.one("SELECT * FROM chats WHERE id=?", (run.message.chat_id,))
    count = await store.one(
        "SELECT count(*) AS n FROM messages WHERE chat_id=? AND role='assistant'",
        (run.message.chat_id,),
    )
    if (
        not values["auto_title"]
        or not chat
        or chat["title_source"] == "user"
        or not count
        or count["n"] != 1
    ):
        return
    parent = await store.one("SELECT content FROM messages WHERE id=?", (run.message.parent_id,))
    utility = values.get("utility_model")
    if utility:
        model = await manager.registry.resolve(utility["connection_id"], utility["model_id"])
    adapter = await manager.registry.adapter(model.connection_id)
    req = ChatRequest(
        model.model_id,
        [
            ProviderMessage(
                "user",
                "Write a 3–6 word title for this conversation. Reply with the title only,"
                " no quotes.\n\n"
                + str(parent["content"] if parent else "")[:1000]
                + "\n\n"
                + run.message.content[:500],
            )
        ],
        {"temperature": 0.2, "max_tokens": 24},
        model.context_length,
        "off",
    )
    text = ""
    async with asyncio.timeout(20):
        async with manager.semaphores.setdefault(model.connection_id, asyncio.Semaphore(1)):
            stream = adapter.stream(req)
            try:
                async for event in stream:
                    if isinstance(event, TextDelta):
                        text += event.text
            finally:
                await stream.aclose()
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip().strip("\"'").rstrip(".")
    text = " ".join(text.split())[:80]
    if not text:
        return
    await store.execute(
        "UPDATE chats SET title=?,title_source='auto',updated_at=? WHERE id=? AND"
        " title_source!='user'",
        (text, now(), run.message.chat_id),
    )
    current = await store.one("SELECT title_source FROM chats WHERE id=?", (run.message.chat_id,))
    if current and current["title_source"] == "auto":
        await store.execute(
            "UPDATE chat_search SET title=? WHERE chat_id=?", (text, run.message.chat_id)
        )
        await run.emit("chat.title", {"chat_id": run.message.chat_id, "title": text})
