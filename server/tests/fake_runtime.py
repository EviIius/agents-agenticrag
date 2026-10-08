"""Scripted test runtime. All model IDs and responses explicitly identify the fake."""

import asyncio
import hashlib
import json
import re
import time
from collections.abc import AsyncIterator
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

MODELS = ["fake-chat", "fake-reasoning", "fake-vision", "fake-embedding", "fake-embedding-alt"]
MARKDOWN = (
    "Fake runtime reply.\n\n- A clear first step\n- A useful second step\n\n"
    "```python\nprint('Hello')\n```\n\n"
    "| Item | Value |\n| --- | --- |\n| Example | 42 |"
)


def create_fake_runtime() -> FastAPI:
    app = FastAPI(title="Fake runtime")
    app.state.captures = []
    app.state.tool_support = False
    app.state.tool_script = None
    app.state.tool_delay = 0.0
    app.state.disconnected = 0
    app.state.first_tokens = []
    app.state.loaded = {"fake-chat": 16384}

    @app.get("/api/tags")
    async def tags() -> dict[str, Any]:
        return {
            "models": [
                {
                    "name": model,
                    "model": model,
                    "size": 1024,
                    "digest": "synthetic-fake-digest",
                    "details": {"parameter_size": "1B", "quantization_level": "F16"},
                }
                for model in MODELS
            ]
        }

    @app.post("/api/show")
    async def show(request: Request) -> dict[str, Any]:
        body = await request.json()
        app.state.captures.append(body)
        model = body.get("model", "fake-chat")
        context = 32768 if model == "fake-vision" else 16384
        return {
            "capabilities": (
                ["embedding"]
                if model in ("fake-embedding", "fake-embedding-alt")
                else ["completion"]
            )
            + (["tools"] if app.state.tool_support else [])
            + (["thinking"] if model == "fake-reasoning" else [])
            + (["vision"] if model == "fake-vision" else []),
            "model_info": {"general.architecture": "fake", "fake.context_length": context},
            "parameters": f"num_ctx {context}",
        }

    @app.post("/api/embed", response_model=None)
    async def embed(request: Request) -> dict[str, Any] | JSONResponse:
        body = await request.json()
        app.state.captures.append(body)
        await asyncio.sleep(0.025)
        if body.get("model") not in ("fake-embedding", "fake-embedding-alt"):
            return JSONResponse({"error": "Fake embedding model unavailable"}, status_code=404)
        dimension = 16 if body["model"] == "fake-embedding-alt" else 8
        return {
            "embeddings": [
                [float(v + 1) / 256 for v in hashlib.sha256(text.encode()).digest()[:dimension]]
                for text in body["input"]
            ]
        }

    @app.get("/api/version")
    async def version() -> dict[str, str]:
        return {"version": "synthetic-fake-version"}

    @app.get("/api/ps")
    async def ps() -> dict[str, Any]:
        return {
            "models": [
                {"name": model, "size_vram": 1024, "context_length": context}
                for model, context in app.state.loaded.items()
            ]
        }

    @app.get("/tests/state")
    async def state() -> dict[str, Any]:
        return {
            "captures": app.state.captures,
            "disconnected": app.state.disconnected,
            "first_tokens": app.state.first_tokens,
        }

    @app.get("/v1/models")
    async def models() -> dict[str, Any]:
        return {
            "object": "list",
            "data": [
                {"id": model, "object": "model", "owned_by": "Fake runtime"} for model in MODELS
            ],
        }

    async def chat(request: Request, ollama: bool) -> JSONResponse | StreamingResponse:
        body = await request.json()
        app.state.captures.append(body)
        messages = body.get("messages", [])
        last = next(
            (
                message.get("content", "")
                for message in reversed(messages)
                if message.get("role") == "user"
            ),
            "",
        )
        prompt = last if isinstance(last, str) else json.dumps(last)
        error = re.match(r"#error:(\d+)", prompt)
        if error:
            return JSONResponse({"error": "Fake runtime scripted error"}, status_code=int(error[1]))
        if ollama and not messages:
            if body.get("keep_alive") == 0:
                app.state.loaded.pop(body.get("model"), None)
            else:
                app.state.loaded[body.get("model")] = body.get("options", {}).get("num_ctx", 16384)
            return JSONResponse({"done": True, "message": {"content": ""}})
        if body.get("model", "fake-chat") not in MODELS:
            return JSONResponse({"error": "model not found"}, status_code=404)
        if ollama:
            app.state.loaded[body.get("model")] = body.get("options", {}).get("num_ctx", 16384)
        if ollama and body.get("tools"):
            lines = [line for line in prompt.splitlines() if line.startswith("#tool:")]
            script = app.state.tool_script
            if script is None:
                script = []
                for line in lines:
                    name, _, args = line.removeprefix("#tool:").partition(":")
                    script.append([{"function": {"name": name, "arguments": json.loads(args)}}])
            step = sum(message.get("tool_calls") is not None for message in messages)
            calls = script[step] if step < len(script) else []

            async def tools_stream() -> AsyncIterator[str]:
                try:
                    await asyncio.sleep(app.state.tool_delay)
                    yield (
                        json.dumps(
                            {
                                "message": {
                                    "role": "assistant",
                                    "content": "Fake loop note.",
                                    "tool_calls": calls,
                                },
                                "done": False,
                            }
                        )
                        + "\n"
                    )
                    yield (
                        json.dumps({"message": {"role": "assistant", "content": ""}, "done": True})
                        + "\n"
                    )
                finally:
                    app.state.disconnected += 1

            return StreamingResponse(tools_stream(), media_type="application/x-ndjson")
        text = MARKDOWN
        cleanup_call = prompt.startswith("You are formatting a speech transcript.")
        if cleanup_call:
            source = prompt.split("<chunk>\n", 1)[-1].rsplit("\n</chunk>", 1)[0]
            text = (
                "A synthetic rewritten summary with substantially different wording."
                if "FAKE-REWRITE" in source
                else source[:1].upper()
                + source[1:]
                + ("" if source.endswith((".", "!", "?")) else ".")
            )
        if isinstance(body.get("format"), dict):
            latest = prompt.split("Latest user message:\n")[-1]
            search = latest.strip().lower() not in {"thanks!", "hello", "rewrite shorter"}
            decision = (
                {"task": "lookup" if search else "conversation"}
                if "task" in body["format"].get("properties", {})
                else {"search": search}
            )
            text = json.dumps(
                {**decision, "queries": [latest[:120]] if search else [], "freshness": "any"}
            )
            if "rows" in body["format"].get("properties", {}):
                definitions = body["format"]["$defs"]
                key = definitions["evidence"]["items"]["enum"][0]
                # Synthetic output follows the advertised evidence IDs. Ordinary
                # planner/title JSON behavior above stays unchanged.
                text = json.dumps(
                    {
                        "rows": [
                            {
                                "label": label,
                                "kind": "excerpt",
                                "value": "",
                                "evidence": [key],
                            }
                            for label in definitions["label"]["enum"]
                        ]
                    }
                )
                scripted_answer = getattr(app.state, "evidence_answer", None)
                if scripted_answer is not None:
                    text = json.dumps(scripted_answer)
        elif "<library_results>" in prompt:
            numbers = re.findall(r'<source id="(\d+)"', prompt)
            first = re.search(
                r'<source id="1"[^>]*>\nCitation label: \[1\]\n\n(.*?)</source>', prompt, re.S
            )
            passage = first[1].strip() if first else "Invented lanterns are blue."
            passage = re.sub(r"^Section: [^\n]*\n", "", passage).split("\n\n", 1)[0]
            text = (
                "Synthetic Library answer: "
                + passage
                + " "
                + "".join(f"[{n}]" for n in numbers[:2])
                + "."
            )
            if "#uncited" in prompt:
                text = "Synthetic Library answer without citations."
        elif "<search_results" in prompt and "#uncited" in prompt:
            text = MARKDOWN
        elif "<search_results" in prompt:
            text = "Synthetic web answer: Milwaukee Bucks defeated Phoenix Suns 4–2 in 2021 [1][2]."
        elif prompt.startswith("#planner:"):
            text = prompt.removeprefix("#planner:")
        elif prompt.startswith("#cite"):
            text = "Fake citations [1][2], 【3†L1】, [4, 5], and [9]."
        elif prompt.startswith("#image?"):
            has_image = any(
                message.get("images")
                or (
                    isinstance(message.get("content"), list)
                    and any(part.get("type") == "image_url" for part in message["content"])
                )
                for message in messages
            )
            text = f"Fake runtime received an image: {has_image}"
        long = re.search(r"#long:(\d+)", prompt)
        if long:
            text = " ".join(f"token{index}" for index in range(min(int(long[1]), 10000)))
        slow = re.search(r"#slow:(\d+)", prompt)
        delay = 1 / max(int(slow[1]), 1) if slow else 0.005
        stall = re.search(r"#stall:(\d+)", prompt)
        reason = prompt.startswith("#think")
        finish = "length" if prompt.startswith("#length") else "stop"
        if not body.get("stream", True):
            if ollama:
                return JSONResponse(
                    {
                        "model": body.get("model", "fake-chat"),
                        "message": {"role": "assistant", "content": text},
                        "done": True,
                        "done_reason": finish,
                    }
                )
            return JSONResponse(
                {
                    "choices": [
                        {"message": {"role": "assistant", "content": text}, "finish_reason": finish}
                    ]
                }
            )

        async def stream() -> AsyncIterator[str]:
            completed = False
            model = body.get("model", "fake-chat")

            def packet(delta: dict[str, str], done: bool = False) -> str:
                if ollama:
                    message = {"role": "assistant", **delta}
                    payload: dict[str, Any] = {"model": model, "message": message, "done": done}
                    if done:
                        payload.update(
                            done_reason=finish,
                            eval_count=len(text.split()),
                            eval_duration=1000000000,
                            prompt_eval_count=10,
                        )
                    return json.dumps(payload) + "\n"
                payload = {
                    "id": "fake-run",
                    "object": "chat.completion.chunk",
                    "model": model,
                    "choices": [
                        {"index": 0, "delta": delta, "finish_reason": finish if done else None}
                    ],
                }
                if done:
                    payload["usage"] = {"prompt_tokens": 10, "completion_tokens": len(text.split())}
                return "data: " + json.dumps(payload) + "\n\n"

            try:
                if reason:
                    if ollama:
                        yield packet({"thinking": "Fake reasoning, separated from the answer."})
                    else:
                        yield packet(
                            {"content": "<think>Fake reasoning, separated from the answer.</think>"}
                        )
                pieces = re.findall(r"\S+\s*|\s+", text)
                for index, piece in enumerate(pieces):
                    if await request.is_disconnected():
                        return
                    if stall and index == len(pieces) // 2:
                        await asyncio.sleep(min(int(stall[1]), 120))
                    if prompt.startswith("#error:stream") and index == 3:
                        yield (
                            ("" if ollama else "data: ")
                            + json.dumps({"error": "Fake mid-stream error"})
                            + ("\n" if ollama else "\n\n")
                        )
                        return
                    if index == 0:
                        app.state.first_tokens.append(
                            {"prompt": prompt, "at_ms": time.time() * 1000}
                        )
                    yield packet({"content": piece})
                    await asyncio.sleep(delay)
                yield packet({}, True)
                if not ollama:
                    yield "data: [DONE]\n\n"
                completed = True
            finally:
                if not completed:
                    app.state.disconnected += 1

        return StreamingResponse(
            stream(), media_type="application/x-ndjson" if ollama else "text/event-stream"
        )

    @app.post("/api/chat", response_model=None)
    async def ollama_chat(request: Request) -> JSONResponse | StreamingResponse:
        return await chat(request, True)

    @app.post("/v1/chat/completions", response_model=None)
    async def openai_chat(request: Request) -> JSONResponse | StreamingResponse:
        return await chat(request, False)

    return app


app = create_fake_runtime()
