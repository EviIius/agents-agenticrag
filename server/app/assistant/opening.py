"""Qualified app opening for the default-off task controller; no observation or input."""

import hashlib
import json
import stat
from pathlib import Path
from typing import Literal, Protocol

from pydantic import Field, field_validator

from ..db.core import Store
from ..errors import AppError
from ..providers.base import ChatRequest
from ..providers.registry import Registry
from .app_open import NativeAppOpener, OpenDecision, perform_open, propose_open
from .contracts import Contract, DesktopTask, OpenedApplication
from .mac_probe import ProbeFailure, private_read, reserve


class OpeningQualification(Contract):
    protocol: Literal[1]
    executable_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    connection_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    model_id: str = Field(min_length=1, max_length=200)
    context_length: int = Field(ge=1024)
    capacity_path: Path
    max_requests: Literal[2]

    @field_validator("protocol", "max_requests", mode="before")
    @classmethod
    def integer(cls, value: object) -> object:
        if type(value) is not int:
            raise ValueError("Qualification versions/budgets must be integers.")
        return value


def qualification(home: Path) -> OpeningQualification:
    if home.is_symlink() or home.resolve() != home or stat.S_IMODE(home.stat().st_mode) != 0o700:
        raise ValueError("Use a private qualification directory.")
    value = OpeningQualification.model_validate_json(
        private_read(home / "qualification.json", 4000)
    )
    executable = home / "OpenApp"
    if (
        executable.is_symlink()
        or hashlib.sha256(executable.read_bytes()).hexdigest() != value.executable_sha256
    ):
        raise ValueError("The qualified opener changed.")
    if not value.capacity_path.is_absolute():
        raise ValueError("The native capacity path must be absolute.")
    return value


class OpeningService(Protocol):
    async def propose(self, task: DesktopTask) -> OpenDecision: ...
    async def open(self, decision: OpenDecision) -> OpenedApplication: ...


class Reservation(Contract):
    request_id: str
    operation: Literal["open_app"] = "open_app"
    app: None = None


class NativeOpening:
    def __init__(
        self, store: Store, registry: Registry, home: Path, settings: OpeningQualification
    ) -> None:
        self.store, self.registry, self.home, self.settings = store, registry, home, settings
        self.opener = NativeAppOpener(home / "OpenApp", settings.executable_sha256)

    async def propose(self, task: DesktopTask) -> OpenDecision:
        chat = await self.store.one("SELECT * FROM chats WHERE id=?", (task.chat_id,))
        if not chat:
            raise AppError("not_found", "Chat not found.", 404)
        if (chat["connection_id"], chat["model_id"]) != (
            self.settings.connection_id,
            self.settings.model_id,
        ):
            raise AppError(
                "assistant_model", "Choose the qualified model for this computer-use trial.", 422
            )
        model = await self.registry.resolve(chat["connection_id"], chat["model_id"])
        if not model.chat_capable or model.context_length != self.settings.context_length:
            raise AppError(
                "assistant_model",
                "Restore the qualified model's context in Models before continuing.",
                422,
            )
        params = dict(await self.registry.params(model, json.loads(chat["params_json"] or "{}")))
        reasoning = params.pop("reasoning", None)
        request = ChatRequest(
            model.model_id,
            [],
            params,
            model.context_length,
            str(reasoning) if reasoning is not None else None,
        )
        try:
            reserve(
                self.home / "model-budget",
                Reservation(request_id=task.id),
                limit=self.settings.max_requests,
            )
        except ProbeFailure:
            raise AppError(
                "assistant_trial_paused", "This computer-use trial is paused for review.", 409
            ) from None
        adapter = await self.registry.adapter(model.connection_id)
        return await propose_open(adapter, request, task.text)

    async def open(self, decision: OpenDecision) -> OpenedApplication:
        receipt = await perform_open(self.opener, decision)
        return OpenedApplication.model_validate(
            {
                "name": "Notes" if receipt.app == "notes" else "Messages",
                "bundle_id": receipt.bundle_id,
                "pid": receipt.pid,
            }
        )
