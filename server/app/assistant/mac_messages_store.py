"""Isolated exact-build Messages store trial. Never registered or supplied to a model."""

import asyncio
import hashlib
import json
import re
import time
from pathlib import Path
from typing import Literal

from pydantic import Field, ValidationError, field_validator, model_validator

from .contracts import Contract
from .mac_probe import ProbeFailure, finish_owned, helper_pid, private_read, reserve, stop_helper

STORE_IDENTITY = "dev.agenticrag.aether.messages-reader"


class StoreRequest(Contract):
    protocol: Literal[1] = 1
    request_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    operation: Literal["resolve_self", "read_thread"]
    expires_at: float = Field(allow_inf_nan=False)

    @property
    def app(self) -> None:
        return None  # shared ledger protocol only; no caller-selectable app/path/address

    @field_validator("protocol", mode="before")
    @classmethod
    def version(cls, value: object) -> object:
        if type(value) is not int:
            raise ValueError("Invalid protocol version.")
        return value


class StoreTarget(Contract):
    chat_guid: str = Field(min_length=1, max_length=200)
    address: str = Field(min_length=1, max_length=200)
    service: Literal["iMessage", "SMS", "RCS"]
    handle_row_id: int = Field(gt=0, le=2**63 - 1)

    @field_validator("chat_guid", "address")
    @classmethod
    def byte_cap(cls, value: str) -> str:
        if len(value.encode()) > 200 or "\0" in value:
            raise ValueError("Oversized or invalid identity.")
        return value

    @field_validator("address")
    @classmethod
    def exact_address(cls, value: str) -> str:
        if not re.fullmatch(r"\+[1-9][0-9]{6,14}", value) and not re.fullmatch(
            r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?\.[A-Za-z]{2,63}",
            value,
        ):
            raise ValueError("An exact address is required.")
        return value


class StoreMessage(Contract):
    guid: str = Field(min_length=1, max_length=200)
    row_id: int = Field(gt=0, le=2**63 - 1)
    from_me: bool
    sender_handle: str = Field(max_length=200)
    date: int = Field(gt=0, le=2**63 - 1)
    text: str = Field(min_length=1, max_length=4000)

    @field_validator("guid", "sender_handle", "text")
    @classmethod
    def bytes_and_format(cls, value: str) -> str:
        if "\0" in value or "\ufffc" in value:
            raise ValueError("Unsupported message format.")
        return value

    @model_validator(mode="after")
    def caps(self) -> "StoreMessage":
        if len(self.text.encode()) > 4000 or any(
            len(value.encode()) > 200 for value in (self.guid, self.sender_handle)
        ):
            raise ValueError("Oversized private record.")
        return self


class StoreSlice(Contract):
    access: Literal["read_only"]
    qualification: Literal["unqualified"]
    target: StoreTarget
    messages: tuple[StoreMessage, ...] = Field(min_length=1, max_length=8)
    latest_incoming_guid: str | None = Field(max_length=200)

    @model_validator(mode="after")
    def bound(self) -> "StoreSlice":
        messages = self.messages
        latest = next((m.guid for m in messages if not m.from_me), None)
        order = [(m.date, m.row_id) for m in messages]
        if (
            len({m.guid for m in messages}) != len(messages)
            or len({m.row_id for m in messages}) != len(messages)
            or order != sorted(order, reverse=True)
            or sum(len(m.text.encode()) for m in messages) > 16_000
            or any(not m.from_me and m.sender_handle != self.target.address for m in messages)
            or self.latest_incoming_guid != latest
        ):
            raise ValueError("The private source binding was refused.")
        return self


class StoreReply(Contract):
    protocol: Literal[1]
    request_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    operation: Literal["resolve_self", "read_thread"]
    helper_identity: Literal["dev.agenticrag.aether.messages-reader"]
    helper_pid: int = Field(gt=1)
    status: Literal[
        "ok",
        "invalid",
        "permission_required",
        "unavailable",
        "unsupported_schema",
        "unsupported_message",
        "ambiguous_recipient",
        "no_conversation",
        "stale_selection",
        "deadline",
        "cancelled",
    ]
    target: StoreTarget | None = None
    snapshot: StoreSlice | None = None

    @field_validator("protocol", mode="before")
    @classmethod
    def version(cls, value: object) -> object:
        return StoreRequest.version(value)

    @model_validator(mode="after")
    def shape(self) -> "StoreReply":
        resolving = self.status == "ok" and self.operation == "resolve_self"
        reading = self.status == "ok" and self.operation == "read_thread"
        if resolving != (self.target is not None) or reading != (self.snapshot is not None):
            raise ValueError("Unexpected private store data.")
        return self


def validate_store(raw: bytes, request: StoreRequest) -> StoreReply:
    try:
        if len(raw) > 100_000:
            raise ValueError
        result = StoreReply.model_validate_json(raw)
        if result.request_id != request.request_id or result.operation != request.operation:
            raise ValueError
        return result
    except (ValueError, ValidationError):
        raise ProbeFailure("The private store receipt was refused.") from None


def verify_store_build(directory: Path, digest: str) -> Path:
    try:
        raw = private_read(directory / "build-manifest.json", 50_000)
        manifest = json.loads(raw)
        if hashlib.sha256(raw).hexdigest() != digest or manifest["identity"] != STORE_IDENTITY:
            raise ValueError
        bundle = directory / "Aether Messages Reader.app"
        files = manifest["files"]
        if (
            type(manifest["protocol"]) is not int
            or manifest["protocol"] != 1
            or not 2 <= len(files) <= 5
        ):
            raise ValueError
        if not {"Contents/MacOS/MessagesReader", "Contents/Info.plist"} <= files.keys():
            raise ValueError
        actual = list(bundle.rglob("*"))
        if any(p.is_symlink() for p in actual) or {
            str(p.relative_to(bundle)) for p in actual if p.is_file()
        } != set(files):
            raise ValueError
        for name, sha in files.items():
            file = bundle / name
            if (
                Path(name).is_absolute()
                or ".." in Path(name).parts
                or file.resolve() != file.absolute()
                or hashlib.sha256(file.read_bytes()).hexdigest() != sha
            ):
                raise ValueError
        return bundle
    except (OSError, ValueError, KeyError, TypeError):
        raise ProbeFailure("The sealed Messages reader changed or is unavailable.") from None


async def run_store(
    build: Path,
    manifest_hash: str,
    directory: Path,
    request: StoreRequest,
    *,
    approved_scope: Literal["messages-store-self"] | None = None,
) -> StoreReply:
    if approved_scope != "messages-store-self":
        raise ProbeFailure("This private store receipt requires its declared self-thread scope.")
    if not time.time() < request.expires_at <= time.time() + 15:
        raise ProbeFailure("The private store receipt deadline was refused.")
    bundle = verify_store_build(build, manifest_hash)
    job = reserve(directory, request, limit=3)
    spawning = asyncio.create_task(
        asyncio.create_subprocess_exec(
            "/usr/bin/open",
            "-n",
            "-W",
            "-a",
            str(bundle),
            "--args",
            "--native-job",
            str(job),
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
    )
    process: asyncio.subprocess.Process | None = None
    try:
        process = await asyncio.shield(spawning)
        await asyncio.wait_for(process.wait(), max(0.01, request.expires_at - time.time()))
    except (TimeoutError, asyncio.CancelledError):
        if process is None:
            process = await finish_owned(spawning)
        await finish_owned(
            asyncio.create_task(stop_helper(process, job, bundle / "Contents/MacOS/MessagesReader"))
        )
        raise
    if process.returncode:
        raise ProbeFailure("The store reader did not confirm completion; do not retry.")
    reply = validate_store(private_read(job / "response.json", 100_000), request)
    if reply.helper_pid != helper_pid(job) or reply.helper_identity != STORE_IDENTITY:
        raise ProbeFailure("The private store receipt came from a different helper.")
    return reply
