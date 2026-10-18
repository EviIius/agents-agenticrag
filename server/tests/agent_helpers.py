"""Synthetic native transport and persisted-run fixtures, never a real runtime."""

import asyncio
import copy
import json
from dataclasses import dataclass
from typing import Any

import httpx
from fastapi import FastAPI

from app.providers.base import ChatRequest, ProviderMessage
from app.providers.ollama import Ollama
from app.runs.agent import Agent, Qualification
from app.runs.agent_tools import Handler, Tools
from app.runs.context import Context
from app.runs.manager import Run
from app.schemas import ModelInfo, Passage, ReasoningCaps, Source
from tests.test_chat import finish, start


def call(name: str, **arguments: Any) -> dict[str, Any]:
    return {"function": {"name": name, "arguments": arguments}}


def packets(text: str = "", calls: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    return [
        {"message": {"content": text, "tool_calls": calls or []}},
        {"done": True, "done_reason": "stop", "eval_count": 7, "prompt_eval_count": 90},
    ]


def source(url: str = "https://public.example.test/one", kind: str = "page") -> Source:
    return Source(
        n=999,
        url=url,
        title="Fake retained source",
        site_name="Fake",
        domain="example.test",
        fetched_at="2026-10-18",
        kind=kind,  # type: ignore[arg-type]
        document_id="fake-document" if kind == "document" else None,
        passages=[Passage(source_url=url, ord=0, text="The fake public label is Lantern.")],
    )


class Wire(httpx.AsyncByteStream):
    def __init__(self, backend: "Backend", chunks: list[dict[str, Any]]) -> None:
        self.backend, self.chunks = backend, chunks

    async def __aiter__(self) -> Any:
        for item in self.chunks:
            if item.get("pause"):
                self.backend.paused.set()
                await asyncio.Event().wait()
            yield (json.dumps(item) + "\n").encode()

    async def aclose(self) -> None:
        self.backend.closed += 1


class Backend:
    def __init__(self, turns: list[list[dict[str, Any]]]) -> None:
        self.turns = copy.deepcopy(turns)
        self.requests: list[dict[str, Any]] = []
        self.closed = 0
        self.paused = asyncio.Event()

    def handle(self, request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/version":
            return httpx.Response(200, json={"version": "fake-native-version"})
        assert request.url.path == "/api/chat"
        self.requests.append(json.loads(request.content))
        assert self.turns, "Unexpected extra model request"
        return httpx.Response(200, stream=Wire(self, self.turns.pop(0)))


@dataclass
class Rig:
    app: FastAPI
    run: Run
    adapter: Ollama
    backend: Backend
    model: ModelInfo
    request: ChatRequest
    context: Context

    def agent(
        self, handlers: dict[str, Handler] | None = None, kind: str = "web", **kwargs: Any
    ) -> Agent:
        return Agent(
            self.app.state.runs,
            self.adapter,
            self.model,
            Tools(kind, handlers or {}),  # type: ignore[arg-type]
            [Qualification("fake-digest", 32768, "fake-native-version", 1)],
            **kwargs,
        )

    async def execute(self, agent: Agent) -> Run:
        self.run.task = asyncio.create_task(
            agent(self.run, self.request, self.context, asyncio.Semaphore(1))
        )
        self.app.state.runs.runs[self.run.id] = self.run
        await self.run.task
        return self.run


async def rig(chat_app: Any, turns: list[list[dict[str, Any]]]) -> Rig:
    app, client, _ = chat_app
    previous = await finish(app, await start(client, "Fake native-loop task", "fake-chat"))
    message = previous.message.model_copy(deep=True)
    message.content, message.reasoning, message.stats, message.status = "", None, None, "streaming"
    run = Run("fake-agent-" + message.id, message)
    backend = Backend(turns)
    adapter = Ollama("fake", "http://fake", "47m")
    await adapter.client.aclose()
    adapter.client = httpx.AsyncClient(transport=httpx.MockTransport(backend.handle))
    model = ModelInfo(
        connection_id="fake",
        model_id="opaque-unrelated-id",
        display_name="Fake",
        digest="fake-digest",
        tools=True,
        context_length=32768,
        context_limit=32768,
        reasoning=ReasoningCaps(options=["off", "low", "medium", "xhigh"]),
    )
    app.state.registry.adapters["fake-agent-" + message.id] = adapter
    adapter.models[model.model_id] = model
    request = ChatRequest(
        model.model_id,
        [
            ProviderMessage("system", "Fake user instructions"),
            ProviderMessage("user", "Fake native-loop task"),
        ],
        context_length=32768,
    )
    context = Context(request.messages, 20, 0, 1024, 0.3)
    return Rig(app, run, adapter, backend, model, request, context)
