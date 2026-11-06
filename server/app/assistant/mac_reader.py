"""AS1-B private candidate reads. Not a qualified conversation or registered tool.

Never log these models or their validation errors: candidate fields are private.
No function here infers recipient/direction or supplies data to a model/controller.
"""

import asyncio
import time
from pathlib import Path
from typing import Literal

from pydantic import Field, ValidationError, ValidationInfo, field_validator, model_validator

from .contracts import Contract
from .mac_probe import (
    IDENTITY,
    ProbeFailure,
    RoleNode,
    finish_owned,
    helper_pid,
    private_read,
    reserve,
    stop_helper,
    verify_build,
)


class ReadBoundary(Contract):
    nodes: tuple[RoleNode, ...] = Field(min_length=1, max_length=160)
    boundary: tuple[int, ...] = Field(min_length=1, max_length=7)
    paths: tuple[tuple[int, ...], ...] = Field(min_length=1, max_length=8)

    @model_validator(mode="after")
    def selection(self) -> "ReadBoundary":
        seen: dict[tuple[int, ...], RoleNode] = {}
        for node in self.nodes:
            if node.path in seen:
                raise ValueError("Duplicate boundary node.")
            if node.path:
                parent = seen.get(node.path[:-1])
                if parent is None or node.path[-1] >= parent.children:
                    raise ValueError("Invalid boundary tree.")
            elif seen or node.role != "AXWindow":
                raise ValueError("Invalid boundary window.")
            seen[node.path] = node
        group = seen.get(self.boundary)
        expected = {
            path
            for path, node in seen.items()
            if node.role == "AXTextArea" and path[: len(self.boundary)] == self.boundary
        }
        if not group or group.role != "AXGroup" or set(self.paths) != expected:
            raise ValueError("Invalid text-area boundary.")
        if len(set(self.paths)) != len(self.paths):
            raise ValueError("Duplicate candidate path.")
        return self


class ReadRequest(Contract):
    protocol: Literal[1] = 1
    request_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    operation: Literal["request_access", "read_selected"]
    app: Literal["messages"] | None = None
    expires_at: float = Field(allow_inf_nan=False)

    @field_validator("protocol", mode="before")
    @classmethod
    def version(cls, value: object) -> object:
        if type(value) is not int:
            raise ValueError("Invalid protocol.")
        return value

    @model_validator(mode="after")
    def target(self) -> "ReadRequest":
        if (self.operation == "read_selected") != (self.app is not None):
            raise ValueError("Invalid read target.")
        return self


class CandidateArea(Contract):
    path: tuple[int, ...] = Field(min_length=1, max_length=8)
    value: str = Field(max_length=4000)
    description: str = Field(max_length=1000)
    identifier: str = Field(max_length=200)
    subrole: str = Field(max_length=200)
    value_settable: Literal[False] = False

    @field_validator("path")
    @classmethod
    def indices(cls, value: tuple[int, ...]) -> tuple[int, ...]:
        if any(type(index) is not int or not 0 <= index < 32 for index in value):
            raise ValueError("Invalid candidate path.")
        return value

    @field_validator("value", "description", "identifier", "subrole")
    @classmethod
    def byte_cap(cls, value: str, info: ValidationInfo) -> str:
        # Match Swift's UTF-8 limits, including multibyte source text.
        cap = (
            4000
            if info.field_name == "value"
            else 1000
            if info.field_name == "description"
            else 200
        )
        if len(value.encode()) > cap:
            raise ValueError("Candidate attribute exceeds its byte limit.")
        return value

    @field_validator("value_settable", mode="before")
    @classmethod
    def read_only(cls, value: object) -> object:
        if value is not False:
            raise ValueError("Settable candidates are excluded.")
        return value


class CandidateSlice(Contract):
    qualification: Literal["unqualified"] = "unqualified"
    window_title: str = Field(max_length=200)
    group_identifier: str = Field(max_length=200)
    boundary: tuple[int, ...] = Field(min_length=1, max_length=7)
    items: tuple[CandidateArea, ...] = Field(min_length=1, max_length=8)
    settable_excluded: int = Field(ge=0, le=8)

    @model_validator(mode="after")
    def bounded(self) -> "CandidateSlice":
        if any(type(i) is not int or not 0 <= i < 32 for i in self.boundary):
            raise ValueError("Invalid boundary.")
        if len(self.window_title.encode()) > 200 or len(self.group_identifier.encode()) > 200:
            raise ValueError("Oversized selection attribute.")
        paths = [item.path for item in self.items]
        if len(set(paths)) != len(paths) or len(paths) + self.settable_excluded > 8:
            raise ValueError("Invalid candidate count.")
        if any(
            len(p) <= len(self.boundary) or p[: len(self.boundary)] != self.boundary for p in paths
        ):
            raise ValueError("Candidate escaped its boundary.")
        if sum(len(item.value.encode()) for item in self.items) > 16_000:
            raise ValueError("Candidate slice exceeds its byte limit.")
        return self


class ReadReply(Contract):
    protocol: Literal[1]
    request_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    operation: Literal["request_access", "read_selected"]
    app: Literal["messages"] | None
    helper_identity: Literal["dev.agenticrag.aether.desktop-trial"]
    helper_pid: int = Field(gt=1)
    status: Literal[
        "ok",
        "permission_required",
        "cancelled",
        "deadline",
        "stale_window",
        "identity_mismatch",
        "unavailable",
    ]
    trusted: bool | None = None
    target_pid: int | None = Field(default=None, gt=1)
    bundle_id: Literal["com.apple.MobileSMS"] | None = None
    candidate: CandidateSlice | None = None

    @field_validator("protocol", mode="before")
    @classmethod
    def version(cls, value: object) -> object:
        return ReadRequest.version(value)

    @model_validator(mode="after")
    def shape(self) -> "ReadReply":
        reading = self.status == "ok" and self.operation == "read_selected"
        if (self.operation == "read_selected") != (self.app == "messages"):
            raise ValueError("Unexpected target.")
        if reading != (self.candidate is not None):
            raise ValueError("Unexpected candidate content.")
        if reading:
            if self.target_pid is None or self.bundle_id is None or self.trusted is not True:
                raise ValueError("Unverified app.")
        elif self.target_pid is not None or self.bundle_id is not None:
            raise ValueError("Unexpected app content.")
        if self.status == "permission_required" and self.trusted is not False:
            raise ValueError("Unexpected permission status.")
        if self.operation == "request_access" and self.status == "ok" and self.trusted is not True:
            raise ValueError("Unexpected permission status.")
        return self


def validate_read(raw: bytes, request: ReadRequest) -> ReadReply:
    try:
        if len(raw) > 100_000:
            raise ValueError
        reply = ReadReply.model_validate_json(raw)
        if (reply.request_id, reply.operation, reply.app) != (
            request.request_id,
            request.operation,
            request.app,
        ):
            raise ValueError
        return reply
    except (ValueError, ValidationError):
        raise ProbeFailure("The private read receipt was refused.") from None


async def run_read_probe(
    build: Path,
    expected_manifest_hash: str,
    directory: Path,
    request: ReadRequest,
    *,
    approved_scope: Literal["as1-b1"] | None = None,
) -> ReadReply:
    if approved_scope != "as1-b1":
        raise ProbeFailure("AS1-B1 text access requires its reviewed scope.")
    if not time.time() < request.expires_at <= time.time() + 15:
        raise ProbeFailure("The read request expired or exceeds its deadline.")
    bundle = verify_build(build, expected_manifest_hash)
    # A non-reader build cannot accidentally satisfy this scope.
    if not (bundle / "Contents/Resources/read-boundary.json").is_file():
        raise ProbeFailure("The sealed reader boundary is missing.")
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
            asyncio.create_task(stop_helper(process, job, bundle / "Contents/MacOS/DesktopTrial"))
        )
        raise
    if process.returncode:
        raise ProbeFailure("The reader did not confirm completion; do not retry.")
    reply = validate_read(private_read(job / "response.json", 100_000), request)
    if reply.helper_pid != helper_pid(job) or reply.helper_identity != IDENTITY:
        raise ProbeFailure("The private read came from a different helper.")
    return reply
