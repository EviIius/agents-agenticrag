"""Offline reproduction and a proposed harness-only patch; no inference/network."""

import ast
import asyncio
import difflib
import hashlib
import json
import sys
from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "server")]

from app.providers.base import ChatRequest, Finish, ProviderMessage, TextDelta, Usage  # noqa: E402
from app.providers.ollama import Ollama  # noqa: E402
from app.search import planner  # noqa: E402


def replacement(source, before, after):
    assert source.count(before) == 1
    return source.replace(before, after)


def proposed_patch(source):
    revised = replacement(
        source,
        "    selected = None\n",
        """    original_schema = planner.schema
    expected_schema = None

    def bound_schema(latest):
        nonlocal expected_schema
        expected_schema = original_schema(latest)
        return expected_schema

    planner.schema = bound_schema  # Observe the unchanged request-specific schema.
    selected = None
""",
    )
    revised = replacement(
        revised,
        """        assert self.capacity is not None
        assert request.model_id == MODEL and request.context_length == 16384
        assert request.json_schema is None or request.json_schema == planner.SCHEMA
        if request.json_schema:
            assert request.params == {"temperature": 0.2, "max_tokens": 256}
        else:
            assert request.params == {}
        assert "tools" not in self.payload(request)
        entry = {""",
        """        entry = {""",
    )
    revised = replacement(
        revised,
        """        stream = original_stream(self, request)
        try:
            async for event in stream:""",
        """        stream = None
        try:
            assert self.capacity is not None
            assert request.model_id == MODEL and request.context_length == 16384
            if request.json_schema is not None:
                assert expected_schema is not None and request.json_schema == expected_schema
                assert request.params == {"temperature": 0.2, "max_tokens": 256}
            else:
                assert request.params == {}
            assert "tools" not in entry["payload"]
            stream = original_stream(self, request)
            async for event in stream:""",
    )
    revised = replacement(
        revised,
        "            await stream.aclose()\n",
        "            if stream is not None:\n                await stream.aclose()\n",
    )
    revised = replacement(
        revised,
        "def g9(candidate, baseline):\n",
        '''def protocol_verified(folder, document):
    """A swallowed instrumentation error must stop before interpreting scores."""
    traces = [json.loads(line) for line in (folder / "trace.jsonl").read_text().splitlines()]
    wires = [json.loads(json.loads(line)["body"])
             for line in (folder / "wire.jsonl").read_text().splitlines()]
    turns = sum(len(result["turns"]) for result in document["results"])
    planners = [row for row in traces if row["payload"].get("format") is not None]
    answers = [row for row in traces if row["payload"].get("format") is None]
    return (
        len(planners) == len(answers) == turns
        and sum(row.get("format") is not None for row in wires) == turns
        and sum(row.get("stream") is True and row.get("format") is None for row in wires) == turns
        and all(row["error"] is None and row["capacity_enabled"]
                and any(event["type"] == "Usage" for event in row["events"])
                and any(event["type"] == "Finish"
                        and event["value"]["reason"] != "error" for event in row["events"])
                for row in traces)
    )


def g9(candidate, baseline):
''',
    )
    revised = replacement(
        revised,
        '        prompts = json.loads((OUT / "prompts.json").read_text())[arm]\n',
        """        if not protocol_verified(OUT / label, document):
            result["stop"] = {"label": label, "reason": "protocol/harness failure",
                              "retained_report": str(report.relative_to(ROOT))}
            index.write_text(json.dumps(result, indent=2) + "\\n")
            raise RuntimeError("Missing/failed planner or answer trace: " + label)
        prompts = json.loads((OUT / "prompts.json").read_text())[arm]
""",
    )
    compile(revised, "proposed-experiment-v2.py", "exec")
    return revised


def extract_function(source, name):
    node = next(
        n
        for n in ast.walk(ast.parse(source))
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name
    )
    return ast.get_source_segment(source, node)


async def exercise(source, folder):
    calls = []

    async def no_network_activity():
        return None

    async def no_inference_stream(adapter, request):
        calls.append(request.json_schema is not None)
        answer = (
            json.dumps(
                {
                    "task": "transform",
                    "queries": [],
                    "freshness": "any",
                    "selection_condition": None,
                }
            )
            if request.json_schema
            else "hello"
        )
        yield TextDelta(answer)
        yield Usage(10, 10)
        yield Finish("stop")

    namespace = {
        "activity": no_network_activity,
        "MODEL": "offline-model",
        "planner": planner,
        "original_stream": no_inference_stream,
        "arm": "offline",
        "folder": folder,
        "asdict": asdict,
        "monotonic": monotonic,
        "json": json,
        "expected_schema": None,
    }
    exec(extract_function(source, "captured_stream"), namespace)
    original_stream, original_schema = Ollama.stream, planner.schema

    def bound_schema(latest):
        result = original_schema(latest)
        namespace["expected_schema"] = result
        return result

    # Even unexpected adapter I/O is rejected locally; no real transport exists.
    import httpx

    def reject_network(request):
        raise AssertionError("Offline harness test attempted network I/O")

    client = httpx.AsyncClient(transport=httpx.MockTransport(reject_network))
    adapter = Ollama("offline", "https://offline.invalid", client=client)
    adapter.capacity = object()
    Ollama.stream = namespace["captured_stream"]
    planner.schema = bound_schema
    try:
        plan, fallback = await planner.plan(
            adapter, "offline-model", "Translate bonjour into English.", [], True, 16384
        )
        first_calls = len(calls)
        valid_answer = ChatRequest(
            "offline-model", [ProviderMessage("user", "Translate bonjour.")], {}, 16384
        )
        _ = [event async for event in adapter.stream(valid_answer)]
        # Invalid sampling must be recorded and rejected before the synthetic provider.
        invalid = ChatRequest("offline-model", valid_answer.messages, {"temperature": 0.9}, 16384)
        before_invalid = len(calls)
        rejected = False
        try:
            _ = [event async for event in adapter.stream(invalid)]
        except AssertionError:
            rejected = True
        assert rejected and len(calls) == before_invalid
        return {
            "search": plan.search,
            "fallback": fallback,
            "synthetic_planner_streams": first_calls,
            "invalid_sampling_rejected_before_provider": rejected,
            "traces": [json.loads(x) for x in (folder / "trace.jsonl").read_text().splitlines()],
        }
    finally:
        Ollama.stream, planner.schema = original_stream, original_schema
        await adapter.close()


def main():
    source = (OUT / "experiment.py").read_text()
    candidate = proposed_patch(source)
    patch = "".join(
        difflib.unified_diff(
            source.splitlines(keepends=True),
            candidate.splitlines(keepends=True),
            fromfile="a/artifacts/images-i1/search-repair/experiment.py",
            tofile="b/artifacts/images-i1/search-repair/experiment.py",
        )
    )
    assert not (OUT / "harness-v2.patch").exists()
    (OUT / "harness-v2.patch").write_text(patch)
    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        original_dir, corrected_dir = root / "original", root / "corrected"
        original_dir.mkdir()
        corrected_dir.mkdir()
        original = asyncio.run(exercise(source, original_dir))
        corrected = asyncio.run(exercise(candidate, corrected_dir))
        assert original["fallback"] and original["synthetic_planner_streams"] == 0
        assert not corrected["fallback"] and not corrected["search"]
        assert corrected["synthetic_planner_streams"] == 1
        assert len(original["traces"]) == 1 and len(corrected["traces"]) == 3
        assert corrected["traces"][-1]["error"] == "AssertionError"
        namespace = {"json": json}
        exec(extract_function(candidate, "protocol_verified"), namespace)
        document = {"results": [{"turns": [{}]}]}
        wire = [{"body": json.dumps(row["payload"])} for row in corrected["traces"][:2]]
        (corrected_dir / "wire.jsonl").write_text("\n".join(map(json.dumps, wire)))
        assert not namespace["protocol_verified"](corrected_dir, document)
        (corrected_dir / "trace.jsonl").write_text(
            "\n".join(map(json.dumps, corrected["traces"][:2]))
        )
        assert namespace["protocol_verified"](corrected_dir, document)
        (corrected_dir / "trace.jsonl").write_text(json.dumps(corrected["traces"][1]))
        assert not namespace["protocol_verified"](corrected_dir, document)
    result = {
        "mode": "Offline synthetic adapter; no inference or external network",
        "original_harness_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "proposed_patch_sha256": hashlib.sha256(patch.encode()).hexdigest(),
        "original": original,
        "corrected": corrected,
        "protocol_gate_accepts_complete_trace": True,
        "protocol_gate_rejects_missing_planner_and_swallowed_assertion": True,
        "production_changes": [],
        "real_model_calls": 0,
        "limits": "Confirms harness plumbing only; synthetic JSON is not model qualification.",
    }
    (OUT / "offline-harness-verification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            {key: value for key, value in result.items() if key not in ("original", "corrected")},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
