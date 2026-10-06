import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from ..db import messages
from ..db.connections import now, uid
from ..db.core import Store
from ..errors import AppError
from ..providers.base import ChatRequest
from ..providers.registry import Registry
from ..schemas import ActiveRun, Message, ModelInfo, RunEvent
from .context import Context


@dataclass
class Run:
    id: str
    message: Message
    events: list[RunEvent] = field(default_factory=list)
    changed: asyncio.Condition = field(default_factory=asyncio.Condition)
    closed: bool = False
    task: asyncio.Task[None] | None = None

    async def emit(self, kind: Any, data: dict[str, Any]) -> None:
        async with self.changed:
            self.events.append(RunEvent.model_validate({"type": kind, "data": data}))
            if kind == "run.closed":
                self.closed = True
            self.changed.notify_all()

    async def tail(self, after: int = 0) -> AsyncIterator[tuple[int, RunEvent]]:
        index = max(0, after)
        while True:
            async with self.changed:
                while len(self.events) <= index and not self.closed:
                    await self.changed.wait()
                batch = self.events[index:]
                done = self.closed
            for event in batch:
                index += 1
                yield index, event
            if done:
                return


WebHook = Callable[[Run, ChatRequest, Context, bool], Awaitable[None]]


class RunManager:
    def __init__(self, store: Store, registry: Registry, data_dir: Any) -> None:
        self.store, self.registry, self.data_dir = store, registry, data_dir
        self.runs: dict[str, Run] = {}
        self.semaphores: dict[str, asyncio.Semaphore] = {}
        self.limits: dict[str, int] = {}
        self.waiting: dict[str, int] = {}
        self.web_hook: WebHook | None = None
        self.web_finalize: Callable[[Run], Awaitable[None]] | None = None
        self.library_hook: Callable[[Run, ChatRequest, Context], Awaitable[None]] | None = None
        self.library_finalize: Callable[[Run], Awaitable[None]] | None = None
        self.chat_locks: dict[str, asyncio.Lock] = {}

    def chat_lock(self, chat_id: str) -> asyncio.Lock:
        return self.chat_locks.setdefault(chat_id, asyncio.Lock())

    async def recover(self) -> None:
        await self.store.execute(
            "UPDATE messages SET status='interrupted',error_json=?,updated_at=? WHERE"
            " status='streaming'",
            ('{"code":"interrupted","message":"Interrupted because the server restarted."}', now()),
        )

    def start(
        self,
        message: Message,
        model: ModelInfo,
        context: Context,
        params: dict[str, Any],
        force_web: bool = False,
    ) -> Run:
        run = Run(uid(), message)
        self.runs[run.id] = run
        run.task = asyncio.create_task(
            self.generate(run, model, context, params, force_web), name="answer-" + run.id
        )
        return run

    async def active(self) -> list[ActiveRun]:
        return [
            ActiveRun(run_id=r.id, chat_id=r.message.chat_id, assistant_message_id=r.message.id)
            for r in self.runs.values()
            if not r.closed and r.message.status == "streaming"
        ]

    async def cancel(self, identifier: str) -> None:
        run = self.runs.get(identifier)
        if not run:
            raise AppError("not_found", "Run not found.", 404)
        if run.closed:
            return
        if run.task:
            run.task.cancel()
            await asyncio.gather(run.task, return_exceptions=True)
        if not run.closed:
            if run.message.status == "streaming":
                run.message.status = "stopped"
                if run.message.stats:
                    run.message.stats.finish_reason = "stopped"
            await messages.save(self.store, run.message, True)
            await run.emit("message.done", {"message": run.message.model_dump()})
            await run.emit("run.closed", {})

    async def close(self) -> None:
        for run in list(self.runs.values()):
            if not run.closed:
                await self.cancel(run.id)

    async def generate(
        self, run: Run, model: ModelInfo, context: Context, params: dict[str, Any], force_web: bool
    ) -> None:
        from .generate import generate

        await generate(self, run, model, context, params, force_web)
