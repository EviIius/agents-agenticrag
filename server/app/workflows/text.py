"""Shared unchanged text request construction for legacy and graph performers."""

import asyncio
import hashlib
from typing import Any, Protocol

from ..db.core import Store
from ..errors import AppError
from ..providers.base import ChatRequest, Finish, ProviderMessage, TextDelta
from ..runs.manager import RunManager
from . import templates
from .schemas import WorkflowRun, WorkflowStep


class TextHost(Protocol):
    store: Store
    runs: RunManager

    async def state(
        self, identifier: str, state: str, stage: str, error: str | None = None
    ) -> None: ...
    async def save_step(
        self,
        identifier: str,
        step: WorkflowStep,
        state: str,
        output: dict[str, Any] | None,
        error: str | None = None,
    ) -> None: ...
    async def record_text_request(
        self, run: WorkflowRun, step: WorkflowStep, body: dict[str, Any]
    ) -> None: ...
    async def text_delta(self, identifier: str, step: WorkflowStep, text: str) -> None: ...


async def write_text(
    self: TextHost,
    run: WorkflowRun,
    step: WorkflowStep,
    system: str,
    material: str,
    json_schema: dict[str, Any] | None = None,
) -> dict[str, Any]:
    selected = run.input.model
    model = await self.runs.registry.resolve(selected.connection_id, selected.model_id)
    params: dict[str, Any] = await self.runs.registry.params(
        model, selected.params.model_dump(exclude_none=True)
    )
    messages = [ProviderMessage("system", system), ProviderMessage("user", material)]
    pref = await self.store.one(
        "SELECT tokens_per_char FROM model_prefs WHERE connection_id=? AND model_id=?",
        (model.connection_id, model.model_id),
    )
    ratio = float(pref["tokens_per_char"] or 0.3) if pref else 0.3
    maximum = model.context_length or 8192
    reserve = int(params.get("max_tokens") or max(1024, min(8192, maximum * 0.25)))
    estimated = sum(int(len(m.content) * ratio) + 4 for m in messages)
    if estimated + reserve + 256 > maximum:
        raise AppError(
            "context_overflow",
            "The full source does not fit this model's input/output allowance. "
            "Choose a larger context or shorter source in a new run. No source was truncated.",
            422,
        )
    adapter = await self.runs.registry.adapter(model.connection_id)
    if adapter.capacity and adapter.capacity.busy:
        await self.state(run.id, "running", "Waiting for native capacity: " + step.label)
    request = ChatRequest(
        model.model_id, messages, params, maximum, params.get("reasoning"), json_schema=json_schema
    )
    saved_request: dict[str, Any] = {
        "model": model.model_id,
        "connection_id": model.connection_id,
        "context_length": maximum,
        "params": params,
        "messages": [{"role": m.role, "content": m.content} for m in messages],
        "prompt_version": templates.VERSION,
    }
    if json_schema is not None:
        saved_request["json_schema"] = json_schema
    await self.record_text_request(run, step, saved_request)
    stream = adapter.stream(request, background=True)
    output: dict[str, Any] = {
        "text": "",
        "model": selected.model_dump(),
        "model_display_name": model.display_name,
        "resolved_params": params,
        "context_length": maximum,
        "prompt_version": templates.VERSION,
        "prompt_sha256": hashlib.sha256(system.encode()).hexdigest(),
        "draft": True,
    }
    last = 0.0
    finished = False
    try:
        async for event in stream:
            if isinstance(event, TextDelta):
                if not output["text"]:
                    await self.state(run.id, "running", step.label)
                output["text"] += event.text
                await self.text_delta(run.id, step, event.text)
                clock = asyncio.get_running_loop().time()
                if clock - last >= 1:
                    await self.save_step(run.id, step, "running", output)
                    last = clock
            elif isinstance(event, Finish):
                if event.reason != "stop":
                    raise AppError(
                        "workflow_incomplete",
                        "The model did not finish this draft. "
                        "Partial output is saved; retry with your selected settings.",
                        409,
                    )
                finished = True
        if not finished or not output["text"].strip():
            raise AppError(
                "workflow_empty", "The model returned no complete draft. Retry this step.", 409
            )
        return output
    finally:
        await stream.aclose()
        if output["text"]:
            await self.save_step(run.id, step, "running", output)
