import asyncio
import base64
import json
import re
from collections.abc import AsyncGenerator
from time import monotonic
from typing import Any

import httpx

from ..errors import AppError
from ..schemas import ModelInfo, ReasoningCaps
from .base import (
    ChatRequest,
    Finish,
    ProviderEvent,
    ReasoningDelta,
    TextDelta,
    Timing,
    ToolCall,
    Usage,
)
from .thinktags import ThinkSplitter


def runtime_error(status: int, detail: str) -> AppError:
    code = "provider_error"
    if status == 404 or "not found" in detail.lower():
        code = "model_not_found"
    elif re.search(r"memory|insufficient|failed to load", detail, re.I):
        code = "model_load_failed"
    elif re.search(r"context|too long|exceeds", detail, re.I):
        code = "context_overflow"
    return AppError(code, detail[:300], 502)


class Ollama:
    def __init__(
        self,
        connection_id: str,
        base_url: str,
        keep_alive: str = "30m",
        client: httpx.AsyncClient | None = None,
        idle_timeout: float = 60,
    ) -> None:
        self.connection_id = connection_id
        self.base_url = base_url.rstrip("/")
        self.keep_alive = keep_alive
        self.client = client or httpx.AsyncClient(
            timeout=httpx.Timeout(300, connect=5), trust_env=False
        )
        self.shows: dict[str, tuple[float, dict[str, Any]]] = {}
        self.idle_timeout = idle_timeout
        self.models: dict[str, ModelInfo] = {}

    async def close(self) -> None:
        await self.client.aclose()

    async def json(
        self, method: str, path: str, body: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        try:
            response = await self.client.request(method, self.base_url + path, json=body)
        except httpx.RequestError as exc:
            raise AppError("runtime_unreachable", "Cannot reach Ollama.", 502) from exc
        if response.is_error:
            raise runtime_error(response.status_code, response.text)
        return dict(response.json())

    async def list_models(self) -> list[ModelInfo]:
        tags = await self.json("GET", "/api/tags")
        ps = await self.json("GET", "/api/ps")
        loaded = {m["name"]: m for m in ps.get("models", [])}
        out = []
        for tag in tags.get("models", []):
            name = tag["name"]
            cached = self.shows.get(name)
            if cached and monotonic() - cached[0] < 600:
                show = cached[1]
            else:
                show = await self.json("POST", "/api/show", {"model": name})
                self.shows[name] = (monotonic(), show)
            caps = show.get("capabilities", [])
            details = show.get("details", tag.get("details", {}))
            info = show.get("model_info", {})
            maximum = info.get(f"{info.get('general.architecture')}.context_length")
            context = loaded.get(name, {}).get("context_length")
            param = re.search(r"^num_ctx\s+(\d+)", show.get("parameters", ""), re.M)
            # Operational ceiling comes from runtime configuration, not model names.
            configured = int(param[1]) if param else min(maximum or 8192, 16384)
            limit = min(configured, maximum) if maximum else configured
            context = min(context or limit, limit)
            reasoning = None
            thinking = show.get("thinking")
            if thinking:

                def convert(value: Any) -> str:
                    return "on" if value is True else "off" if value is False else str(value)

                options = [convert(v) for v in thinking.get("values", [])]
                if options != ["off"] and options:
                    reasoning = ReasoningCaps(
                        options=options, default=convert(thinking.get("default"))
                    )
            elif "thinking" in caps:
                reasoning = ReasoningCaps(options=["off", "on"])
            out.append(
                ModelInfo(
                    connection_id=self.connection_id,
                    model_id=name,
                    display_name=name,
                    digest=tag.get("digest"),
                    family=details.get("family"),
                    params=details.get("parameter_size"),
                    quant=details.get("quantization_level"),
                    size_bytes=tag.get("size"),
                    context_max=maximum,
                    context_limit=limit,
                    context_length=context,
                    vision="vision" in caps,
                    tools="tools" in caps,
                    embedding="embedding" in caps,
                    reasoning=reasoning,
                    loaded=name in loaded,
                    loaded_bytes=loaded.get(name, {}).get("size_vram"),
                    chat_capable="completion" in caps,
                )
            )
        self.models = {m.model_id: m for m in out}
        return out

    def payload(self, req: ChatRequest) -> dict[str, Any]:
        options = {
            ("num_predict" if k == "max_tokens" else k): v
            for k, v in req.params.items()
            if k in {"temperature", "top_p", "top_k", "max_tokens", "seed"} and v is not None
        }
        if req.context_length:
            options["num_ctx"] = req.context_length
        messages: list[dict[str, Any]] = []
        for m in req.messages:
            entry: dict[str, Any] = {"role": m.role, "content": m.content}
            if m.images:
                entry["images"] = [base64.b64encode(i).decode() for i in m.images]
            if m.tool_calls is not None:
                entry["tool_calls"] = m.tool_calls
            if m.tool_name is not None:
                entry["tool_name"] = m.tool_name
            messages.append(entry)
        payload: dict[str, Any] = {
            "model": req.model_id,
            "messages": messages,
            "stream": True,
            "keep_alive": self.keep_alive,
        }
        if options:
            payload["options"] = options
        model = self.models.get(req.model_id)
        if req.reasoning is not None and model and model.reasoning:
            choice = (
                req.reasoning
                if req.reasoning in model.reasoning.options
                else model.reasoning.options[0]
            )
            payload["think"] = {"off": False, "on": True}.get(choice, choice)
        if req.json_schema:
            payload["format"] = req.json_schema
        if req.tools is not None:
            payload["tools"] = req.tools
        return payload

    async def load(self, model_id: str, context_length: int | None) -> None:
        payload: dict[str, Any] = {
            "model": model_id,
            "messages": [],
            "keep_alive": self.keep_alive,
            "stream": False,
        }
        if context_length:
            payload["options"] = {"num_ctx": context_length}
        await self.json("POST", "/api/chat", payload)

    async def unload(self, model_id: str) -> None:
        await self.json(
            "POST",
            "/api/chat",
            {"model": model_id, "messages": [], "keep_alive": 0, "stream": False},
        )

    async def stream(self, req: ChatRequest) -> AsyncGenerator[ProviderEvent, None]:
        splitter = ThinkSplitter()
        native = False
        call_number = 0
        try:
            async with self.client.stream(
                "POST", self.base_url + "/api/chat", json=self.payload(req)
            ) as response:
                if response.is_error:
                    await response.aread()
                    raise runtime_error(response.status_code, response.text)
                lines = response.aiter_lines().__aiter__()
                first = True
                while True:
                    try:
                        async with asyncio.timeout(300 if first else self.idle_timeout):
                            line = await anext(lines)
                        first = False
                    except StopAsyncIteration:
                        break
                    if not line:
                        continue
                    chunk = json.loads(line)
                    if chunk.get("error"):
                        raise runtime_error(500, str(chunk["error"]))
                    message = chunk.get("message", {})
                    if req.tools is not None:
                        for call in message.get("tool_calls", []):
                            function = call.get("function", {})
                            arguments = function.get("arguments")
                            yield ToolCall(
                                str(call.get("id") or f"call-{call_number}"),
                                function.get("name")
                                if isinstance(function.get("name"), str)
                                else "",
                                arguments if isinstance(arguments, str) else json.dumps(arguments),
                            )
                            call_number += 1
                    if "thinking" in message:
                        native = True
                        for event in splitter.end():
                            yield event
                        if message["thinking"]:
                            yield ReasoningDelta(message["thinking"])
                    text = message.get("content", "")
                    if text:
                        if native:
                            yield TextDelta(text)
                        else:
                            for event in splitter.feed(text):
                                yield event
                    if chunk.get("done"):
                        for event in splitter.end():
                            yield event
                        if "eval_count" in chunk:
                            yield Usage(chunk.get("prompt_eval_count", 0), chunk["eval_count"])
                            yield Timing(
                                chunk.get("load_duration", 0) / 1e6,
                                chunk.get("prompt_eval_duration", 0) / 1e6,
                                chunk.get("eval_duration", 0) / 1e6,
                            )
                        yield Finish("length" if chunk.get("done_reason") == "length" else "stop")
                        return
                for event in splitter.end():
                    yield event
                yield Finish("error", "provider_error")
        except (TimeoutError, httpx.ReadTimeout):
            yield Finish("error", "idle_timeout")
        except httpx.RequestError:
            yield Finish("error", "runtime_unreachable")
        except AppError as exc:
            yield Finish("error", exc.code + ":" + exc.message)
        except (ValueError, KeyError, TypeError, AttributeError):
            yield Finish("error", "provider_error:Invalid Ollama response")

    async def complete_json(self, req: ChatRequest) -> dict[str, Any]:
        text = ""
        async for event in self.stream(req):
            if isinstance(event, TextDelta):
                text += event.text
            elif isinstance(event, Finish) and event.reason == "error":
                raise AppError("provider_error", event.detail or "Utility request failed", 502)
        return dict(json.loads(text.strip().removeprefix("```json").removesuffix("```")))

    async def embed(self, model_id: str, texts: list[str]) -> list[list[float]]:
        result = await self.json("POST", "/api/embed", {"model": model_id, "input": texts})
        return [[float(v) for v in vector] for vector in result["embeddings"]]
