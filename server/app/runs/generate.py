"""Answer generation; search is a single hook before the provider stream."""

from __future__ import annotations

import asyncio
from time import monotonic
from typing import TYPE_CHECKING, Any

from ..db import chats, messages, settings
from ..errors import AppError
from ..providers.base import ChatRequest, Finish, ReasoningDelta, TextDelta, Timing, Usage
from ..schemas import ErrorDetail, ModelInfo, Stats, WebInfo
from .context import Context

if TYPE_CHECKING:
    from .manager import Run, RunManager


async def generate(
    manager: RunManager,
    run: Run,
    model: ModelInfo,
    context: Context,
    params: dict[str, Any],
    force_web: bool,
) -> None:
    started = monotonic()
    first: float | None = None
    reasoning_started: float | None = None
    last_delta = started
    last_flush = started
    stats = Stats(
        context_length=model.context_length or 8192,
        dropped_message_count=context.dropped,
        params=params,
    )
    run.message.stats = stats
    conn = model.connection_id
    connection = await manager.store.one(
        "SELECT max_concurrent FROM connections WHERE id=?", (conn,)
    )
    limit = int(str(connection["max_concurrent"])) if connection else 1
    idle = not any(
        other.id != run.id
        and not other.closed
        and other.message.model
        and other.message.model.connection_id == conn
        for other in manager.runs.values()
    )
    if conn not in manager.semaphores or (idle and manager.limits.get(conn) != limit):
        manager.semaphores[conn] = asyncio.Semaphore(limit)
        manager.limits[conn] = limit
    semaphore = manager.semaphores[conn]
    queued = False
    stream = None
    try:
        request = ChatRequest(
            model.model_id, context.messages, params, model.context_length, params.get("reasoning")
        )
        if run.research_enabled:
            if manager.research_hook is None:
                raise AppError("research_unavailable", "Research is unavailable.", 422)
            await run.emit(
                "run.started",
                {
                    "assistant_message_id": run.message.id,
                    "connection_id": conn,
                    "model_id": model.model_id,
                    "model_loaded": model.loaded,
                },
            )
            await manager.research_hook(run, request, context, semaphore)
        if semaphore.locked():
            manager.waiting[conn] = manager.waiting.get(conn, 0) + 1
            queued = True
            await run.emit("run.queued", {"position": manager.waiting[conn]})
        async with semaphore:
            if queued:
                manager.waiting[conn] -= 1
                queued = False
            if not run.research_enabled:
                await run.emit(
                    "run.started",
                    {
                        "assistant_message_id": run.message.id,
                        "connection_id": conn,
                        "model_id": model.model_id,
                        "model_loaded": model.loaded,
                    },
                )
            adapter = await manager.registry.adapter(conn)

            chat = await chats.chat(manager.store, run.message.chat_id)
            if run.research_enabled:
                pass  # Research prepared the existing answer request before this lock.
            elif chat.library_enabled and manager.library_hook:
                await manager.library_hook(run, request, context)
            elif (
                context.has_recording
                and (await settings.get(manager.store))["transcription.block_web"]
            ):
                run.message.web = WebInfo(
                    status="skipped",
                    notice=ErrorDetail(code="search_blocked_recording", message=""),
                )
                await run.emit("search.skipped", {"reason": "recording"})
            elif manager.web_hook and (chat.web_enabled or force_web):
                await manager.web_hook(run, request, context, force_web)
            stream = adapter.stream(request)
            async for event in stream:
                clock = monotonic()
                if isinstance(event, (TextDelta, ReasoningDelta)):
                    if first is None:
                        first = clock
                        stats.ttft_ms = (first - started) * 1000
                    last_delta = clock
                    if isinstance(event, TextDelta):
                        if reasoning_started is not None and stats.reasoning_ms is None:
                            stats.reasoning_ms = (clock - reasoning_started) * 1000
                        run.message.content += event.text
                        await run.emit("text.delta", {"text": event.text})
                    else:
                        if reasoning_started is None:
                            reasoning_started = clock
                        run.message.reasoning = (run.message.reasoning or "") + event.text
                        await run.emit("reasoning.delta", {"text": event.text})
                    if last_flush == started or clock - last_flush >= 1:
                        await messages.save(manager.store, run.message)
                        last_flush = clock
                elif isinstance(event, Usage):
                    stats.prompt_tokens = event.prompt_tokens
                    stats.completion_tokens = event.completion_tokens
                    stats.tokens_estimated = False
                    chars = sum(len(m.content) for m in request.messages)
                    if chars and event.prompt_tokens:
                        ratio = 0.7 * context.ratio + 0.3 * max(
                            0.05, min(1, event.prompt_tokens / chars)
                        )
                        await manager.store.execute(
                            "INSERT INTO model_prefs(connection_id,model_id,tokens_per_char) "
                            "VALUES ("
                            "?,?,?) ON CONFLICT(connection_id,model_id) DO UPDATE SET "
                            "tokens_per_char"
                            "=excluded.tokens_per_char",
                            (conn, model.model_id, ratio),
                        )
                elif isinstance(event, Timing):
                    stats.load_ms = event.load_ms
                    if event.gen_ms:
                        stats.tokens_per_sec = stats.completion_tokens / event.gen_ms * 1000
                elif isinstance(event, Finish):
                    if event.reason == "error":
                        code, _, detail = (event.detail or "provider_error").partition(":")
                        raise AppError(code, detail or code, 502)
                    stats.finish_reason = event.reason
            run.message.status = "complete"
    except asyncio.CancelledError:
        run.message.status = "stopped"
        stats.finish_reason = "stopped"
    except Exception as exc:
        run.message.status = "error"
        stats.finish_reason = "error"
        run.message.error = ErrorDetail(
            code=exc.code if isinstance(exc, AppError) else "provider_error",
            message=exc.message if isinstance(exc, AppError) else "Generation failed.",
        )
    finally:
        if queued:
            manager.waiting[conn] -= 1
        if stream:
            await stream.aclose()
        stats.total_ms = (monotonic() - started) * 1000
        if stats.tokens_estimated:
            stats.completion_tokens = round(
                len(run.message.content + str(run.message.reasoning or "")) * 0.3
            )
        if not stats.tokens_per_sec and first:
            stats.tokens_per_sec = stats.completion_tokens / max(0.001, last_delta - first)
        if manager.web_finalize:
            await manager.web_finalize(run)
        if manager.library_finalize:
            await manager.library_finalize(run)
        await messages.save(manager.store, run.message, True)
        manager.registry.updated = 0  # A generation may have loaded/ejected a model.
        if run.message.error:
            await run.emit(
                "message.error",
                {
                    **run.message.error.model_dump(),
                    "message_snapshot": run.message.model_dump(),
                },
            )
        else:
            await run.emit("message.done", {"message": run.message.model_dump()})
        if run.message.status == "complete" and not run.research_enabled:
            from .titles import title

            try:
                await title(manager, run, model)
            except (Exception, asyncio.CancelledError):
                pass  # Title failure/cancellation keeps the completed answer and fallback.
        await run.emit("run.closed", {})
        asyncio.get_running_loop().call_later(900, manager.runs.pop, run.id, None)
