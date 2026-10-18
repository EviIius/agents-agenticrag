"""Scripted C1 checks; zero real model requests."""

import json
import sys
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from experiments.native_c1 import controller as c1  # noqa: E402

from app.capacity import Capacity  # noqa: E402
from app.runs import agent as agent_module  # noqa: E402
from app.schemas import ModelInfo  # noqa: E402

CORPUS = json.loads((ROOT / "experiments/native_n1/cases-original.json").read_text())


def test_candidate_matches_reviewed_text_for_both_source_kinds():
    frozen = json.loads(c1.CANDIDATE.read_text())
    for kind in ("web", "library"):
        assert c1.expected_system(kind) == c1.original.SYSTEM + "\n\n" + frozen[kind]["v2_prompt"]


@pytest.mark.parametrize("corruption", ["old_prompt", "changed_prompt", "missing_system"])
async def test_wire_prompt_refused_before_admission_or_network(tmp_path, corruption):
    ledger = c1.Ledger(tmp_path / "ledger.json")
    ledger.begin("S1-H01")
    sent = []
    capacity = Capacity(tmp_path / "native.lock")
    tools = c1.original.Fixtures(CORPUS, "H01").tools()
    transport = c1.FrozenTransport(
        ledger,
        "S1-H01",
        tools,
        tmp_path,
        capacity,
        httpx.MockTransport(lambda request: sent.append(request)),
    )
    system = c1.expected_system("web")
    if corruption == "old_prompt":
        system = c1.original.SYSTEM + "\n\n" + agent_module.prompt("web")
    else:
        system += " Changed"
    body = {"messages": [{"role": "system", "content": system}]}
    if corruption == "missing_system":
        body["messages"] = []
    async with httpx.AsyncClient(transport=transport) as client:
        async with capacity.lease():
            with pytest.raises(c1.Refused, match="prompt changed"):
                await client.post("http://127.0.0.1:11434/api/chat", json=body)
    state = json.loads(ledger.path.read_text())
    assert state["stopped"] and state["calls"] == 0 and not sent


@pytest.mark.parametrize("cited", [True, False])
async def test_actual_controller_uses_candidate_and_stops_uncited_items(tmp_path, cited):
    task = "S1-H01"
    ledger = c1.Ledger(tmp_path / "ledger.json")
    ledger.begin(task)
    answer = (
        "- Cedar: 24 units, CSV [1].\n- Harbor: 36 units, JSON [2]."
        if cited
        else "Sources [1][2]:\n- Cedar: 24 units, CSV.\n- Harbor: 36 units, JSON."
    )
    turns = [
        {"tool_calls": [{"function": {"name": "web_search", "arguments": {"query": "specs"}}}]},
        {"content": answer},
    ]
    bodies = []

    def handle(request):
        if request.url.path == "/api/version":
            return httpx.Response(200, json={"version": "fake-version"})
        bodies.append(json.loads(request.content))
        return httpx.Response(
            200, content=(json.dumps({"message": turns.pop(0)}) + '\n{"done":true}\n').encode()
        )

    async def sampler():
        return {"swap_mib": 0, "health_ok": True, "health_ms": 1, "models": []}

    model = ModelInfo(
        connection_id="native-n1",
        model_id=c1.original.MODEL,
        display_name="Synthetic",
        tools=True,
        digest="fake-digest",
        context_length=32768,
        context_limit=32768,
    )
    admission = {
        "stage": "N1-experiment-only",
        "model_id": model.model_id,
        "digest": model.digest,
        "runtime_version": "fake-version",
        "swap_baseline_mib": 0,
    }
    folder = tmp_path / "task"
    folder.mkdir()
    old_prompt = agent_module.prompt
    old_transport = c1.original.CountedTransport
    result = await c1.execute_case(
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
    assert agent_module.prompt is old_prompt and c1.original.CountedTransport is old_transport
    assert len(bodies) == 2 and not turns
    assert all(b["messages"][0]["content"] == c1.expected_system("web") for b in bodies)
    assert all(b["options"] == {"num_ctx": 32768} and "think" not in b for b in bodies)
    assert result["message"]["content"] == answer
    assert all(result["automatic_checks"].values()) is cited
    state = json.loads(ledger.path.read_text())
    assert state["calls"] == 2 and bool(state["stopped"]) is not cited


def test_new_paths_never_resume_old_ledger():
    assert c1.QA != c1.original.QA
    assert c1.OUT != c1.original.OUT
    assert c1.OLD_LEDGER.parent == c1.original.QA


async def test_prompt_binding_restored_after_exception(monkeypatch):
    async def fail(*args, **kwargs):
        assert agent_module.prompt is c1.prompt
        raise RuntimeError("scripted failure")

    old = agent_module.prompt
    monkeypatch.setattr(c1, "N1_EXECUTE", fail)
    with pytest.raises(RuntimeError, match="scripted failure"):
        await c1.execute_case()
    assert agent_module.prompt is old
