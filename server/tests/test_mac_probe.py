"""AS1-A offline tests: invented receipts and fake processes, never macOS access."""

import asyncio
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, cast

import pytest
from pydantic import ValidationError

from app.assistant import mac_probe as probe


def request(**changes: Any) -> probe.ProbeRequest:
    return probe.ProbeRequest.model_validate(
        {
            "request_id": "a" * 32,
            "operation": "structure",
            "app": "messages",
            "expires_at": time.time() + 10,
            **changes,
        }
    )


def response(job: probe.ProbeRequest, **changes: Any) -> bytes:
    return json.dumps(
        {
            "protocol": 1,
            "request_id": job.request_id,
            "operation": job.operation,
            "app": job.app,
            "helper_identity": probe.IDENTITY,
            "helper_pid": 12345,
            "status": "ok",
            "trusted": True,
            "target_pid": 23456,
            "bundle_id": probe.APPS[job.app or "messages"],
            "nodes": [{"path": [], "role": "AXWindow", "children": 0}],
            **changes,
        }
    ).encode()


@pytest.fixture
def sealed(tmp_path: Path) -> tuple[Path, str]:
    build = tmp_path / "build"
    build.mkdir(mode=0o700)
    bundle = build / "Aether Desktop Trial.app"
    files = {
        "Contents/MacOS/DesktopTrial": b"synthetic executable",
        "Contents/Info.plist": b"synthetic plist",
    }
    for name, raw in files.items():
        file = bundle / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(raw)
    raw = json.dumps(
        {
            "protocol": 1,
            "identity": probe.IDENTITY,
            "files": {name: hashlib.sha256(value).hexdigest() for name, value in files.items()},
        }
    ).encode()
    probe.private_write(build / "build-manifest.json", raw)
    return build, hashlib.sha256(raw).hexdigest()


@pytest.mark.parametrize(
    "change",
    [
        {"protocol": True},
        {"app": "safari"},
        {"operation": "send"},
        {"operation": "permission"},
        {"app": None},
        {"script": "untrusted"},
        {"expires_at": float("inf")},
    ],
)
def test_request_rejects_extra_operations_targets_and_fields(change: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        request(**change)


@pytest.mark.parametrize(
    "changes",
    [
        {"helper_identity": "another.app"},
        {"request_id": "b" * 32},
        {"app": "notes"},
        {"bundle_id": "another.app"},
        {"target_pid": None},
        {"protocol": True},
        {"title": "private synthetic title"},
        {"nodes": [{"path": [], "role": "private synthetic role", "children": 0}]},
        {"nodes": [{"path": [0], "role": "AXWindow", "children": 0}]},
        {"nodes": [{"path": [], "role": "AXWindow", "children": 0}] * 2},
        {
            "nodes": [
                {"path": [], "role": "AXWindow", "children": 0},
                {"path": [0], "role": "AXStaticText", "children": 0},
            ]
        },
        {"trusted": False},
        {"nodes": []},
    ],
)
def test_reply_refuses_wrong_identity_private_text_and_forged_trees(
    changes: dict[str, Any],
) -> None:
    job = request()
    with pytest.raises(probe.ProbeFailure) as error:
        probe.validate_reply(response(job, **changes), job)
    assert "private synthetic" not in str(error.value)


def test_reply_accepts_bounded_role_only_tree_and_permission_negative_control() -> None:
    job = request()
    reply = probe.validate_reply(response(job), job)
    assert reply.nodes[0].role == "AXWindow" and reply.target_pid == 23456
    permission = request(operation="permission", app=None)
    reply = probe.validate_reply(
        response(
            permission,
            status="permission_required",
            trusted=False,
            target_pid=None,
            bundle_id=None,
            nodes=[],
        ),
        permission,
    )
    assert reply.trusted is False
    with pytest.raises(probe.ProbeFailure):
        probe.validate_reply(b" " * 100_001, job)


@pytest.mark.parametrize("alteration", ["binary", "extra", "symlink", "manifest"])
def test_seal_refuses_changed_and_added_build_files(
    sealed: tuple[Path, str],
    alteration: str,
) -> None:
    build, digest = sealed
    bundle = probe.verify_build(build, digest)
    if alteration == "binary":
        (bundle / "Contents/MacOS/DesktopTrial").write_bytes(b"changed")
    elif alteration == "extra":
        (bundle / "extra").write_bytes(b"added")
    elif alteration == "symlink":
        file = bundle / "Contents/Info.plist"
        backup = build / "elsewhere"
        file.rename(backup)
        file.symlink_to(backup)
    else:
        digest = "0" * 64
    with pytest.raises(probe.ProbeFailure):
        probe.verify_build(build, digest)


def test_private_files_refuse_replacement_symlinks_oversize_and_broad_permissions(
    tmp_path: Path,
) -> None:
    file = tmp_path / "private"
    probe.private_write(file, b"synthetic")
    assert probe.private_read(file, 20) == b"synthetic"
    with pytest.raises(FileExistsError):
        probe.private_write(file, b"replacement")
    with pytest.raises(probe.ProbeFailure):
        probe.private_read(file, 1)
    os.chmod(file, 0o644)
    with pytest.raises(probe.ProbeFailure):
        probe.private_read(file, 20)
    linked = tmp_path / "symlink"
    linked.symlink_to(file)
    with pytest.raises(OSError):
        probe.private_read(linked, 20)


def test_native_trial_reservations_are_durable_single_use_and_at_most_eight(tmp_path: Path) -> None:
    root = tmp_path / "trial"
    job = request()
    directory = probe.reserve(root, job)
    assert directory.stat().st_mode & 0o777 == 0o700
    assert (
        json.loads(probe.private_read(directory / "request.json", 4096))["request_id"]
        == job.request_id
    )
    with pytest.raises(probe.ProbeFailure):
        probe.reserve(root, job)
    for index in range(1, 8):
        probe.reserve(root, request(request_id=f"{index:032x}"))
    with pytest.raises(probe.ProbeFailure):
        probe.reserve(root, request(request_id="9" * 32))
    os.chmod(root, 0o755)
    with pytest.raises(probe.ProbeFailure):
        probe.reserve(root, request(request_id="f" * 32))


class Process:
    def __init__(self, done: bool = False, output: bytes = b"") -> None:
        self.returncode: int | None = 0 if done else None
        self.exited = asyncio.Event()
        self.output = output
        self.killed = False
        if done:
            self.exited.set()

    async def wait(self) -> int:
        await self.exited.wait()
        return self.returncode or 0

    async def communicate(self) -> tuple[bytes, bytes]:
        self.returncode = 0
        return self.output, b""

    def kill(self) -> None:
        self.killed = True
        self.returncode = -9
        self.exited.set()


async def test_default_denied_and_expired_requests_never_spawn(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def forbidden(*args: object, **kwargs: object) -> None:
        pytest.fail("An unapproved/expired job attempted native execution.")

    monkeypatch.setattr(asyncio, "create_subprocess_exec", forbidden)
    with pytest.raises(probe.ProbeFailure, match="reviewed scope"):
        await probe.run_probe(tmp_path, "", tmp_path, request())
    with pytest.raises(probe.ProbeFailure, match="expired"):
        await probe.run_probe(
            tmp_path, "", tmp_path, request(expires_at=time.time() - 1), approved_scope="as1-a"
        )


async def test_success_uses_fixed_launch_command_and_checks_matching_process_receipt(
    sealed: tuple[Path, str],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    build, digest = sealed
    job = request()
    calls = []

    async def spawn(*args: str, **kwargs: object) -> Process:
        calls.append(args)
        directory = Path(args[-1])
        probe.private_write(
            directory / "helper.json",
            json.dumps({"request_id": job.request_id, "pid": 12345}).encode(),
        )
        probe.private_write(directory / "response.json", response(job))
        return Process(done=True)

    monkeypatch.setattr(asyncio, "create_subprocess_exec", spawn)
    reply = await probe.run_probe(build, digest, tmp_path / "trial", job, approved_scope="as1-a")
    assert reply.status == "ok" and len(calls) == 1
    assert calls[0][:5] == (
        "/usr/bin/open",
        "-n",
        "-W",
        "-a",
        str(build / "Aether Desktop Trial.app"),
    )


@pytest.mark.parametrize("when", ["running", "spawning", "deadline", "repeat_cancel"])
async def test_stop_owns_late_spawn_and_only_signals_verified_helper(
    sealed: tuple[Path, str],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    when: str,
) -> None:
    build, digest = sealed
    job = request(expires_at=time.time() + (0.05 if when == "deadline" else 10))
    child = Process()
    launched = asyncio.Event()
    inspecting = asyncio.Event()
    release = asyncio.Event()
    signals = []
    directory = tmp_path / "trial" / job.request_id

    async def spawn(*args: str, **kwargs: object) -> Process:
        if args[0] == "/bin/ps":
            inspecting.set()
            if when == "repeat_cancel":
                await release.wait()
            executable = build / "Aether Desktop Trial.app/Contents/MacOS/DesktopTrial"
            command = f"{executable} --native-job {directory}"
            return Process(done=True, output=command.encode())
        probe.private_write(
            directory / "helper.json",
            json.dumps({"request_id": job.request_id, "pid": 12345}).encode(),
        )
        launched.set()
        if when == "spawning":
            await release.wait()
        return child

    def stop(pid: int, sig: int) -> None:
        signals.append((pid, sig))
        child.returncode = -15
        child.exited.set()

    monkeypatch.setattr(asyncio, "create_subprocess_exec", spawn)
    monkeypatch.setattr(os, "kill", stop)
    task = asyncio.create_task(
        probe.run_probe(build, digest, tmp_path / "trial", job, approved_scope="as1-a")
    )
    await launched.wait()
    if when != "deadline":
        task.cancel()
    if when == "repeat_cancel":
        await inspecting.wait()
        task.cancel()
    release.set()
    with pytest.raises(TimeoutError if when == "deadline" else asyncio.CancelledError):
        await task
    assert signals == [(12345, 15)] and child.exited.is_set()
    assert probe.private_read(directory / "cancel", 20) == b"cancel"


async def test_stop_never_kills_a_pid_with_another_command(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    job = tmp_path / ("a" * 32)
    job.mkdir()
    probe.private_write(
        job / "helper.json", json.dumps({"request_id": job.name, "pid": 12345}).encode()
    )

    async def inspect(*args: str, **kwargs: object) -> Process:
        return Process(done=True, output=b"another application")

    monkeypatch.setattr(asyncio, "create_subprocess_exec", inspect)
    monkeypatch.setattr(os, "kill", lambda *_: pytest.fail("An unrelated PID was signalled."))
    with pytest.raises(probe.ProbeFailure):
        await probe.stop_helper(
            cast(asyncio.subprocess.Process, Process(done=True)), job, Path("/synthetic/helper")
        )


def test_swift_probe_has_no_text_capture_or_input_api_and_no_runtime_registration() -> None:
    root = Path(__file__).resolve().parents[2]
    source = (root / "tools/mac_desktop/Probe.swift").read_text()
    for forbidden in [
        "kAXValueAttribute",
        "kAXTitleAttribute",
        "kAXDescriptionAttribute",
        "kAXIdentifierAttribute",
        "AXUIElementPerformAction",
        "AXUIElementSetAttributeValue",
        "CGEvent",
        "ScreenCaptureKit",
        "chat.db",
    ]:
        assert forbidden not in source
    assert "mac_probe" not in (root / "server/app/main.py").read_text()
