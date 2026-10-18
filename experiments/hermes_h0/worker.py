"""Supervised Hermes library probe; no direct runtime, cloud or user-data access."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

from protocol import TOOL_NAMES, FixtureTools, GateFailure


def main() -> None:
    settings = json.loads(Path(sys.argv[1]).read_text())
    trial = Path(settings["trial_dir"]).resolve()
    source = Path(settings["source_dir"]).resolve()
    model = settings["model"]
    started = time.monotonic()
    events = trial / "worker-events.jsonl"

    def emit(kind: str, **data) -> None:
        with events.open("a") as handle:
            handle.write(
                json.dumps({"kind": kind, "seconds": time.monotonic() - started, **data}) + "\n"
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

    def within(path, roots) -> bool:
        if isinstance(path, int):
            return True
        resolved = Path(os.fsdecode(path)).resolve()
        return any(resolved == root or resolved.is_relative_to(root) for root in roots)

    def audit(event, args) -> None:
        if event == "socket.connect":
            address = args[1]
            if not (isinstance(address, tuple) and address[:2] == ("127.0.0.1", settings["port"])):
                emit("blocked", category="network")
                raise PermissionError("Only the host-controlled trial proxy is reachable")
        elif event in {"os.system", "os.exec", "os.posix_spawn", "subprocess.Popen"}:
            emit("blocked", category="process")
            raise PermissionError("Hermes cannot launch child processes in H0")
        elif event == "open":
            path, mode, flags = args
            writing = (isinstance(mode, str) and any(value in mode for value in "wax+")) or (
                isinstance(flags, int)
                and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC)
            )
            if not within(path, [trial] if writing else read_roots):
                emit("blocked", category="file_write" if writing else "file_read")
                raise PermissionError("File access is outside the isolated trial roots")

    sys.addaudithook(audit)
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
            result = tools.call(_name, args)
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
        max_iterations=3,
        run_budget_seconds=180,
        quiet_mode=True,
        save_trajectories=False,
        skip_context_files=True,
        skip_memory=True,
        skip_background_review=True,
        load_soul_identity=False,
        checkpoints_enabled=False,
        max_tokens=None,
        reasoning_config=None,
        platform="h0_isolated",
        cwd=str(trial),
        stream_delta_callback=lambda *a, **k: emit("stream_delta", arguments=a, values=k),
        event_callback=lambda *a, **k: emit("hermes_event", arguments=a, values=k),
        status_callback=lambda *a, **k: emit("status", arguments=a, values=k),
    )
    names = sorted(tool["function"]["name"] for tool in agent.tools)
    emit("initialized", tools=names, max_iterations=agent.max_iterations)
    if set(names) != TOOL_NAMES:
        raise GateFailure("Hermes effective tool set does not match the host allowlist")
    result = agent.run_conversation(
        user_message=settings["question"],
        system_message=settings["system_prompt"],
        task_id="h0-structural",
    )
    emit("result", result=result)
    (trial / "worker-result.json").write_text(json.dumps(result, default=str, indent=2) + "\n")
    agent.close()
    emit("closed")


if __name__ == "__main__":
    main()
