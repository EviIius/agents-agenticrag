"""N0: real native adapter and scheduler, scripted inference and fixture tools only."""

import asyncio
import json
from pathlib import Path
from typing import Any

import pytest

from app.capacity import Capacity
from app.db import messages
from app.errors import AppError
from app.runs.agent import Budgets
from app.runs.agent_tools import Arguments, ToolOutput, Tools
from tests.agent_helpers import call, packets, rig, source
from tests.test_chat import chat_app as chat_app


async def test_same_conversation_stream_parts_sources_and_replay(chat_app: Any) -> None:
    r = await rig(
        chat_app,
        [
            packets("Checking. ", [call("web_search", query="fake label")]),
            packets("The label is Lantern [1]."),
        ],
    )

    async def search(args: Arguments) -> ToolOutput:
        return ToolOutput(sources=[source()])

    await r.execute(r.agent({"web_search": search}))
    assert r.run.message.status == "complete"
    assert r.run.message.content == "Checking. The label is Lantern [1]."
    assert [p.type for p in r.run.message.parts] == ["text", "tool", "text"]
    assert r.run.message.agent and r.run.message.agent.calls == 2
    second = r.backend.requests[1]
    assert second["messages"][-2]["content"] == "Checking. "
    assert second["messages"][-1]["role"] == "tool"
    assert second["messages"][-1]["tool_name"] == "web_search"
    assert '<source id="1"' in second["messages"][-1]["content"]
    assert "Citation label: [1]" in second["messages"][-1]["content"]
    assert all(
        c["keep_alive"] == "47m" and c["options"] == {"num_ctx": 32768} and "think" not in c
        for c in r.backend.requests
    )
    saved = await messages.message(r.app.state.store, r.run.message.id)
    assert saved.parts == r.run.message.parts and saved.agent == r.run.message.agent
    assert saved.content == "".join(p.text for p in saved.parts if p.type == "text")
    rows = await messages.sources(r.app.state.store, saved.chat_id)
    assert rows[saved.id][0].cited
    events = [event.type async for _, event in r.run.tail()]
    assert events.count("tool.started") == events.count("tool.finished") == 1
    assert events[-2:] == ["message.done", "run.closed"]
    assert [i async for i, _ in r.run.tail(2)] == list(range(3, len(events) + 1))


@pytest.mark.parametrize("reasoning", [None, "off", "low", "medium", "xhigh"])
async def test_exact_reasoning_and_sampling_every_step(
    chat_app: Any, reasoning: str | None
) -> None:
    r = await rig(chat_app, [packets(calls=[call("calculate", expression="6*7")]), packets("42")])
    r.request.reasoning = reasoning
    r.request.params = {"temperature": 0.4, "seed": 12, "max_tokens": 80}
    await r.execute(r.agent())
    assert r.run.message.status == "complete"
    for body in r.backend.requests:
        assert body["options"] == {
            "temperature": 0.4,
            "seed": 12,
            "num_predict": 80,
            "num_ctx": 32768,
        }
        if reasoning is None:
            assert "think" not in body
        else:
            assert body["think"] == (False if reasoning == "off" else reasoning)


@pytest.mark.parametrize(
    "problem", ["thinking", "tools", "context", "digest", "version", "recording"]
)
async def test_unqualified_or_unsupported_guard_precedes_inference(
    chat_app: Any, problem: str
) -> None:
    r = await rig(chat_app, [])
    agent = r.agent()
    if problem == "thinking":
        r.request.reasoning = "high"
    if problem == "tools":
        r.model.tools = False
    if problem == "context":
        r.request.context_length = 65536
    if problem == "digest":
        r.model.digest = "not-qualified"
    if problem == "version":
        agent.qualifications = []
    if problem == "recording":
        r.context.has_recording = True
        agent.tools.block_web = True
    with pytest.raises(AppError):
        await agent.guard(r.request, r.context)
    assert r.backend.requests == []


@pytest.mark.parametrize("mode", ["steps", "context", "answer_now"])
async def test_single_closing_call_keeps_exact_settings(chat_app: Any, mode: str) -> None:
    turns = [packets("Kept. ", [call("calculate", expression="6*7")]), packets("42")]
    r = await rig(chat_app, turns if mode == "steps" else [packets("Closing")])
    agent = r.agent(budgets=Budgets(steps=1))
    if mode == "context":
        agent.budgets = Budgets(context_fraction=0.0001)
    if mode == "answer_now":
        agent.answer_now.set()
    await r.execute(agent)
    assert r.run.message.agent and r.run.message.agent.limit_reached == mode
    assert len(r.backend.requests) == (2 if mode == "steps" else 1)
    assert "tools" not in r.backend.requests[-1]
    assert all(body["options"] == {"num_ctx": 32768} for body in r.backend.requests)


@pytest.mark.parametrize(
    "bad",
    [
        call("terminal", command="fake"),
        call("web_search", query=8),
        call("web_search", query="ok", unexpected=True),
        call("calculate", expression="1/0"),
        {"function": {"name": "calculate", "arguments": "bad JSON"}},
    ],
)
async def test_invalid_calls_get_short_feedback_without_dispatch(
    chat_app: Any, bad: dict[str, Any]
) -> None:
    r = await rig(chat_app, [packets(calls=[bad]), packets("Cannot do that.")])
    await r.execute(r.agent())
    info = r.run.message.agent
    assert info and info.invalid_calls == 1 and info.calls == 2
    assert r.run.message.status == "complete"
    assert r.run.message.parts[0].step and r.run.message.parts[0].step.status == "failed"
    assert "Tool refused" in r.backend.requests[-1]["messages"][-1]["content"]


async def test_per_tool_budget_and_partial_answer_survive(chat_app: Any) -> None:
    r = await rig(
        chat_app,
        [
            packets(
                "Partial. ",
                [call("calculate", expression="6*7"), call("calculate", expression="8*9")],
            ),
            packets("Done"),
        ],
    )
    await r.execute(r.agent(budgets=Budgets(calculations=1)))
    info = r.run.message.agent
    assert info and info.calculations == 1 and info.invalid_calls == 1
    assert r.run.message.content == "Partial. Done"


@pytest.mark.parametrize("phase", ["model", "tool"])
async def test_stop_closes_stream_or_tool_and_releases_capacity(
    chat_app: Any, tmp_path: Path, phase: str
) -> None:
    turns: list[list[dict[str, Any]]] = (
        [[{"message": {"content": "Kept partial. "}}, {"pause": True}]]
        if phase == "model"
        else [packets(calls=[call("web_search", query="fake")])]
    )
    r = await rig(chat_app, turns)
    tool_started, tool_closed = asyncio.Event(), asyncio.Event()

    async def search(args: Arguments) -> ToolOutput:
        tool_started.set()
        try:
            await asyncio.Event().wait()
        finally:
            tool_closed.set()
        return ToolOutput()

    capacity = r.adapter.capacity = Capacity(tmp_path / "fake-native.lock")
    agent = r.agent({"web_search": search})
    task = asyncio.create_task(r.execute(agent))
    await asyncio.wait_for((r.backend.paused if phase == "model" else tool_started).wait(), 2)
    await r.app.state.runs.cancel(r.run.id)
    await task
    assert r.run.message.status == "stopped" and r.run.closed
    assert r.backend.closed == 1 and not capacity.busy
    assert not capacity.interactive and capacity.fd is None
    if phase == "model":
        assert r.run.message.content == "Kept partial. "
    else:
        assert tool_closed.is_set()
    assert (await messages.message(r.app.state.store, r.run.message.id)).status == "stopped"


async def test_scheduler_and_connection_semaphore_are_free_during_tools(chat_app: Any) -> None:
    r = await rig(chat_app, [packets(calls=[call("web_search", query="fake")]), packets("Done")])
    semaphore = asyncio.Semaphore(1)
    r.adapter.capacity = Capacity()

    async def search(args: Arguments) -> ToolOutput:
        assert not semaphore.locked() and r.adapter.capacity and not r.adapter.capacity.busy
        async with semaphore:
            async with r.adapter.capacity.lease():
                pass  # Another chat/native operation can acquire both during the tool.
        return ToolOutput()

    agent = r.agent({"web_search": search})
    await agent(r.run, r.request, r.context, semaphore)
    assert r.run.message.status == "complete"


async def test_time_limit_is_hard_and_starts_no_extra_closing_request(chat_app: Any) -> None:
    r = await rig(chat_app, [[{"message": {"content": "Partial"}}, {"pause": True}]])
    await r.execute(r.agent(budgets=Budgets(seconds=0.03)))
    assert r.run.message.agent and r.run.message.agent.limit_reached == "time"
    assert r.run.message.content == "Partial" and len(r.backend.requests) == 1
    assert r.backend.closed == 1


async def test_answer_now_closes_active_stream_before_one_closing_call(chat_app: Any) -> None:
    r = await rig(
        chat_app, [[{"message": {"content": "Partial. "}}, {"pause": True}], packets("Done")]
    )
    agent = r.agent()
    task = asyncio.create_task(r.execute(agent))
    await asyncio.wait_for(r.backend.paused.wait(), 2)
    agent.answer_now.set()
    await task
    assert r.run.message.content == "Partial. Done" and r.backend.closed == 2
    assert len(r.backend.requests) == 2 and "tools" not in r.backend.requests[-1]


async def test_answer_now_cancels_a_tool_and_skips_pending_batch_calls(chat_app: Any) -> None:
    r = await rig(
        chat_app,
        [
            packets(calls=[call("web_search", query="fake"), call("calculate", expression="6*7")]),
            packets("Done"),
        ],
    )
    started, closed = asyncio.Event(), asyncio.Event()

    async def search(args: Arguments) -> ToolOutput:
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            closed.set()
        return ToolOutput()

    agent = r.agent({"web_search": search})
    task = asyncio.create_task(r.execute(agent))
    await asyncio.wait_for(started.wait(), 2)
    agent.answer_now.set()
    await asyncio.wait_for(task, 2)
    assert closed.is_set() and len(r.backend.requests) == 2
    assert r.run.message.agent and r.run.message.agent.calculations == 0
    assert "Not executed" in r.backend.requests[-1]["messages"][-1]["content"]


async def test_numbering_is_stable_and_read_output_is_bounded(chat_app: Any) -> None:
    url = "https://public.example.test/one"
    r = await rig(
        chat_app,
        [
            packets(calls=[call("web_search", query="fake")]),
            packets(calls=[call("read_page", url=url, focus="label")]),
            packets(calls=[call("web_search", query="again")]),
            packets("Lantern [1]."),
        ],
    )

    async def search(args: Arguments) -> ToolOutput:
        return ToolOutput(sources=[source(url, "snippet")])

    async def read(args: Arguments) -> ToolOutput:
        found = source(url)
        found.passages[0].text = "Fake passage " * 1000
        from app.schemas import WebRead

        return ToolOutput(sources=[found], read=WebRead(url=url, status="used"))

    await r.execute(r.agent({"web_search": search, "read_page": read}))
    assert r.run.message.agent and r.run.message.agent.source_count == 1
    assert r.run.message.agent.pages == 1
    saved = (await messages.sources(r.app.state.store, r.run.message.chat_id))[r.run.message.id]
    assert saved[0].n == 1 and saved[0].kind == "page" and saved[0].cited
    assert len(saved[0].passages[0].text) == 4000
    assert (await messages.reads(r.app.state.store, r.run.message.chat_id))[r.run.message.id][
        0
    ].status == "used"


async def test_provider_error_keeps_partial_and_emits_error_snapshot(chat_app: Any) -> None:
    r = await rig(chat_app, [[{"message": {"content": "Partial"}}, {"error": "fake failure"}]])
    await r.execute(r.agent())
    assert r.run.message.status == "error" and r.run.message.content == "Partial"
    assert r.run.message.stats and r.run.message.stats.finish_reason == "error"
    assert r.run.events[-2].type == "message.error" and r.run.closed


@pytest.mark.parametrize("kind", ["web", "library"])
async def test_missing_or_invalid_citation_is_flagged_without_retry(
    chat_app: Any, kind: str
) -> None:
    name = "web_search" if kind == "web" else "library_search"
    r = await rig(chat_app, [packets(calls=[call(name, query="label")]), packets("Lantern [99].")])

    async def search(args: Arguments) -> ToolOutput:
        return ToolOutput(sources=[source(kind="page" if kind == "web" else "document")])

    await r.execute(r.agent({name: search}, kind))
    info = r.run.message.agent
    assert info and info.source_count == 1 and info.invalid_citations == 1
    assert info.notice and info.notice.code == "uncited"
    assert "99" not in r.run.message.content and len(r.backend.requests) == 2
    assert "99" not in "".join(p.text for p in r.run.message.parts)


async def test_untrusted_link_private_query_and_cross_scope_never_dispatch(chat_app: Any) -> None:
    secret = "eight private tokens must never leave this machine"
    r = await rig(
        chat_app,
        [
            packets(
                calls=[
                    call("read_page", url="https://attacker.example.test/", focus="x"),
                    call("web_search", query=secret),
                    call("library_search", query="x"),
                ]
            ),
            packets("Refused"),
        ],
    )
    agent = r.agent()
    agent.tools = Tools("web", {}, private_context=[secret])
    await r.execute(agent)
    assert r.run.message.agent and r.run.message.agent.invalid_calls == 3
    assert r.run.message.agent.searches == r.run.message.agent.pages == 0
    assert r.run.message.content == "Refused"


async def test_restart_keeps_text_and_stops_persisted_tool_row(chat_app: Any) -> None:
    r = await rig(
        chat_app, [packets("Partial ", [call("calculate", expression="6*7")]), packets("42")]
    )
    await r.execute(r.agent())
    parts = [part.model_dump() for part in r.run.message.parts]
    parts[1]["step"]["status"] = "running"
    await r.app.state.store.execute(
        "UPDATE messages SET status='streaming',parts_json=? WHERE id=?",
        (json.dumps(parts), r.run.message.id),
    )
    await r.app.state.runs.recover()
    saved = await messages.message(r.app.state.store, r.run.message.id)
    assert saved.status == "interrupted" and saved.content == "Partial 42"
    assert saved.parts[1].step and saved.parts[1].step.status == "stopped"


async def test_tool_exception_is_short_and_agent_is_not_installed_in_send_path(
    chat_app: Any,
) -> None:
    r = await rig(
        chat_app, [packets(calls=[call("web_search", query="fake")]), packets("Unavailable")]
    )

    async def search(args: Arguments) -> ToolOutput:
        raise RuntimeError("fake-private-exception-detail")

    await r.execute(r.agent({"web_search": search}))
    assert r.run.message.parts[0].step and r.run.message.parts[0].step.status == "failed"
    assert "fake-private-exception-detail" not in json.dumps(r.backend.requests)
    assert r.app.state.runs.web_hook.__class__.__module__ == "app.search.pipeline"
    assert r.app.state.runs.library_hook.__class__.__module__ == "app.library.pipeline"


@pytest.mark.parametrize(
    "values",
    [
        {"steps": 7},
        {"searches": 5},
        {"pages": 7},
        {"library_searches": 5},
        {"calculations": 9},
        {"seconds": 181},
        {"context_fraction": 0.8},
    ],
)
def test_host_budgets_cannot_be_raised_above_approved_limits(values: dict[str, Any]) -> None:
    with pytest.raises(ValueError):
        Budgets(**values)
