"""Private selected-container metadata; no bodies or qualified conversation claims."""

import asyncio
import time
from pathlib import Path
from typing import Literal

from pydantic import Field, ValidationError, field_validator, model_validator

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


class MetadataRequest(Contract):
    protocol: Literal[3] = 3
    request_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    operation: Literal["inspect_metadata"] = "inspect_metadata"
    app: Literal["messages"] = "messages"
    expires_at: float = Field(allow_inf_nan=False)

    @field_validator("protocol", mode="before")
    @classmethod
    def version(cls, value: object) -> object:
        if type(value) is not int:
            raise ValueError("Invalid protocol version.")
        return value


CAPS = {
    "AXIdentifier": 200,
    "AXDescription": 1000,
    "AXHelp": 1000,
    "AXTitle": 200,
    "AXRoleDescription": 200,
    "AXSubrole": 200,
    "AXDOMIdentifier": 200,
}


class MetadataItem(Contract):
    path: tuple[int, ...] = Field(min_length=1, max_length=8)
    role: Literal["AXGroup", "AXTextArea"]
    fields: dict[str, str]
    custom_content_available: bool
    attributed_range_available: bool
    url_available: bool
    linked_elements_available: bool
    selected_available: bool

    @field_validator("path")
    @classmethod
    def indices(cls, value: tuple[int, ...]) -> tuple[int, ...]:
        return CandidateArea.indices(value)

    @field_validator("fields")
    @classmethod
    def byte_caps(cls, value: dict[str, str]) -> dict[str, str]:
        if value.keys() != CAPS.keys() or any(
            len(text.encode()) > CAPS[key] for key, text in value.items()
        ):
            raise ValueError("Unexpected or oversized metadata.")
        return value


class MetadataSlice(Contract):
    access: Literal["read_only"]
    qualification: Literal["unqualified"]
    boundary: tuple[int, ...] = Field(min_length=1, max_length=5)
    items: tuple[MetadataItem, ...] = Field(min_length=4, max_length=25)

    @model_validator(mode="after")
    def bounded(self) -> "MetadataSlice":
        if any(type(i) is not int or not 0 <= i < 32 for i in self.boundary):
            raise ValueError("Invalid pane boundary.")
        areas = [item.path for item in self.items if item.role == "AXTextArea"]
        paths = [item.path for item in self.items]
        expected = [self.boundary]
        for path in areas:
            expected.extend([path[:-2], path[:-1], path])
        if (
            not 1 <= len(areas) <= 8
            or paths != expected
            or len(set(paths)) != len(paths)
            or any(
                len(path) != len(self.boundary) + 3
                or path[: len(self.boundary)] != self.boundary
                or path[-2:] != (0, 0)
                for path in areas
            )
            or any(
                item.role == "AXGroup"
                and not len(self.boundary) <= len(item.path) <= len(self.boundary) + 2
                for item in self.items
            )
            or sum(len(text.encode()) for item in self.items for text in item.fields.values())
            > 16_000
        ):
            raise ValueError("Unexpected selected-container metadata.")
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


class MetadataReply(Contract):
    protocol: Literal[3]
    request_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    operation: Literal["inspect_metadata"]
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
    snapshot: MetadataSlice | None = None
    failure_stage: Stage | None = None

    @field_validator("protocol", mode="before")
    @classmethod
    def version(cls, value: object) -> object:
        return MetadataRequest.version(value)

    @model_validator(mode="after")
    def shape(self) -> "MetadataReply":
        reading = self.status == "ok"
        if reading != (self.snapshot is not None):
            raise ValueError("Unexpected private metadata.")
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


def validate_metadata(raw: bytes, request: MetadataRequest) -> MetadataReply:
    try:
        if len(raw) > 100_000:
            raise ValueError
        reply = MetadataReply.model_validate_json(raw)
        if reply.request_id != request.request_id:
            raise ValueError
        return reply
    except (ValueError, ValidationError):
        # Validation errors may embed private input: never log/chain them.
        raise ProbeFailure("The private metadata receipt was refused.") from None


async def run_metadata(
    build: Path,
    manifest_hash: str,
    directory: Path,
    request: MetadataRequest,
    *,
    approved_scope: Literal["selected-metadata-self"] | None = None,
) -> MetadataReply:
    if approved_scope != "selected-metadata-self":
        raise ProbeFailure("This private metadata requires its declared self-thread scope.")
    if not time.time() < request.expires_at <= time.time() + 15:
        raise ProbeFailure("The private metadata deadline was refused.")
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
        raise ProbeFailure("The metadata reader did not confirm completion; do not retry.")
    reply = validate_metadata(private_read(job / "response.json", 100_000), request)
    if reply.helper_pid != helper_pid(job) or reply.helper_identity != IDENTITY:
        raise ProbeFailure("The private metadata came from a different helper.")
    return reply
