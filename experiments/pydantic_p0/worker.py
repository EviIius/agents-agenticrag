"""Isolated PydanticAI runner; all inference and tools pass through the host gate."""

from __future__ import annotations

import asyncio
import dataclasses
import json
import sys
import threading
import time
import uuid
from pathlib import Path

from policy import AuditPolicy

sys.path.append(str(Path(__file__).resolve().parent.parent / "hermes_h0"))
from protocol import TOOL_NAMES, FixtureTools, GateFailure  # noqa: E402


def main():
    settings = json.loads(Path(sys.argv[1]).read_text())
    trial = Path(settings["trial_dir"]).resolve()
    started = time.monotonic()
    event_lock = threading.RLock()
    sequence = 0

    def emit(kind, **data):
        nonlocal sequence
        with event_lock, (trial / "worker-events.jsonl").open("a") as handle:
            sequence += 1
            handle.write(
                json.dumps(
                    {
                        "sequence": sequence,
                        "kind": kind,
                        "seconds": time.monotonic() - started,
                        **data,
                    },
                    default=str,
                )
                + "\n"
            )

    source = Path(sys.prefix) / "lib/python3.14/site-packages/pydantic_ai"
    read_roots = [
        trial,
        Path(__file__).resolve().parent,
        Path(__file__).resolve().parent.parent / "hermes_h0",
        Path(sys.prefix).resolve(),
        Path(sys.base_prefix).resolve(),
        Path("/System"),
        Path("/usr"),
        Path("/Library/Developer"),
        Path("/private/etc"),
        Path("/private/var/db"),
        Path("/dev"),
    ]
    sys.addaudithook(AuditPolicy(trial, source, read_roots, settings["port"], emit))
    emit("import_started")
    from openai import AsyncOpenAI
    from pydantic_ai import Agent, AgentRunResultEvent, Tool
    from pydantic_ai.messages import PartDeltaEvent, PartStartEvent, TextPart, TextPartDelta
    from pydantic_ai.models.ollama import OllamaModel
    from pydantic_ai.profiles.openai import OpenAIModelProfile
    from pydantic_ai.providers.ollama import OllamaProvider
    from pydantic_ai.usage import UsageLimits

    emit("import_complete")
    fixtures = FixtureTools(settings["sources"])

    def call(name, arguments):
        try:
            result = fixtures.call(name, arguments)
        except Exception:
            emit("tool_rejected", tool=name)
            raise
        emit("tool_result", tool=name, arguments=arguments, result=result)
        return result

    def web_search(query: str):
        return call("web_search", {"query": query})

    def library_search(query: str):
        return call("library_search", {"query": query})

    def read_page(source_id: str):
        return call("read_page", {"source_id": source_id})

    def calculator(expression: str):
        return call("calculator", {"expression": expression})

    functions = [
        (web_search, "Search the retained synthetic web records."),
        (read_page, "Read a retained source by its ID."),
        (library_search, "Search the synthetic Library."),
        (calculator, "Calculate bounded arithmetic."),
    ]
    tools = [
        Tool(fn, description=description, max_retries=0, strict=False)
        for fn, description in functions
    ]
    names = sorted(tool.name for tool in tools)
    if set(names) != TOOL_NAMES:
        raise GateFailure("Effective tool set differs from host allowlist")

    async def run():
        # Explicit protocol profile: never infer capabilities from a model name.
        # Tool support was observed through Ollama metadata and the previous H0 call.
        profile = OpenAIModelProfile(
            supports_tools=True,
            supports_json_schema_output=False,
            supports_json_object_output=False,
            openai_supports_strict_tool_definition=False,
            openai_chat_thinking_field="reasoning",
            openai_chat_streaming_requires_finish_reason=True,
        )
        async with AsyncOpenAI(
            base_url=f"http://127.0.0.1:{settings['port']}/v1",
            api_key="synthetic-host-only",
            max_retries=0,
            timeout=180,
        ) as client:
            model = OllamaModel(
                settings["model"],
                provider=OllamaProvider(openai_client=client),
                profile=profile,
                settings={"extra_body": {"options": {"num_ctx": 65536}}},
            )
            agent = Agent(
                model,
                system_prompt=settings["system_prompt"],
                output_type=str,
                tools=tools,
                retries=0,
                name="p0_candidate",
            )
            emit("initialized", tools=names, max_iterations=3, session_id=str(uuid.uuid4()))
            final = None
            async with agent.run_stream_events(
                settings["question"], usage_limits=UsageLimits(request_limit=3)
            ) as stream:
                async for event in stream:
                    emit("agent_event", event_type=type(event).__name__)
                    if isinstance(event, PartStartEvent) and isinstance(event.part, TextPart):
                        emit("stream_delta", text=event.part.content)
                    elif isinstance(event, PartDeltaEvent) and isinstance(
                        event.delta, TextPartDelta
                    ):
                        emit("stream_delta", text=event.delta.content_delta)
                    elif isinstance(event, AgentRunResultEvent):
                        final = {
                            "final_response": event.result.output,
                            "usage": dataclasses.asdict(event.result.usage()),
                            "messages": json.loads(event.result.all_messages_json()),
                        }
            if final is None:
                raise GateFailure("No completed result event")
            emit("result", result=final)
            (trial / "worker-result.json").write_text(
                json.dumps(final, indent=2, default=str) + "\n"
            )
        emit("closed")

    asyncio.run(run())


if __name__ == "__main__":
    main()
