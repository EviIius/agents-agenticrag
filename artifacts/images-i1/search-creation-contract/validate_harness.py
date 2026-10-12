"""Exercise actual frozen capture/protocol functions with a rejecting transport."""

import asyncio
import hashlib
import importlib.util
import json
import sys
from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "server"), str(OUT)]
import contract  # noqa: E402
import httpx  # noqa: E402
from app.providers.base import ChatRequest, Finish, ProviderMessage, TextDelta, Usage  # noqa: E402
from app.providers.ollama import Ollama  # noqa: E402
from app.search import planner  # noqa: E402


async def exercise(
    source, helper, folder, candidate, missing_ref=False, rejected_social=False, creation=False
):
    calls = []
    material = contract.Material.create("synthetic", "literal", "bonjour", "0")

    async def activity():
        return None

    async def provider(adapter, request):
        calls.append(request.json_schema is not None)
        raw = {"task": "transform", "queries": [], "freshness": "any", "selection_condition": None}
        if candidate:
            raw["input_ref"] = (
                None if missing_ref or creation else {"ref": material.ref, "quote": "bonjour"}
            )
        if rejected_social:
            raw.update(task="conversation", input_ref=None)
        yield TextDelta(json.dumps(raw) if request.json_schema else "hello")
        yield Usage(10, 10)
        yield Finish("stop")

    namespace = {
        "activity": activity,
        "MODEL": "synthetic",
        "planner": planner,
        "original_stream": provider,
        "arm": "offline",
        "folder": folder,
        "asdict": asdict,
        "monotonic": monotonic,
        "json": json,
        "expected_schema": None,
    }
    exec(helper.extract_function(source, "captured_stream"), namespace)
    original_schema, original_stream, original_plan = planner.schema, Ollama.stream, planner.plan
    target_schema = contract.schema if candidate else original_schema

    def bound_schema(latest):
        namespace["expected_schema"] = target_schema(latest)
        return namespace["expected_schema"]

    def reject_network(request):
        raise AssertionError("Offline check attempted transport I/O")

    adapter = Ollama(
        "synthetic",
        "https://offline.invalid",
        client=httpx.AsyncClient(transport=httpx.MockTransport(reject_network)),
    )
    adapter.capacity = object()
    Ollama.stream = namespace["captured_stream"]
    planner.schema = bound_schema
    if candidate:
        planner.plan = contract.plan
    token = contract.MATERIALS.set(() if rejected_social or creation else (material,))
    try:
        result, fallback = await planner.plan(
            adapter,
            "synthetic",
            "What is the station's opening year?"
            if rejected_social
            else "Write a Python function that adds two numbers."
            if creation
            else "Translate bonjour into English.",
            [],
            True,
            16384,
        )
        assert result.search is rejected_social
        assert fallback is (missing_ref or rejected_social or creation) and calls == [True]
        request = ChatRequest("synthetic", [ProviderMessage("user", "hello")], {}, 16384)
        _ = [event async for event in adapter.stream(request)]
        with_error = ChatRequest("synthetic", request.messages, {"temperature": 0.9}, 16384)
        try:
            _ = [event async for event in adapter.stream(with_error)]
            raise RuntimeError("Invalid sampling escaped instrumentation")
        except AssertionError:
            pass
        assert calls == [True, False]
        traces = [json.loads(line) for line in (folder / "trace.jsonl").read_text().splitlines()]
        assert traces[-1]["error"] == "AssertionError"
        gate_namespace = {"json": json}
        exec(helper.extract_function(source, "protocol_verified"), gate_namespace)
        gate = gate_namespace["protocol_verified"]
        (folder / "wire.jsonl").write_text(
            "\n".join(json.dumps({"body": json.dumps(row["payload"])}) for row in traces[:2])
        )
        document = {"results": [{"turns": [{}]}]}
        assert not gate(folder, document)
        (folder / "trace.jsonl").write_text("\n".join(map(json.dumps, traces[:2])))
        assert gate(folder, document)
        (folder / "trace.jsonl").write_text(json.dumps(traces[1]))
        assert not gate(folder, document)
        return {
            "arm": "candidate" if candidate else "baseline",
            "native_ref_missing": missing_ref,
            "native_conversation_rejected": rejected_social,
            "native_transform_creation_admitted": creation,
            "fallback_used": fallback,
            "bound_schema_and_reference_accepted": True,
            "invalid_sampling_and_missing_planner_rejected": True,
            "synthetic_provider_calls": calls,
            "real_model_calls": 0,
        }
    finally:
        contract.MATERIALS.reset(token)
        planner.schema, Ollama.stream, planner.plan = (
            original_schema,
            original_stream,
            original_plan,
        )
        await adapter.close()


def main():
    spec = importlib.util.spec_from_file_location(
        "old_verifier", OUT.parent / "search-repair/verify_harness.py"
    )
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    source = (OUT / "experiment.py").read_text()
    rows = []
    with TemporaryDirectory() as temporary:
        for candidate in (False, True):
            folder = Path(temporary) / str(candidate)
            folder.mkdir()
            rows.append(asyncio.run(exercise(source, helper, folder, candidate)))
        folder = Path(temporary) / "candidate-null-ref"
        folder.mkdir()
        rows.append(asyncio.run(exercise(source, helper, folder, True, missing_ref=True)))
        folder = Path(temporary) / "candidate-rejected-conversation"
        folder.mkdir()
        rows.append(asyncio.run(exercise(source, helper, folder, True, rejected_social=True)))
        folder = Path(temporary) / "candidate-new-code"
        folder.mkdir()
        rows.append(asyncio.run(exercise(source, helper, folder, True, creation=True)))
    (OUT / "offline-harness.json").write_text(
        json.dumps(
            {
                "passed": True,
                "harness_sha256": hashlib.sha256(source.encode()).hexdigest(),
                "arms": rows,
            },
            indent=2,
        )
        + "\n"
    )
    print(
        "Actual baseline/four-candidate capture/schema/reference/protocol checks passed; "
        "rejecting transport, no inference."
    )


if __name__ == "__main__":
    main()
