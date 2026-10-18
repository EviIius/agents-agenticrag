"""N0 native loop. Not installed as a RunManager hook; production paths stay off."""

import asyncio
import copy
import json
from dataclasses import dataclass
from html import escape
from time import monotonic
from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from ..db import messages
from ..errors import AppError
from ..providers.base import (
    ChatRequest,
    Finish,
    ProviderMessage,
    ReasoningDelta,
    TextDelta,
    Timing,
    ToolCall,
    Usage,
    validate_reasoning,
)
from ..providers.ollama import Ollama
from ..schemas import (
    AgentInfo,
    AgentPart,
    AgentStep,
    ErrorDetail,
    LibraryInfo,
    ModelInfo,
    Stats,
    WebInfo,
)
from ..search import citations
from .agent_prompt import prompt
from .agent_sources import Sources
from .agent_tools import ReadPage, Tools
from .context import Context
from .manager import Run, RunManager


class Budgets(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
    steps: int = Field(default=6, ge=1, le=6)
    searches: int = Field(default=4, ge=0, le=4)
    pages: int = Field(default=6, ge=0, le=6)
    library_searches: int = Field(default=4, ge=0, le=4)
    calculations: int = Field(default=8, ge=0, le=8)
    seconds: float = Field(default=180, gt=0, le=180)
    context_fraction: float = Field(default=0.7, gt=0, le=0.7)


@dataclass(frozen=True)
class Qualification:
    digest: str
    context_length: int
    runtime_version: str
    validity: float


COUNTERS = {
    "web_search": "searches",
    "read_page": "pages",
    "library_search": "library_searches",
    "calculate": "calculations",
}
T = TypeVar("T")


class AnswerNow(Exception):
    """Internal control signal, never a model instruction or retry."""


class Agent:
    def __init__(
        self,
        manager: RunManager,
        adapter: Ollama,
        model: ModelInfo,
        tools: Tools,
        qualifications: list[Qualification],
        *,
        budgets: Budgets | None = None,
        answer_now: asyncio.Event | None = None,
    ) -> None:
        self.manager, self.adapter, self.model, self.tools = manager, adapter, model, tools
        self.qualifications, self.budgets = qualifications, budgets or Budgets()
        self.answer_now = answer_now or asyncio.Event()

    async def guard(self, request: ChatRequest, context: Context) -> None:
        model = self.model
        if not model.tools or not model.chat_capable or request.model_id != model.model_id:
            raise AppError("agent_unsupported", "This model can't use the native tools.", 422)
        validate_reasoning(model, request.reasoning)
        if (
            not request.context_length
            or request.context_length != model.context_length
            or model.context_limit is not None
            and request.context_length > model.context_limit
            or not model.digest
        ):
            raise AppError("agent_unqualified", "This model context has not been qualified.", 422)
        version = (await self.adapter.json("GET", "/api/version")).get("version")
        if not any(
            q.digest == model.digest
            and q.context_length == request.context_length
            and q.runtime_version == version
            and q.validity >= 0.95
            for q in self.qualifications
        ):
            raise AppError(
                "agent_unqualified", "This model configuration needs its tool probe.", 422
            )
        if context.has_recording and self.tools.kind == "web" and self.tools.block_web:
            raise AppError("search_blocked_recording", "Web tools are blocked for recordings.", 422)

    async def __call__(
        self,
        run: Run,
        request: ChatRequest,
        context: Context,
        semaphore: asyncio.Semaphore,
    ) -> None:
        await self.guard(request, context)
        self.tools = self.tools.for_run()
        started = monotonic()
        loop = copy.deepcopy(request)
        loop.tools = self.tools.schemas()
        loop.messages[0].content += "\n\n" + prompt(self.tools.kind)
        info = run.message.agent = AgentInfo()
        stats = run.message.stats = Stats(
            context_length=request.context_length or 8192, params=request.params
        )
        sources = Sources(self.manager.store, run.message.id, self.tools.kind)
        if self.tools.kind == "web":
            run.message.web = WebInfo(status="used")
        else:
            run.message.library = LibraryInfo(status="used")

        async def save() -> None:
            await messages.save(self.manager.store, run.message)

        async def turn(closing: bool = False) -> tuple[str, list[ToolCall]]:
            calls: list[ToolCall] = []
            text = ""
            stream = None
            async with semaphore:
                info.calls += 1  # No SDK retry or hidden auxiliary call.
                try:
                    stream = self.adapter.stream(loop)
                    async for event in stream:
                        if isinstance(event, (TextDelta, ReasoningDelta)) and stats.ttft_ms is None:
                            stats.ttft_ms = (monotonic() - started) * 1000
                        if isinstance(event, TextDelta):
                            text += event.text
                            run.message.content += event.text
                            if not run.message.parts or run.message.parts[-1].type != "text":
                                run.message.parts.append(AgentPart(type="text"))
                            run.message.parts[-1].text += event.text
                            await run.emit("text.delta", {"text": event.text})
                        elif isinstance(event, ReasoningDelta):
                            run.message.reasoning = (run.message.reasoning or "") + event.text
                            await run.emit("reasoning.delta", {"text": event.text})
                        elif isinstance(event, ToolCall):
                            if closing or len(calls) >= 32:
                                raise AppError("provider_error", "Unexpected tool call.", 502)
                            calls.append(event)
                        elif isinstance(event, Usage):
                            stats.prompt_tokens = event.prompt_tokens
                            stats.completion_tokens += event.completion_tokens
                            stats.tokens_estimated = False
                        elif isinstance(event, Timing):
                            stats.load_ms = event.load_ms
                        elif isinstance(event, Finish):
                            if event.reason == "error":
                                raise AppError("provider_error", "Native tool request failed.", 502)
                            stats.finish_reason = event.reason
                finally:
                    if stream:
                        await stream.aclose()
                    await save()
            return text, calls

        async def interruptible(task: asyncio.Task[T]) -> T:
            now = asyncio.create_task(self.answer_now.wait())
            try:
                done, _ = await asyncio.wait([task, now], return_when=asyncio.FIRST_COMPLETED)
                if task in done:
                    return await task
                info.limit_reached = "answer_now"
                raise AnswerNow
            finally:
                for child in (task, now):
                    if not child.done():
                        child.cancel()
                await asyncio.gather(task, now, return_exceptions=True)

        async def model_step() -> tuple[str, list[ToolCall]]:
            try:
                return await interruptible(asyncio.create_task(turn()))
            except AnswerNow:
                return "", []

        try:
            async with asyncio.timeout(self.budgets.seconds):
                for _ in range(self.budgets.steps):
                    estimated = context.ratio * len(
                        json.dumps([[m.content, m.tool_calls] for m in loop.messages])
                        + json.dumps(loop.tools)
                    )
                    if estimated >= stats.context_length * self.budgets.context_fraction:
                        info.limit_reached = "context"
                        break
                    if self.answer_now.is_set():
                        info.limit_reached = "answer_now"
                        break
                    info.steps += 1
                    text, calls = await model_step()
                    if info.limit_reached or not calls:
                        break
                    history: list[dict[str, Any]] = []
                    for call in calls:
                        try:
                            parsed = json.loads(call.arguments)
                        except ValueError:
                            parsed = None
                        # Preserve valid native objects. A malformed call gets a placeholder
                        # only in replay history; validation uses the ORIGINAL bytes below.
                        history.append(
                            {
                                "id": call.id,
                                "type": "function",
                                "function": {
                                    "name": call.name,
                                    "arguments": parsed if isinstance(parsed, dict) else {},
                                },
                            }
                        )
                    loop.messages.append(ProviderMessage("assistant", text, tool_calls=history))
                    for index, call in enumerate(calls):
                        step = AgentStep(
                            id=f"{info.steps}-{len(run.message.parts)}",
                            tool=call.name,
                            arguments=(
                                history[index]["function"]["arguments"]
                                if len(call.arguments) <= 10_000
                                else {}
                            ),
                        )
                        run.message.parts.append(AgentPart(type="tool", step=step))
                        clock = monotonic()
                        await run.emit("tool.started", {"step": step.model_dump()})
                        await save()
                        try:
                            value = self.tools.validate(call.name, call.arguments)
                            step.arguments = value.model_dump()
                            counter = COUNTERS[call.name]
                            if getattr(info, counter) >= getattr(self.budgets, counter):
                                raise ValueError("Tool budget reached")
                            setattr(info, counter, getattr(info, counter) + 1)
                            output = await interruptible(
                                asyncio.create_task(self.tools.execute(call.name, value))
                            )
                            # Read output is bounded before it enters the conversation/catalogue.
                            if isinstance(value, ReadPage):
                                remaining = int(1200 / max(context.ratio, 0.05))
                                for source in output.sources:
                                    for passage in source.passages:
                                        passage.text = passage.text[:remaining]
                                        remaining -= len(passage.text)
                            block = await sources.add(output.sources) if output.sources else ""
                            info.source_count = len(sources.values)
                            if output.read:
                                await sources.read(output.read)
                            result = block + "\n" + escape(output.text)
                            step.status = "done"
                        except (ValueError, ArithmeticError):
                            info.invalid_calls += 1
                            step.status = "failed"
                            result = "Tool refused: invalid arguments, permission or budget."
                            step.detail = result
                        except asyncio.CancelledError:
                            step.status = "stopped"
                            step.detail = "Stopped"
                            raise
                        except AnswerNow:
                            step.status = "stopped"
                            result = "Tool interrupted to answer now."
                            step.detail = result
                        except Exception:
                            step.status = "failed"
                            result = "Tool unavailable."
                            step.detail = result
                        finally:
                            step.ms = (monotonic() - clock) * 1000
                            await run.emit("tool.finished", {"step": step.model_dump()})
                            await save()
                        loop.messages.append(
                            ProviderMessage(
                                "tool",
                                result + "\nBudget: " + info.model_dump_json(),
                                tool_name=call.name,
                            )
                        )
                        if info.limit_reached:
                            for pending in calls[index + 1 :]:
                                loop.messages.append(
                                    ProviderMessage(
                                        "tool",
                                        "Not executed: answering now.",
                                        tool_name=pending.name,
                                    )
                                )
                            break
                    if info.limit_reached:
                        break
                else:
                    info.limit_reached = "steps"
                if info.limit_reached:
                    loop.tools = None
                    await turn(closing=True)  # One closing call within the same hard deadline.
            run.message.status = "complete"
        except TimeoutError:
            info.limit_reached = "time"
            run.message.status = "complete"
            info.notice = ErrorDetail(code="agent_time_limit", message="Time limit reached.")
        except asyncio.CancelledError:
            run.message.status = "stopped"
            stats.finish_reason = "stopped"
        except Exception:
            run.message.status = "error"
            stats.finish_reason = "error"
            run.message.error = ErrorDetail(code="provider_error", message="Native agent failed.")
        finally:
            info.source_count = len(sources.values)
            before = run.message.content
            info.invalid_citations = len(
                citations.cited(before) - set(range(1, info.source_count + 1))
            )
            if info.invalid_citations:
                info.notice = ErrorDetail(
                    code="invalid_citation", message="Unknown source citation"
                )
            run.message.content = citations.normalize(before, info.source_count)
            if run.message.content != before:
                for part in run.message.parts:
                    if part.type == "text":
                        part.text = citations.normalize(part.text, info.source_count)
            if (
                info.source_count
                and run.message.status == "complete"
                and not citations.cited(run.message.content)
            ):
                info.notice = ErrorDetail(code="uncited", message="No sources cited")
            if self.manager.web_finalize:
                await self.manager.web_finalize(run)
            if self.manager.library_finalize:
                await self.manager.library_finalize(run)
            stats.total_ms = (monotonic() - started) * 1000
            await messages.save(self.manager.store, run.message, True)
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
            await run.emit("run.closed", {})
