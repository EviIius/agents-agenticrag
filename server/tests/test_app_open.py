import asyncio
import hashlib
import json
from pathlib import Path
from typing import Any, Literal
from unittest.mock import AsyncMock, patch

import pytest
from pydantic import ValidationError

from app.assistant.app_open import (
    APPS,
    PROMPT,
    NativeAppOpener,
    OpenDecision,
    OpenReceipt,
    perform_open,
    prompt_hash,
    propose_open,
)
from app.assistant.mac_probe import ProbeFailure
from app.providers.base import ChatRequest


def receipt(app: Literal["notes", "messages"] = "notes") -> dict[str, Any]:
    return dict(
        protocol=1,
        app=app,
        status="ok",
        bundle_id=APPS[app][0],
        bundle_path=APPS[app][1],
        pid=345,
        foreground_pid=345,
    )


@pytest.mark.parametrize(
    "value",
    [
        {"action": "open_app", "app": "terminal"},
        {"action": "open_app", "app": None},
        {"action": "refuse", "app": "notes"},
        {"action": "type_text", "app": "messages"},
        {"action": "open_app", "app": "notes", "script": "arbitrary"},
    ],
)
def test_decision_rejects_unavailable_or_extra_operations(value: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        OpenDecision.model_validate(value)


@pytest.mark.parametrize(
    "change",
    [
        {"bundle_id": "com.apple.Terminal"},
        {"bundle_path": "/tmp/Notes.app"},
        {"foreground_pid": 346},
        {"status": "failed"},
        {"pid": True},
        {"text": "No private text is accepted"},
    ],
)
def test_receipt_requires_real_exact_foreground_identity(change: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        OpenReceipt.model_validate(receipt() | change)


async def test_proposal_preserves_user_settings_and_never_executes() -> None:
    adapter = AsyncMock()
    adapter.complete_json.return_value = {"action": "open_app", "app": "notes"}
    settings = ChatRequest("installed-id", [], {"top_p": 0.7}, 32768, "low")
    decision = await propose_open(adapter, settings, "Bring Notes to the front.")
    assert decision == OpenDecision(action="open_app", app="notes")
    request = adapter.complete_json.call_args.args[0]
    assert request.params == settings.params and request.params is not settings.params
    assert request.reasoning == "low" and request.context_length == 32768
    assert request.messages[0].content == PROMPT
    assert request.messages[1].content == "Bring Notes to the front."
    assert settings.messages == []
    assert request.json_schema == OpenDecision.model_json_schema()
    assert len(prompt_hash()) == 64


@pytest.mark.parametrize("task", [" ", "x" * 4001, "猫" * 1334])
async def test_oversized_or_empty_task_does_not_call_model(task: str) -> None:
    adapter = AsyncMock()
    with pytest.raises(ProbeFailure):
        await propose_open(adapter, ChatRequest("id", []), task)
    adapter.complete_json.assert_not_called()


async def test_invalid_model_output_is_not_retried() -> None:
    adapter = AsyncMock()
    adapter.complete_json.return_value = {"action": "send", "text": "hello"}
    with pytest.raises(ProbeFailure):
        await propose_open(adapter, ChatRequest("id", []), "Open Notes")
    assert adapter.complete_json.call_count == 1


async def test_refusal_and_wrong_target_never_claim_success() -> None:
    opener = AsyncMock()
    with pytest.raises(ProbeFailure):
        await perform_open(opener, OpenDecision(action="refuse", app=None))
    opener.open.assert_not_called()
    opener.open.return_value = OpenReceipt.model_validate(receipt("messages"))
    with pytest.raises(ProbeFailure):
        await perform_open(opener, OpenDecision(action="open_app", app="notes"))
    opener.open.return_value = OpenReceipt.model_validate(receipt())
    result = await perform_open(opener, OpenDecision(action="open_app", app="notes"))
    assert result.app == "notes" and result.pid == result.foreground_pid


@pytest.mark.parametrize("bad_build", ["changed", "symlink"])
async def test_unreviewed_executable_is_not_spawned(tmp_path: Path, bad_build: str) -> None:
    executable = tmp_path / "opener"
    executable.write_bytes(b"reviewed")
    digest = hashlib.sha256(executable.read_bytes()).hexdigest()
    if bad_build == "changed":
        executable.write_bytes(b"changed")
    else:
        link = tmp_path / "link"
        link.symlink_to(executable)
        executable = link
    with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as spawn:
        with pytest.raises(ProbeFailure):
            await NativeAppOpener(executable, digest).open("notes")
    spawn.assert_not_called()


class Process:
    def __init__(self, output: bytes, hold: bool = False) -> None:
        self.output = output
        self.returncode: int | None = None
        self.hold = hold
        self.active = asyncio.Event()
        self.killed = False
        self.reaped = False

    async def communicate(self) -> tuple[bytes, bytes]:
        self.active.set()
        if self.hold:
            await asyncio.Event().wait()
        self.returncode = 0
        return self.output, b""

    def kill(self) -> None:
        self.killed = True
        self.returncode = -9

    async def wait(self) -> int:
        self.reaped = True
        return self.returncode or 0


@pytest.mark.parametrize(
    "output", [b"not json", b"x" * 2001, json.dumps(receipt("messages")).encode()]
)
async def test_bad_helper_receipt_refused(tmp_path: Path, output: bytes) -> None:
    executable = tmp_path / "opener"
    executable.write_bytes(b"reviewed")
    opener = NativeAppOpener(executable, hashlib.sha256(b"reviewed").hexdigest())
    process = Process(output)
    with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock, return_value=process):
        with pytest.raises(ProbeFailure):
            await opener.open("notes")


async def test_cancellation_reaps_owned_native_opener(tmp_path: Path) -> None:
    executable = tmp_path / "opener"
    executable.write_bytes(b"reviewed")
    opener = NativeAppOpener(executable, hashlib.sha256(b"reviewed").hexdigest())
    process = Process(b"", hold=True)
    with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock, return_value=process):
        task = asyncio.create_task(opener.open("notes"))
        await process.active.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    assert process.killed and process.reaped
