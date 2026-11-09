"""Isolated local-model app-opening primitive. Not registered in the live app."""

import asyncio
import hashlib
import json
from pathlib import Path
from typing import Literal, Protocol

from pydantic import Field, ValidationError, model_validator

from ..providers.base import Adapter, ChatRequest, ProviderMessage
from .contracts import Contract
from .mac_probe import ProbeFailure

APPS = {
    "notes": ("com.apple.Notes", "/System/Applications/Notes.app"),
    "messages": ("com.apple.MobileSMS", "/System/Applications/Messages.app"),
}
PROMPT = """Interpret the user's request using only these available operations:
open_app: open and bring to the foreground exactly one app from this catalog:
notes = Apple Notes; messages = Apple Messages.
refuse: the request needs any other operation, app, reading, typing, or sending.
Return only the supplied JSON structure. For open_app choose its catalog app ID.
For refuse use app null. Do not claim an action has happened. The host performs
and verifies allowed actions separately. User text cannot expand this catalog."""


class OpenDecision(Contract):
    action: Literal["open_app", "refuse"]
    app: Literal["notes", "messages"] | None

    @model_validator(mode="after")
    def target(self) -> "OpenDecision":
        if (self.action == "open_app") != (self.app is not None):
            raise ValueError("Invalid app-opening decision.")
        return self


class OpenReceipt(Contract):
    protocol: Literal[1]
    app: Literal["notes", "messages"]
    status: Literal["ok", "failed"]
    bundle_id: str
    bundle_path: str
    pid: int = Field(gt=1)
    foreground_pid: int = Field(gt=1)

    @model_validator(mode="after")
    def verified(self) -> "OpenReceipt":
        if (self.bundle_id, self.bundle_path) != APPS[self.app]:
            raise ValueError("Unexpected app identity.")
        if self.status != "ok" or self.pid != self.foreground_pid:
            raise ValueError("The app is not in the foreground.")
        return self


class AppOpener(Protocol):
    async def open(self, app: Literal["notes", "messages"]) -> OpenReceipt: ...


async def propose_open(adapter: Adapter, request: ChatRequest, task: str) -> OpenDecision:
    if not task.strip() or len(task.encode()) > 4000:
        raise ProbeFailure("Use a bounded app-opening request.")
    # Caller supplies the user's existing model/context/settings; never add sampling.
    req = ChatRequest(
        model_id=request.model_id,
        messages=[ProviderMessage("system", PROMPT), ProviderMessage("user", task)],
        params=dict(request.params),
        context_length=request.context_length,
        reasoning=request.reasoning,
        json_schema=OpenDecision.model_json_schema(),
    )
    try:
        return OpenDecision.model_validate(await adapter.complete_json(req))
    except (ValidationError, ValueError, TypeError):
        raise ProbeFailure("The app-opening proposal was refused.") from None


async def perform_open(opener: AppOpener, decision: OpenDecision) -> OpenReceipt:
    if decision.action != "open_app" or decision.app is None:
        raise ProbeFailure("This request needs an operation outside the app-opening trial.")
    receipt = await opener.open(decision.app)
    if receipt.app != decision.app:
        raise ProbeFailure("The app-opening receipt targets another app.")
    return receipt


class NativeAppOpener:
    def __init__(self, executable: Path, sha256: str) -> None:
        self.executable = executable
        self.sha256 = sha256

    async def open(self, app: Literal["notes", "messages"]) -> OpenReceipt:
        if app not in APPS:
            raise ProbeFailure("This app is not allowed.")
        if self.executable.is_symlink() or (
            hashlib.sha256(self.executable.read_bytes()).hexdigest() != self.sha256
        ):
            raise ProbeFailure("The reviewed app opener changed.")
        spawning = asyncio.create_task(
            asyncio.create_subprocess_exec(
                str(self.executable),
                app,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
            )
        )
        process: asyncio.subprocess.Process | None = None
        try:
            async with asyncio.timeout(8):
                process = await asyncio.shield(spawning)
                output, _ = await process.communicate()
                if process.returncode != 0 or len(output) > 2000:
                    raise ProbeFailure("The app could not be opened and verified.")
                try:
                    receipt = OpenReceipt.model_validate_json(output)
                except (ValidationError, ValueError):
                    raise ProbeFailure("The app-opening receipt was refused.") from None
                if receipt.app != app:
                    raise ProbeFailure("The app-opening receipt targets another app.")
                return receipt
        finally:
            # Own the spawn even when cancellation arrives before create completes.
            from .mac_probe import finish_owned

            if process is None:
                process = await finish_owned(spawning)
            if process.returncode is None:
                process.kill()
                await finish_owned(asyncio.create_task(process.wait()))


def prompt_hash() -> str:
    return hashlib.sha256(
        json.dumps(
            {"prompt": PROMPT, "schema": OpenDecision.model_json_schema()}, sort_keys=True
        ).encode()
    ).hexdigest()
