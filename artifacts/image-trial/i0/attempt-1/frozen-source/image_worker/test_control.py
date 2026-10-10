"""Synthetic checks for failure and cancellation boundaries; no image dependencies."""

import hashlib
import json
import os
import struct
import sys
import zlib

import pytest
from control import supervise, validate_output


def invoke(tmp_path, code, **kwargs):
    return supervise(
        [sys.executable, "-u", "-c", code],
        tmp_path / "session",
        cwd=tmp_path,
        env=dict(os.environ),
        metrics=False,
        timeout=2,
        grace=1,
        **kwargs,
    )


def test_cancel_waits_for_worker_exit(tmp_path):
    receipt = invoke(
        tmp_path,
        'import json,time; print(json.dumps({"type":"generation_progress"}),flush=True); time.sleep(30)',
        cancel_on="generation_progress",
    )
    assert receipt["termination_signalled"] and receipt["worker_reaped"]
    assert receipt["exit_code"] != 0 and not receipt["success"]
    assert receipt["completed_jobs"] == []


def test_timeout_never_becomes_success(tmp_path):
    receipt = invoke(tmp_path, "import time; time.sleep(30)")
    assert receipt["timed_out"] and receipt["worker_reaped"]
    assert not receipt["success"]


def test_exit_zero_without_terminal_event_fails(tmp_path):
    receipt = invoke(tmp_path, "pass")
    assert receipt["exit_code"] == 0 and not receipt["success"]


def test_terminal_event_with_nonzero_exit_fails(tmp_path):
    receipt = invoke(
        tmp_path, 'import json,sys; print(json.dumps({"type":"worker_finished"})); sys.exit(1)'
    )
    assert not receipt["success"]


def test_finished_worker_can_succeed(tmp_path):
    receipt = invoke(tmp_path, 'import json; print(json.dumps({"type":"worker_finished"}))')
    assert receipt["success"] and receipt["worker_reaped"]


def test_malformed_event_terminates_owned_worker(tmp_path):
    with pytest.raises(json.JSONDecodeError):
        invoke(tmp_path, 'import time; print("bad",flush=True); time.sleep(30)')


def chunk(kind, body):
    return (
        struct.pack(">I", len(body))
        + kind
        + body
        + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)
    )


def png():
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(b"\0\0\0\0"))
        + chunk(b"IEND", b"")
    )


@pytest.mark.parametrize("mutation", ["truncated", "crc", "hash", "dimensions", "missing_metadata"])
def test_invalid_or_partial_output_rejected(tmp_path, mutation):
    data = png()
    (tmp_path / "test.json").write_text(
        json.dumps({"job": "test", "sha256": hashlib.sha256(data).hexdigest()})
    )
    if mutation == "truncated":
        data = data[:-5]
    elif mutation == "crc":
        data = data[:-1] + bytes([data[-1] ^ 1])
    elif mutation == "hash":
        (tmp_path / "test.json").write_text(json.dumps({"job": "test", "sha256": "wrong"}))
    elif mutation == "missing_metadata":
        (tmp_path / "test.json").unlink()
    (tmp_path / "test.png").write_bytes(data)
    with pytest.raises((ValueError, FileNotFoundError)):
        validate_output(tmp_path, "test", 2 if mutation == "dimensions" else 1, 1)


def test_complete_output_accepts_matching_hash(tmp_path):
    data = png()
    (tmp_path / "test.png").write_bytes(data)
    (tmp_path / "test.json").write_text(
        json.dumps({"job": "test", "sha256": hashlib.sha256(data).hexdigest()})
    )
    assert validate_output(tmp_path, "test", 1, 1)["job"] == "test"
