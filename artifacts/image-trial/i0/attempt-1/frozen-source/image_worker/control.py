"""Event-driven subprocess supervision for the isolated image trial, not an app queue."""

import hashlib
import json
import os
import selectors
import signal
import subprocess
import time
import urllib.request
from pathlib import Path


def get_json(url: str) -> object:
    with urllib.request.urlopen(url, timeout=5) as response:
        return json.load(response)


def require_idle() -> None:
    if get_json("http://127.0.0.1:8787/api/runs/active"):
        raise RuntimeError("Human chat is active; stop the image trial")
    if get_json("http://127.0.0.1:8787/api/transcription/audio-storage")["active_files"]:
        raise RuntimeError("Human transcription is active; stop the image trial")


def sample(pid: int) -> dict:
    result = subprocess.run(
        ["/bin/ps", "-o", "rss=", "-p", str(pid)], capture_output=True, text=True
    )
    rss = result.stdout.strip()
    swap = subprocess.run(
        ["/usr/sbin/sysctl", "vm.swapusage"], capture_output=True, text=True
    ).stdout.strip()
    started = time.monotonic()
    try:
        with urllib.request.urlopen("http://127.0.0.1:8787/api/health", timeout=3) as response:
            health = {"status": response.status, "seconds": time.monotonic() - started}
    except Exception as error:
        health = {"error": type(error).__name__, "seconds": time.monotonic() - started}
    return {
        "rss_bytes": int(rss) * 1024 if rss.isdigit() else None,
        "swap": swap,
        "app_health": health,
    }


def terminate(process: subprocess.Popen, grace: float) -> bool:
    """Return only after reaping our process; signal the whole isolated session."""
    if process.poll() is not None:
        return False
    os.killpg(process.pid, signal.SIGTERM)
    try:
        process.wait(timeout=grace)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=grace)
    return True


def supervise(
    command: list[str],
    folder: Path,
    *,
    cwd: Path,
    env: dict[str, str],
    timeout: float = 1200,
    grace: float = 10,
    cancel_on: str | None = None,
    cancel_delay: float = 0,
    metrics: bool = True,
) -> dict:
    folder.mkdir(parents=True, exist_ok=False)
    events = []
    samples = []
    started = time.monotonic()
    cancellation_due = None
    signalled = False
    timed_out = False
    process = None
    with (
        (folder / "stderr.log").open("x") as errors,
        (folder / "events.jsonl").open("x") as journal,
    ):
        try:
            process = subprocess.Popen(
                command,
                cwd=cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=errors,
                start_new_session=True,
            )
            selector = selectors.DefaultSelector()
            selector.register(process.stdout, selectors.EVENT_READ)
            buffer = b""
            next_sample = started
            while selector.get_map() or process.poll() is None:
                now = time.monotonic()
                if metrics and now >= next_sample:
                    samples.append({"elapsed_seconds": now - started, **sample(process.pid)})
                    next_sample = time.monotonic() + 1
                if now - started > timeout and process.poll() is None:
                    timed_out = True
                    signalled = terminate(process, grace)
                if (
                    cancellation_due is not None
                    and now >= cancellation_due
                    and process.poll() is None
                ):
                    signalled = terminate(process, grace)
                    cancellation_due = None
                for key, _ in selector.select(timeout=0.1):
                    data = os.read(key.fileobj.fileno(), 65536)
                    if not data:
                        selector.unregister(key.fileobj)
                        if buffer:
                            raise ValueError("Incomplete worker event")
                        continue
                    buffer += data
                    while b"\n" in buffer:
                        line, buffer = buffer.split(b"\n", 1)
                        event = json.loads(line)
                        if not isinstance(event, dict) or not isinstance(event.get("type"), str):
                            raise ValueError("Invalid worker event")
                        events.append(event)
                        journal.write(json.dumps(event) + "\n")
                        journal.flush()
                        if (
                            event["type"] == cancel_on
                            and not signalled
                            and cancellation_due is None
                        ):
                            cancellation_due = time.monotonic() + cancel_delay
            process.wait(timeout=grace)
            selector.close()
        finally:
            if process is not None and process.poll() is None:
                terminate(process, grace)
            if process is not None and process.stdout is not None:
                process.stdout.close()
    try:
        os.kill(process.pid, 0)
        process_absent = False
    except ProcessLookupError:
        process_absent = True
    completed = [event for event in events if event["type"] == "completed"]
    finished = any(event["type"] == "worker_finished" for event in events)
    success = (
        process.returncode == 0 and finished and not signalled and not timed_out and process_absent
    )
    receipt = {
        "command": command,
        "cwd": str(cwd),
        "exit_code": process.returncode,
        "elapsed_seconds": time.monotonic() - started,
        "events": len(events),
        "completed_jobs": [event["job"] for event in completed],
        "success": success,
        "cancel_trigger": cancel_on,
        "termination_signalled": signalled,
        "worker_reaped": process.poll() is not None,
        "process_absent_after_reap": process_absent,
        "timed_out": timed_out,
        "sampled_peak_rss_bytes": max((item["rss_bytes"] or 0 for item in samples), default=0),
        "sampling_limitation": "One-second process RSS samples, not a true peak or GPU allocation proof.",
        "samples": samples,
    }
    (folder / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


def validate_output(folder: Path, job: str, width: int = 1024, height: int = 1024) -> dict:
    """Completion needs a complete PNG, exact dimensions, metadata and matching hash."""
    import struct
    import zlib

    image = folder / f"{job}.png"
    metadata = json.loads((folder / f"{job}.json").read_text())
    data = image.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Invalid PNG signature")
    cursor = 8
    dimensions = None
    ended = False
    while cursor < len(data):
        if len(data) - cursor < 12:
            raise ValueError("Truncated PNG chunk")
        size = struct.unpack(">I", data[cursor : cursor + 4])[0]
        kind = data[cursor + 4 : cursor + 8]
        end = cursor + size + 12
        if end > len(data):
            raise ValueError("Truncated PNG payload")
        body = data[cursor + 8 : cursor + size + 8]
        crc = struct.unpack(">I", data[cursor + size + 8 : end])[0]
        if zlib.crc32(kind + body) & 0xFFFFFFFF != crc:
            raise ValueError("PNG CRC mismatch")
        if kind == b"IHDR":
            dimensions = struct.unpack(">II", body[:8])
        cursor = end
        if kind == b"IEND":
            ended = cursor == len(data)
            break
    if not ended or dimensions != (width, height):
        raise ValueError("Incomplete or incorrectly sized PNG")
    if metadata.get("job") != job or metadata.get("sha256") != hashlib.sha256(data).hexdigest():
        raise ValueError("Image metadata/hash mismatch")
    return metadata
