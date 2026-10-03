"""Running ffmpeg / ffprobe / whisper-cli as child processes that can be
stopped promptly when the watcher is asked to shut down."""
from __future__ import annotations

import os
import signal
import subprocess
import threading
from typing import List, NamedTuple, Optional


class Stopped(RuntimeError):
    """The work was interrupted by a shutdown request."""


class Completed(NamedTuple):
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool


_lock = threading.Lock()
_current: Optional[subprocess.Popen] = None
_stop_requested = False


def _kill(proc: subprocess.Popen, sig: int) -> None:
    try:
        os.killpg(proc.pid, sig)
    except (ProcessLookupError, PermissionError):
        pass


def request_stop() -> None:
    """Stop the running child, if any, and refuse to start new ones."""
    global _stop_requested
    _stop_requested = True
    with _lock:
        proc = _current
    if proc is not None and proc.poll() is None:
        _kill(proc, signal.SIGTERM)


def reset() -> None:
    global _stop_requested
    _stop_requested = False


def run(cmd: List[str], timeout: Optional[float] = None) -> Completed:
    global _current
    if _stop_requested:
        raise Stopped("shutting down")
    proc = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, errors="replace",
                            start_new_session=True)
    with _lock:
        _current = proc
    timed_out = False
    try:
        try:
            out, err = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            _kill(proc, signal.SIGKILL)
            out, err = proc.communicate()
    except BaseException:
        _kill(proc, signal.SIGKILL)
        proc.wait()
        raise
    finally:
        with _lock:
            _current = None
    if _stop_requested:
        raise Stopped("shutting down")
    return Completed(proc.returncode, out or "", err or "", timed_out)
