"""AS1-A sealed one-shot probe transport. Not registered with the app or AS0 driver."""

import asyncio
import fcntl
import hashlib
import json
import os
import signal
import stat
import time
from pathlib import Path
from typing import Literal, Protocol

from pydantic import Field, ValidationError, field_validator, model_validator

from .contracts import Contract

IDENTITY = "dev.agenticrag.aether.desktop-trial"
APPS = {"messages": "com.apple.MobileSMS", "notes": "com.apple.Notes"}
ROLES = frozenset(
    "AXApplication AXWindow AXGroup AXSplitGroup AXScrollArea AXList AXOutline AXTable "
    "AXRow AXColumn AXCell AXTextArea AXTextField AXStaticText AXButton AXCheckBox "
    "AXRadioButton AXPopUpButton AXMenuButton AXToolbar AXTabGroup AXTab AXImage AXLink "
    "AXMenu AXMenuItem AXMenuBar AXSlider AXSplitter AXScrollBar AXSheet AXDialog "
    "AXProgressIndicator AXValueIndicator AXUnknown".split()
)
Operation = Literal["permission", "request_access", "open", "structure"]
App = Literal["messages", "notes"]


class ProbeFailure(Exception):
    """Generic status only: native content and system errors must never enter logs."""


class ProbeEnvelope(Contract):
    protocol: Literal[1] = 1
    request_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    operation: Operation
    app: App | None = None

    @field_validator("protocol", mode="before")
    @classmethod
    def version(cls, value: object) -> object:
        if type(value) is not int:
            raise ValueError("Invalid protocol version.")
        return value

    @model_validator(mode="after")
    def target(self) -> "ProbeEnvelope":
        if (self.operation in {"open", "structure"}) != (self.app is not None):
            raise ValueError("Only app operations take an app.")
        return self


class ProbeRequest(ProbeEnvelope):
    expires_at: float = Field(allow_inf_nan=False)


class RoleNode(Contract):
    path: tuple[int, ...] = Field(max_length=8)
    role: str
    children: int = Field(ge=0, le=100_000)

    @field_validator("role")
    @classmethod
    def standard_role(cls, value: str) -> str:
        if value not in ROLES:
            raise ValueError("Unknown role string.")
        return value

    @field_validator("path")
    @classmethod
    def bounded_indices(cls, value: tuple[int, ...]) -> tuple[int, ...]:
        if any(type(index) is not int or not 0 <= index < 32 for index in value):
            raise ValueError("Invalid path.")
        return value


class ProbeReply(ProbeEnvelope):
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
    bundle_id: str | None = None
    nodes: tuple[RoleNode, ...] = Field(default=(), max_length=160)
    truncated: bool = False

    @model_validator(mode="after")
    def shape(self) -> "ProbeReply":
        app_ok = self.status == "ok" and self.app is not None
        if app_ok != (self.target_pid is not None and self.bundle_id == APPS.get(self.app or "")):
            raise ValueError("Unexpected app identity.")
        if not app_ok and (self.target_pid is not None or self.bundle_id is not None):
            raise ValueError("Unexpected target.")
        reading = self.status == "ok" and self.operation == "structure"
        if reading != bool(self.nodes) or reading and self.trusted is not True:
            raise ValueError("Unexpected structure.")
        if self.operation in {"permission", "request_access"} and self.status in {
            "ok",
            "permission_required",
        }:
            if self.trusted != (self.status == "ok"):
                raise ValueError("Unexpected permission status.")
        paths: dict[tuple[int, ...], RoleNode] = {}
        for node in self.nodes:
            if node.path in paths:
                raise ValueError("Duplicate path.")
            if node.path:
                parent = paths.get(node.path[:-1])
                if parent is None or node.path[-1] >= parent.children:
                    raise ValueError("Missing parent.")
            elif paths or node.role != "AXWindow":
                raise ValueError("Expected focused window.")
            paths[node.path] = node
        if self.truncated and not reading:
            raise ValueError("Unexpected truncation.")
        return self


def private_read(path: Path, maximum: int) -> bytes:
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(descriptor, "rb") as source:
        info = os.fstat(source.fileno())
        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_uid != os.getuid()
            or stat.S_IMODE(info.st_mode) != 0o600
            or info.st_size > maximum
        ):
            raise ProbeFailure("Unsafe probe receipt.")
        data = source.read(maximum + 1)
        if len(data) > maximum:
            raise ProbeFailure("Oversized probe receipt.")
        return data


def private_write(path: Path, data: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, "wb") as target:
        target.write(data)


def verify_build(directory: Path, expected_manifest_hash: str) -> Path:
    try:
        raw = private_read(directory / "build-manifest.json", 100_000)
        if hashlib.sha256(raw).hexdigest() != expected_manifest_hash:
            raise ValueError
        manifest = json.loads(raw)
        if manifest["protocol"] != 1 or manifest["identity"] != IDENTITY:
            raise ValueError
        bundle = directory / "Aether Desktop Trial.app"
        files = manifest["files"]
        if not 2 <= len(files) <= 8:
            raise ValueError
        required = {"Contents/MacOS/DesktopTrial", "Contents/Info.plist"}
        if not required <= files.keys():
            raise ValueError
        actual = list(bundle.rglob("*"))
        if any(p.is_symlink() for p in actual) or {
            str(p.relative_to(bundle)) for p in actual if p.is_file()
        } != set(files):
            raise ValueError
        for name, digest in files.items():
            file = bundle / name
            if (
                Path(name).is_absolute()
                or ".." in Path(name).parts
                or file.is_symlink()
                or file.resolve() != file.absolute()
                or hashlib.sha256(file.read_bytes()).hexdigest() != digest
            ):
                raise ValueError
        return bundle
    except (OSError, ValueError, KeyError, TypeError, ProbeFailure):
        raise ProbeFailure("The sealed helper build changed or is unavailable.") from None


def validate_reply(raw: bytes, request: ProbeRequest) -> ProbeReply:
    try:
        if len(raw) > 100_000:
            raise ValueError
        reply = ProbeReply.model_validate_json(raw)
        if (
            reply.request_id != request.request_id
            or reply.operation != request.operation
            or reply.app != request.app
        ):
            raise ValueError
        return reply
    except (ValueError, ValidationError):
        raise ProbeFailure("The helper returned an invalid receipt.") from None


class TrialJob(Protocol):
    @property
    def request_id(self) -> str: ...

    @property
    def operation(self) -> str: ...

    @property
    def app(self) -> str | None: ...

    def model_dump_json(self) -> str: ...


def reserve(directory: Path, request: TrialJob, *, limit: int = 8) -> Path:
    if type(limit) is not int or not 1 <= limit <= 8:
        raise ProbeFailure("Invalid native trial budget.")
    if directory.is_symlink():
        raise ProbeFailure("Unsafe trial directory.")
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    if stat.S_IMODE(directory.stat().st_mode) != 0o700:
        raise ProbeFailure("Unsafe trial directory.")
    lock = os.open(directory / "ledger.lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    with os.fdopen(lock, "r+") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        ledger = directory / "ledger.json"
        records = json.loads(private_read(ledger, 20_000)) if ledger.exists() else []
        if len(records) >= limit or any(r["request_id"] == request.request_id for r in records):
            raise ProbeFailure("The native trial budget or request was already consumed.")
        job = directory / request.request_id
        job.mkdir(mode=0o700)
        private_write(job / "request.json", request.model_dump_json().encode())
        records.append(
            {"request_id": request.request_id, "operation": request.operation, "app": request.app}
        )
        temporary = directory / (request.request_id + ".ledger")
        private_write(temporary, json.dumps(records).encode())
        os.replace(temporary, ledger)
        return job


def helper_pid(job: Path) -> int:
    try:
        receipt = json.loads(private_read(job / "helper.json", 512))
        pid = receipt["pid"]
        if (
            set(receipt) != {"pid", "request_id"}
            or type(pid) is not int
            or pid <= 1
            or receipt["request_id"] != job.name
        ):
            raise ValueError
        return int(pid)
    except (OSError, ValueError, KeyError, TypeError):
        raise ProbeFailure("The helper process receipt is unavailable.") from None


async def stop_helper(process: asyncio.subprocess.Process, job: Path, executable: Path) -> None:
    uncertain = False
    try:
        private_write(job / "cancel", b"cancel")
    except FileExistsError:
        pass
    try:
        pid = helper_pid(job)
        # Inspect only this helper PID; never list or terminate user applications.
        inspector = await asyncio.create_subprocess_exec(
            "/bin/ps",
            "-p",
            str(pid),
            "-o",
            "command=",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        try:
            output, _ = await asyncio.wait_for(inspector.communicate(), 2)
        except BaseException:
            if inspector.returncode is None:
                inspector.kill()
            await inspector.wait()
            raise
        expected = f"{executable} --native-job {job}"
        if output.decode().strip() == expected:
            os.kill(pid, signal.SIGTERM)
        elif inspector.returncode == 0:
            raise ProbeFailure("The helper stop outcome is unknown.")
    except ProcessLookupError:
        pass
    except ProbeFailure:
        # A helper that has not started still sees the durable cancel marker.
        # Do not claim Stop until Launch Services has confirmed process exit.
        uncertain = (job / "helper.json").exists()
    except (OSError, TimeoutError, UnicodeError):
        uncertain = True
    try:
        await asyncio.wait_for(process.wait(), 3)
    except TimeoutError:
        process.kill()  # This is only our open -W launcher, not an app.
        await process.wait()
        raise ProbeFailure("The helper stop outcome is unknown.") from None
    if uncertain:
        raise ProbeFailure("The helper stop outcome is unknown.")


async def finish_owned[T](task: asyncio.Task[T]) -> T:
    """Repeated caller cancellation cannot abandon a process being acquired/stopped."""
    while True:
        try:
            return await asyncio.shield(task)
        except asyncio.CancelledError:
            if task.done():
                return task.result()


async def run_probe(
    build: Path,
    expected_manifest_hash: str,
    directory: Path,
    request: ProbeRequest,
    *,
    approved_scope: Literal["as1-a"] | None = None,
) -> ProbeReply:
    if approved_scope != "as1-a":
        raise ProbeFailure("AS1-A native execution requires its reviewed scope.")
    if not time.time() < request.expires_at <= time.time() + 15:
        raise ProbeFailure("The probe request expired or exceeds the deadline.")
    bundle = verify_build(build, expected_manifest_hash)
    job = reserve(directory, request)
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
        raise ProbeFailure("The helper did not confirm completion; do not retry automatically.")
    reply = validate_reply(private_read(job / "response.json", 100_000), request)
    if reply.helper_pid != helper_pid(job):
        raise ProbeFailure("The helper response came from a different process.")
    return reply
