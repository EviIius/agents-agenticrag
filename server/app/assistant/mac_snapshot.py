"""Versioned private read-only snapshots, never qualified messages or input authority."""

import asyncio
import time
from pathlib import Path
from typing import Literal

from pydantic import Field, ValidationError, ValidationInfo, field_validator, model_validator

from .contracts import Contract
from .mac_probe import (
    IDENTITY,
    ProbeFailure,
    finish_owned,
    helper_pid,
    private_read,
    reserve,
    stop_helper,
    verify_build,
)
from .mac_reader import CandidateArea


class SnapshotRequest(Contract):
    protocol: Literal[2] = 2
    request_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    operation: Literal["read_selected"] = "read_selected"
    app: Literal["messages"] = "messages"
    expires_at: float = Field(allow_inf_nan=False)

    @field_validator("protocol", mode="before")
    @classmethod
    def version(cls, value: object) -> object:
        if type(value) is not int:
            raise ValueError("Invalid protocol version.")
        return value


class SnapshotArea(Contract):
    path: tuple[int, ...] = Field(min_length=1, max_length=8)
    value: str = Field(max_length=4000)
    description: str = Field(max_length=1000)
    identifier: str = Field(max_length=200)
    subrole: str = Field(max_length=200)
    value_settable: bool  # required observed API flag; grants no input authority

    @field_validator("path")
    @classmethod
    def indices(cls, value: tuple[int, ...]) -> tuple[int, ...]:
        return CandidateArea.indices(value)

    @field_validator("value", "description", "identifier", "subrole")
    @classmethod
    def byte_cap(cls, value: str, info: ValidationInfo) -> str:
        return CandidateArea.byte_cap(value, info)


class SnapshotSlice(Contract):
    access: Literal["read_only"]
    qualification: Literal["unqualified"]
    window_title: str = Field(max_length=200)
    group_identifier: str = Field(max_length=200)
    boundary: tuple[int, ...] = Field(min_length=1, max_length=5)
    items: tuple[SnapshotArea, ...] = Field(min_length=1, max_length=8)

    @model_validator(mode="after")
    def bounded(self) -> "SnapshotSlice":
        if any(type(i) is not int or not 0 <= i < 32 for i in self.boundary):
            raise ValueError("Invalid pane boundary.")
        if len(self.window_title.encode()) > 200 or len(self.group_identifier.encode()) > 200:
            raise ValueError("Oversized selection metadata.")
        paths = [item.path for item in self.items]
        if len(set(paths)) != len(paths) or any(
            len(path) != len(self.boundary) + 3
            or path[: len(self.boundary)] != self.boundary
            or path[-2:] != (0, 0)
            for path in paths
        ):
            raise ValueError("Invalid selected text areas.")
        if sum(len(item.value.encode()) for item in self.items) > 16_000:
            raise ValueError("The snapshot exceeds its byte limit.")
        return self


Stage = Literal[
    "dispatch",
    "structure",
    "modifiability",
    "character_count",
    "bounded_range",
    "selection_metadata",
    "stability",
]


class SnapshotReply(Contract):
    protocol: Literal[2]
    request_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    operation: Literal["read_selected"]
    app: Literal["messages"]
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
    snapshot: SnapshotSlice | None = None
    failure_stage: Stage | None = None

    @field_validator("protocol", mode="before")
    @classmethod
    def version(cls, value: object) -> object:
        return SnapshotRequest.version(value)

    @model_validator(mode="after")
    def shape(self) -> "SnapshotReply":
        reading = self.status == "ok"
        if reading != (self.snapshot is not None):
            raise ValueError("Unexpected private snapshot.")
        if reading:
            if (
                self.target_pid is None
                or self.bundle_id is None
                or self.trusted is not True
                or self.failure_stage is not None
            ):
                raise ValueError("Unverified app state.")
        elif self.target_pid is not None or self.bundle_id is not None:
            raise ValueError("Unexpected app data on refusal.")
        if self.status == "permission_required" and self.trusted is not False:
            raise ValueError("Unexpected permission state.")
        return self


def validate_snapshot(raw: bytes, request: SnapshotRequest) -> SnapshotReply:
    try:
        if len(raw) > 100_000:
            raise ValueError
        reply = SnapshotReply.model_validate_json(raw)
        if reply.request_id != request.request_id:
            raise ValueError
        return reply
    except (ValueError, ValidationError):
        # Validation errors may embed private input: never log/chain them.
        raise ProbeFailure("The private snapshot receipt was refused.") from None


async def run_snapshot(
    build: Path,
    manifest_hash: str,
    directory: Path,
    request: SnapshotRequest,
    *,
    approved_scope: Literal["readonly-self"] | None = None,
) -> SnapshotReply:
    if approved_scope != "readonly-self":
        raise ProbeFailure("This private snapshot requires its declared self-thread scope.")
    if not time.time() < request.expires_at <= time.time() + 15:
        raise ProbeFailure("The private snapshot deadline was refused.")
    bundle = verify_build(build, manifest_hash)
    if not (bundle / "Contents/Resources/read-boundary.json").is_file():
        raise ProbeFailure("The sealed pane boundary is missing.")
    job = reserve(directory, request, limit=2)
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
        raise ProbeFailure("The private reader did not confirm completion; do not retry.")
    reply = validate_snapshot(private_read(job / "response.json", 100_000), request)
    if reply.helper_pid != helper_pid(job) or reply.helper_identity != IDENTITY:
        raise ProbeFailure("The private snapshot came from a different helper.")
    return reply
