"""Supervised Hermes library probe; no direct runtime, cloud or user-data access."""

from __future__ import annotations

import json
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hermes_h0"))

from policy import AuditPolicy  # noqa: E402
from protocol import TOOL_NAMES, FixtureTools, GateFailure  # noqa: E402


def main() -> None:
    settings = json.loads(Path(sys.argv[1]).read_text())
    trial = Path(settings["trial_dir"]).resolve()
    source = Path(settings["source_dir"]).resolve()
    model = settings["model"]
    started = time.monotonic()
    events = trial / "worker-events.jsonl"
    event_lock = threading.RLock()
    sequence = 0

    def emit(kind: str, **data) -> None:
        nonlocal sequence
        with event_lock, events.open("a") as handle:
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

    # Audit enforcement is a qualification control, not a general-purpose OS sandbox.
    read_roots = [
        source,
        trial,
        Path(__file__).resolve().parent,
        Path(sys.prefix).resolve(),
        Path(sys.base_prefix).resolve(),
        Path("/System"),
        Path("/usr"),
        Path("/Library/Developer"),
        Path("/private/etc"),
        Path("/private/var/db"),
        Path("/dev"),
    ]

    read_roots.append(Path(__file__).resolve().parent.parent / "hermes_h0")
    sys.addaudithook(AuditPolicy(trial, source, read_roots, settings["port"], emit))
    sys.path.insert(0, str(source))
    emit("import_started")
    from run_agent import AIAgent
    from tools.registry import registry
    from toolsets import create_custom_toolset

    emit("import_complete")
    tools = FixtureTools(settings["sources"])
    definitions = {
        "web_search": ("Search the retained synthetic web records.", {"query": {"type": "string"}}),
        "read_page": ("Read a retained source by its ID.", {"source_id": {"type": "string"}}),
        "library_search": ("Search the synthetic Library.", {"query": {"type": "string"}}),
        "calculator": ("Calculate bounded arithmetic.", {"expression": {"type": "string"}}),
    }
    for name, (description, properties) in definitions.items():

        def handler(args, _name=name, **kwargs):
            try:
                result = tools.call(_name, args)
            except Exception:
                emit("tool_rejected", tool=_name)
                raise
            emit("tool_result", tool=_name, arguments=args, result=result)
            return json.dumps(result)

        registry.register(
            name=name,
            toolset="h0_fixture",
            override=True,
            handler=handler,
            schema={
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": list(properties),
                    "additionalProperties": False,
                },
            },
        )
    create_custom_toolset("h0_fixture", "Isolated H0 fixture adapters", tools=sorted(TOOL_NAMES))
    agent = AIAgent(
        model=model,
        base_url=f"http://127.0.0.1:{settings['port']}/v1",
        api_key="synthetic-host-only",
        provider="custom",
        api_mode="chat_completions",
        enabled_toolsets=["h0_fixture"],
        max_iterations=settings.get("max_iterations", 3),
        run_budget_seconds=180,
        quiet_mode=True,
        save_trajectories=False,
        skip_context_files=True,
        skip_memory=True,
        skip_background_review=True,
        load_soul_identity=False,
        checkpoints_enabled=False,
        max_tokens=None,
        # None selects Hermes' own medium default. Empty preserves the runtime default.
        reasoning_config={},
        platform="h0_isolated",
        cwd=str(trial),
        stream_delta_callback=lambda *a, **k: emit("stream_delta", arguments=a, values=k),
        event_callback=lambda *a, **k: emit("hermes_event", arguments=a, values=k),
        status_callback=lambda *a, **k: emit("status", arguments=a, values=k),
    )
    names = sorted(tool["function"]["name"] for tool in agent.tools)
    emit(
        "initialized", tools=names, max_iterations=agent.max_iterations, session_id=agent.session_id
    )
    if set(names) != TOOL_NAMES:
        raise GateFailure("Hermes effective tool set does not match the host allowlist")
    emit("conversation_started")
    result = agent.run_conversation(
        user_message=settings["question"],
        system_message=settings["system_prompt"],
        task_id=settings.get("task_id", "h0-structural"),
    )
    emit("result", result=result)
    (trial / "worker-result.json").write_text(json.dumps(result, default=str, indent=2) + "\n")
    agent.close()
    emit("closed")


if __name__ == "__main__":
    main()
