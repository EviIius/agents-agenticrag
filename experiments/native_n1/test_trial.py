"""N1 counter/admission/fixture/controller checks: MockTransport, zero native calls."""

import asyncio
import json
import sys
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "server"))
sys.path.insert(0, str(Path(__file__).parent))

from protocol import (  # noqa: E402
    MODEL,
    CountedTransport,
    ExperimentalAgent,
    Fixtures,
    Ledger,
    Refused,
    validate_wire,
)
from trial import execute_case, resource_check  # noqa: E402

from app.capacity import Capacity  # noqa: E402
from app.errors import AppError  # noqa: E402
from app.providers.base import ChatRequest, ProviderMessage  # noqa: E402
from app.providers.ollama import Ollama  # noqa: E402
from app.runs.agent import Agent  # noqa: E402
from app.runs.agent_tools import ReadPage  # noqa: E402
from app.runs.context import Context  # noqa: E402
from app.schemas import ModelInfo  # noqa: E402

CORPUS = json.loads((Path(__file__).parent / "cases-original.json").read_text())


def review(passed=True):
    return {
        "checks": {
            k: passed
            for k in ("facts", "support", "citations", "permissions", "resources", "budgets")
        },
        "notes": "Synthetic explicit test review, not a native quality result.",
    }


def test_ledger_enforces_order_reviews_and_immutable_stop(tmp_path):
    ledger = Ledger(tmp_path / "ledger.json")
    with pytest.raises(Refused):
        ledger.begin("S1-H02")
    ledger.begin("S1-H01")
    assert ledger.admit("S1-H01") == 1
    with pytest.raises(Refused):
        ledger.begin("S1-H02")
    ledger.review("S1-H01", review())
    ledger.begin("S1-H02")
    ledger.review("S1-H02", review(False))
    assert json.loads(ledger.path.read_text())["stopped"]
    with pytest.raises(Refused):
        Ledger(ledger.path).begin("S1-H03")
    with pytest.raises(Refused):
        ledger.admit("S1-H02")
    with pytest.raises(Refused):
        ledger.review("S1-H02", review())


@pytest.mark.parametrize("global_calls,task_calls", [(36, 0), (0, 7)])
def test_both_call_limits_are_durable(tmp_path, global_calls, task_calls):
    ledger = Ledger(tmp_path / "ledger.json")
    ledger.begin("S1-H01")
    with ledger.locked() as state:
        state["calls"] = global_calls
        state["tasks"]["S1-H01"]["calls"] = task_calls
    with pytest.raises(Refused):
        ledger.admit("S1-H01")
    assert json.loads(ledger.path.read_text())["stopped"]


async def test_h04_scope_preserves_original_texts_and_never_offers_web():
    fixture = Fixtures(CORPUS, "H04")
    result = await fixture.search(None)
    assert fixture.tools().names == ["library_search", "calculate"]
    assert [s.document_id for s in result.sources] == ["W1", "W2", "L1"]
    original = {s["id"]: s["text"] for s in CORPUS["sources"]}
    assert all(s.passages[0].text == original[s.document_id] for s in result.sources)


async def test_page_fixture_uses_same_canonical_urls_as_host_allowlist():
    result = await Fixtures(CORPUS, "H01").read(
        ReadPage(url="https://cedar.example.test/spec/?utm_source=fake", focus="storage")
    )
    assert result.sources[0].url == "https://cedar.example.test/spec"
    assert result.sources[0].passages[0].text == CORPUS["sources"][0]["text"]


@pytest.mark.parametrize(
    "extra",
    [
        {"think": False},
        {"options": {"num_ctx": 32768, "temperature": 0}},
        {"keep_alive": "5m"},
        {"model": "unapproved"},
        {"tools": []},
    ],
)
def test_wire_refuses_silent_defaults_and_changed_tools(extra):
    tools = Fixtures(CORPUS, "H01").tools()
    adapter = Ollama.__new__(Ollama)
    adapter.keep_alive = "30m"
    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": "Synthetic"}],
        "stream": True,
        "keep_alive": "30m",
        "options": {"num_ctx": 32768},
        "tools": tools.schemas(),
    }
    validate_wire(body, MODEL, tools)
    with pytest.raises(Refused):
        validate_wire({**body, **extra}, MODEL, tools)


@pytest.mark.parametrize(
    "change",
    [
        {"swap_mib": 0.01},
        {"health_ok": False},
        {"health_ms": 2001},
        {"models": [{"name": "other", "size_vram": 1}]},
        {"models": [{"name": MODEL, "size_vram": 49 * 1024**3}]},
    ],
)
def test_resources_fail_closed(change):
    original = {"swap_mib": 0, "health_ok": True, "health_ms": 1, "models": []}
    resource_check(original, 0)
    with pytest.raises(Refused):
        resource_check({**original, **change}, 0)


async def test_transport_requires_capacity_and_refuses_post_stop(tmp_path):
    ledger = Ledger(tmp_path / "ledger.json")
    ledger.begin("S1-H01")
    tools = Fixtures(CORPUS, "H01").tools()
    capacity = Capacity(tmp_path / "native.lock")
    sent = []

    def handle(request):
        sent.append(request)
        return httpx.Response(200, content=b'{"done":true}\n')

    transport = CountedTransport(
        ledger, "S1-H01", tools, tmp_path, capacity, httpx.MockTransport(handle)
    )
    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": "Synthetic"}],
        "stream": True,
        "keep_alive": "30m",
        "options": {"num_ctx": 32768},
    }
    async with httpx.AsyncClient(transport=transport) as client:
        with pytest.raises(Refused):
            await client.post("http://127.0.0.1:11434/api/chat", json=body)
        async with capacity.lease():
            with pytest.raises(Refused):
                await client.post("http://127.0.0.1:11434/api/chat", json=body)
    assert not sent and json.loads(ledger.path.read_text())["calls"] == 0


@pytest.mark.parametrize("cited", [True, False])
async def test_complete_controller_with_native_scripted_transport(tmp_path, cited):
    task = "S1-H01"
    ledger = Ledger(tmp_path / "ledger.json")
    ledger.begin(task)
    turns = [
        {
            "message": {
                "tool_calls": [
                    {
                        "function": {
                            "name": "web_search",
                            "arguments": {"query": "Synthetic Cedar Harbor specifications"},
                        }
                    }
                ]
            }
        },
        {
            "message": {
                "content": "Cedar: 24 units, CSV [1]. Harbor: 36 units, JSON [2]."
                if cited
                else "Cedar: 24 units, CSV. Harbor: 36 units, JSON."
            }
        },
    ]

    def handle(request):
        if request.url.path == "/api/version":
            return httpx.Response(200, json={"version": "fake-version"})
        return httpx.Response(
            200, content=(json.dumps(turns.pop(0)) + '\n{"done":true}\n').encode()
        )

    async def sampler():
        return {"swap_mib": 0, "health_ok": True, "health_ms": 1, "models": []}

    model = ModelInfo(
        connection_id="native-n1",
        model_id=MODEL,
        display_name="Synthetic",
        tools=True,
        digest="fake-digest",
        context_length=32768,
        context_limit=32768,
    )
    admission = {
        "stage": "N1-experiment-only",
        "model_id": MODEL,
        "digest": "fake-digest",
        "runtime_version": "fake-version",
        "swap_baseline_mib": 0,
    }
    folder = tmp_path / "task"
    folder.mkdir()
    result = await execute_case(
        task,
        CORPUS,
        model,
        admission,
        ledger,
        folder,
        Capacity(tmp_path / "native.lock"),
        upstream=httpx.MockTransport(handle),
        sampler=sampler,
    )
    assert not turns
    assert json.loads(ledger.path.read_text())["calls"] == 2
    assert all(result["automatic_checks"].values()) is cited
    assert result["source_map"] == {"1": "W1", "2": "W2", "3": "W3"}
    assert bool(json.loads(ledger.path.read_text())["stopped"]) is not cited
    assert json.loads((folder / "events.json").read_text())[-1]["type"] == "run.closed"


def test_review_needs_explicit_boolean_semantic_checks(tmp_path):
    ledger = Ledger(tmp_path / "ledger.json")
    ledger.begin("S1-H01")
    for invalid in ({}, {"checks": {"facts": True}, "notes": "Partial"}):
        with pytest.raises(Refused):
            ledger.review("S1-H01", invalid)


async def test_experimental_admission_does_not_qualify_production():
    class MetadataOnly:
        async def json(self, *args):
            return {"version": "fake-version"}

    model = ModelInfo(
        connection_id="native-n1",
        model_id=MODEL,
        display_name="Synthetic",
        tools=True,
        digest="fake-digest",
        context_length=32768,
        context_limit=32768,
    )
    request = ChatRequest(MODEL, [ProviderMessage("user", "Synthetic")], context_length=32768)
    context = Context(request.messages, 0, 0, 1024, 0.3)
    tools = Fixtures(CORPUS, "H01").tools()
    admission = {
        "stage": "N1-experiment-only",
        "model_id": MODEL,
        "digest": "fake-digest",
        "runtime_version": "fake-version",
    }
    agent = ExperimentalAgent(None, MetadataOnly(), model, tools, admission=admission)
    assert agent.qualifications == []
    await agent.guard(request, context)
    with pytest.raises(AppError, match="tool probe"):
        await Agent(None, MetadataOnly(), model, tools, []).guard(request, context)
    agent.admission = {**admission, "digest": "changed"}
    with pytest.raises(Refused):
        await agent.guard(request, context)


async def test_deadline_closes_active_stream_and_capacity(tmp_path, monkeypatch):
    import trial

    assert trial.MAX_SECONDS == 180
    monkeypatch.setattr(trial, "MAX_SECONDS", 0.2)
    ledger = Ledger(tmp_path / "ledger.json")
    task = "S1-H01"
    ledger.begin(task)
    closed = []

    class Stalled(httpx.AsyncByteStream):
        async def __aiter__(self):
            yield b'{"message":{"content":"Synthetic partial"}}\n'
            await asyncio.Event().wait()

        async def aclose(self):
            closed.append(True)

    def handle(request):
        if request.url.path == "/api/version":
            return httpx.Response(200, json={"version": "fake-version"})
        return httpx.Response(200, stream=Stalled())

    async def sampler():
        return {"swap_mib": 0, "health_ok": True, "health_ms": 1, "models": []}

    model = ModelInfo(
        connection_id="native-n1",
        model_id=MODEL,
        display_name="Synthetic",
        tools=True,
        digest="fake-digest",
        context_length=32768,
        context_limit=32768,
    )
    admission = {
        "stage": "N1-experiment-only",
        "model_id": MODEL,
        "digest": "fake-digest",
        "runtime_version": "fake-version",
        "swap_baseline_mib": 0,
    }
    folder = tmp_path / "task"
    folder.mkdir()
    capacity = Capacity(tmp_path / "native.lock")
    result = await execute_case(
        task,
        CORPUS,
        model,
        admission,
        ledger,
        folder,
        capacity,
        upstream=httpx.MockTransport(handle),
        sampler=sampler,
    )
    state = json.loads(ledger.path.read_text())
    assert state["calls"] == 1 and "deadline" in state["stopped"]
    assert closed and not capacity.busy and capacity.fd is None
    assert result["message"]["content"] == "Synthetic partial"
    assert result["message"]["status"] == "stopped"
