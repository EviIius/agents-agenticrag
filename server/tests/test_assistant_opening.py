"""Native task lifecycle with invented state and injected fake operations only."""

import asyncio
import hashlib
import json
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI
from pydantic import ValidationError

from app.assistant.app_open import OpenDecision
from app.assistant.contracts import DesktopTask, OpenedApplication, TaskCreate, TaskDecision
from app.assistant.driver import FakeDesktopDriver, ScriptedProposal
from app.assistant.manager import DesktopTasks
from app.assistant.opening import NativeOpening, OpeningQualification, qualification
from app.config import Settings
from app.db.core import Store, connect
from app.errors import AppError
from app.main import create_app
from app.schemas import ModelInfo

CHAT = "a" * 32
CONNECTION = "b" * 32


class StubOpening:
    def __init__(self) -> None:
        self.proposals = 0
        self.opens = 0
        self.refuse = False
        self.wrong_app = False
        self.active = asyncio.Event()
        self.hold_proposal = False
        self.hold_open = False

    async def propose(self, task: DesktopTask) -> OpenDecision:
        self.proposals += 1
        if self.hold_proposal:
            self.active.set()
            await asyncio.Event().wait()
        return (
            OpenDecision(action="refuse", app=None)
            if self.refuse
            else OpenDecision(action="open_app", app="notes")
        )

    async def open(self, decision: OpenDecision) -> OpenedApplication:
        self.opens += 1
        self.active.set()
        if self.hold_open:
            await asyncio.Event().wait()
        return OpenedApplication(
            name="Messages" if self.wrong_app else "Notes",
            bundle_id="com.apple.MobileSMS" if self.wrong_app else "com.apple.Notes",
            pid=300,
        )


Host = tuple[DesktopTasks, StubOpening, Store]


@pytest_asyncio.fixture
async def host(tmp_path: Path) -> AsyncIterator[tuple[DesktopTasks, StubOpening, Store]]:
    async with connect(tmp_path) as db:
        store = Store(db)
        await store.execute(
            "INSERT INTO chats(id,created_at,updated_at) VALUES (?,?,?)",
            (CHAT, "2026-11-08", "2026-11-08"),
        )
        service = StubOpening()
        manager = DesktopTasks(store, FakeDesktopDriver(), ScriptedProposal(), opening=service)
        try:
            yield manager, service, store
        finally:
            await manager.close()


async def create(manager: DesktopTasks, key: str = "open-request-key") -> DesktopTask:
    return await manager.create(
        CHAT, TaskCreate(request_key=key, text="Open Notes", mode="open_app")
    )


async def settle(manager: DesktopTasks, task: DesktopTask) -> DesktopTask:
    await asyncio.wait_for(asyncio.shield(manager.jobs[task.id]), 2)
    return await manager.get(task.id)


async def test_verified_opening_uses_existing_durable_tasks_and_replay_is_idempotent(
    host: Host,
) -> None:
    manager, service, store = host
    task = await create(manager)
    result = await settle(manager, task)
    assert result.state == "complete" and result.opened_app is not None
    assert result.opened_app.name == "Notes"
    assert result.fake is False and result.observation is None and result.approval is None
    assert result.native_dispatched and service.proposals == service.opens == 1
    replay = await create(manager)
    assert replay.id == result.id and service.proposals == service.opens == 1
    events = [event async for _, event in manager.tail(task.id)]
    assert events[-1].task.opened_app is not None
    assert events[-1].task.opened_app.name == "Notes"
    assert any(event.task.stage == "Choosing an app" for event in events)
    assert not await store.rows("SELECT * FROM assistant_approvals")
    with pytest.raises(AppError, match="approval"):
        await manager.decide(
            task.id,
            TaskDecision(approval_id="invented", revision=result.revision, decision="approve"),
        )


async def test_refusal_executes_no_app_operation(host: Host) -> None:
    manager, service, _ = host
    service.refuse = True
    result = await settle(manager, await create(manager))
    assert result.state == "needs_input" and not result.native_dispatched
    assert service.proposals == 1 and service.opens == 0


async def test_wrong_app_receipt_never_marks_task_complete(host: Host) -> None:
    manager, service, _ = host
    service.wrong_app = True
    result = await settle(manager, await create(manager))
    assert result.state == "outcome_unknown" and result.opened_app is None


@pytest.mark.parametrize("during_open", [False, True])
async def test_stop_and_restart_do_not_replay_native_dispatch(
    host: Host, during_open: bool
) -> None:
    manager, service, _ = host
    service.hold_open = during_open
    service.hold_proposal = not during_open
    task = await create(manager)
    await asyncio.wait_for(service.active.wait(), 2)
    stopped = await manager.cancel(task.id)
    assert stopped.state == ("outcome_unknown" if during_open else "cancelled")
    assert service.opens == int(during_open)
    replay = await create(manager)
    assert replay.id == task.id and service.proposals == 1
    if during_open:
        await manager.save(stopped, state="running")  # persisted crash before receipt
        await manager.recover()
        assert (await manager.get(task.id)).state == "outcome_unknown"
        assert service.opens == 1


@pytest.mark.parametrize(
    "changes",
    [
        {"fixture": "messages"},
        {"observation": {"app_id": "invented"}},
        {"fake": True},
        {"state": "complete"},
    ],
)
def test_opening_task_cannot_gain_private_read_or_input_fields(changes: dict[str, Any]) -> None:
    value = dict(
        id="task",
        chat_id=CHAT,
        text="Open Notes",
        mode="open_app",
        fixture=None,
        fake=False,
        state="running",
        created_at="2026-11-08",
    )
    with pytest.raises(ValidationError):
        DesktopTask.model_validate(value | changes)


async def test_disabled_opening_never_dispatches_or_creates_a_task(host: Host) -> None:
    manager, service, store = host
    manager.opening = None
    with pytest.raises(AppError):
        await create(manager)
    assert service.proposals == 0 and not await store.rows("SELECT * FROM assistant_tasks")


def config(tmp_path: Path) -> OpeningQualification:
    return OpeningQualification(
        protocol=1,
        executable_sha256=hashlib.sha256(b"invented").hexdigest(),
        connection_id=CONNECTION,
        model_id="qualified-runtime-profile",
        context_length=32768,
        capacity_path=tmp_path / "native.lock",
        max_requests=2,
    )


async def test_native_proposal_keeps_saved_parameters_and_has_durable_two_call_limit(
    host: Host, tmp_path: Path
) -> None:
    manager, _, store = host
    settings = config(tmp_path)
    await store.execute(
        "UPDATE chats SET connection_id=?,model_id=? WHERE id=?",
        (CONNECTION, settings.model_id, CHAT),
    )
    registry = AsyncMock()
    registry.resolve.return_value = ModelInfo(
        connection_id=CONNECTION,
        model_id=settings.model_id,
        display_name="Test",
        context_length=32768,
    )
    registry.params.return_value = {"temperature": 0.4, "reasoning": "low"}
    adapter = AsyncMock()
    adapter.complete_json.return_value = {"action": "open_app", "app": "notes"}
    registry.adapter.return_value = adapter
    service = NativeOpening(store, registry, tmp_path, settings)
    for index in range(2):
        task = DesktopTask(
            id=f"{index:032x}",
            chat_id=CHAT,
            text="Open Notes",
            mode="open_app",
            fake=False,
            state="running",
            created_at="2026-11-08",
        )
        await service.propose(task)
    request = adapter.complete_json.call_args.args[0]
    assert request.params == {"temperature": 0.4} and request.reasoning == "low"
    assert request.context_length == 32768
    assert registry.params.return_value == {"temperature": 0.4, "reasoning": "low"}
    with pytest.raises(AppError) as error:
        await service.propose(task.model_copy(update={"id": "f" * 32}))
    assert error.value.code == "assistant_trial_paused" and adapter.complete_json.call_count == 2


def test_qualification_requires_private_directory_exact_binary_and_integer_budget(
    tmp_path: Path,
) -> None:
    tmp_path.chmod(0o700)
    settings = config(tmp_path)
    (tmp_path / "OpenApp").write_bytes(b"invented")
    file = tmp_path / "qualification.json"
    file.write_text(settings.model_dump_json())
    file.chmod(0o600)
    assert qualification(tmp_path) == settings
    (tmp_path / "OpenApp").write_bytes(b"changed")
    with pytest.raises(ValueError):
        qualification(tmp_path)
    with pytest.raises(ValidationError):
        OpeningQualification.model_validate_json(
            json.dumps(settings.model_dump(mode="json") | {"max_requests": True})
        )


async def test_api_opening_round_trip_has_durable_sse_and_no_send_endpoint(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, _ = chat_app
    app.state.config.assistant_enabled = True
    service = StubOpening()
    app.state.assistant = DesktopTasks(
        app.state.store, FakeDesktopDriver(), ScriptedProposal(), opening=service
    )
    chat = (await client.post("/api/chats", json={})).json()
    assert (await client.get("/api/bootstrap")).json()["features"]["assistant_open"] is True
    body = {"request_key": "api-opening-key", "text": "Open Notes", "mode": "open_app"}
    response = await client.post(f"/api/chats/{chat['id']}/assistant-tasks", json=body)
    assert response.status_code == 202
    identifier = response.json()["id"]
    await asyncio.wait_for(asyncio.shield(app.state.assistant.jobs[identifier]), 2)
    result = (await client.get(f"/api/assistant/tasks/{identifier}")).json()
    assert result["state"] == "complete" and result["opened_app"]["name"] == "Notes"
    assert result["fake"] is False and result["approval"] is None
    replay = await client.post(f"/api/chats/{chat['id']}/assistant-tasks", json=body)
    assert replay.json()["id"] == identifier and service.opens == 1
    events = await client.get(f"/api/assistant/tasks/{identifier}/events")
    assert "assistant.snapshot" in events.text and "Opened Notes" in events.text
    invalid = await client.post(
        f"/api/chats/{chat['id']}/assistant-tasks", json=body | {"fixture": "messages"}
    )
    assert invalid.status_code == 422 and service.proposals == 1


async def test_native_configuration_is_ignored_when_capability_is_disabled(tmp_path: Path) -> None:
    app = create_app(
        Settings(
            data_dir=tmp_path,
            dev=True,
            assistant_enabled=False,
            assistant_open_home=tmp_path / "absent-native-home",
        )
    )
    async with app.router.lifespan_context(app):
        assert app.state.assistant is None
        assert app.state.registry.capacity is None


async def test_wrong_selected_profile_fails_before_any_native_model_request(
    host: Host,
    tmp_path: Path,
) -> None:
    _, _, store = host
    registry = AsyncMock()
    service = NativeOpening(store, registry, tmp_path, config(tmp_path))
    task = DesktopTask(
        id="c" * 32,
        chat_id=CHAT,
        text="Open Notes",
        mode="open_app",
        fake=False,
        state="running",
        created_at="2026-11-08",
    )
    with pytest.raises(AppError) as error:
        await service.propose(task)
    assert error.value.code == "assistant_model"
    registry.adapter.assert_not_called()
    assert not (tmp_path / "model-budget").exists()
