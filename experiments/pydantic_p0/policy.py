"""Python audit controls for the isolated trial, not a general OS sandbox."""

from __future__ import annotations

import os
import sys
from pathlib import Path


class AuditPolicy:
    def __init__(self, trial: Path, source: Path, read_roots: list[Path], port: int, emit):
        self.trial = trial.resolve()
        self.source = source.resolve()
        self.read_roots = [p.resolve() for p in read_roots]
        self.port = port
        self.emit = emit

    @staticmethod
    def within(path, roots) -> bool:
        if isinstance(path, int):
            return False
        try:
            resolved = Path(os.fsdecode(path)).resolve()
            return any(resolved == root or resolved.is_relative_to(root) for root in roots)
        except (TypeError, ValueError, OSError):
            return False

    def reject(self, category: str, event: str, args) -> None:
        caller = "python_or_host"
        frame = sys._getframe(2)
        while frame:
            filename = frame.f_code.co_filename
            if filename.startswith(str(self.source) + os.sep):
                caller = "candidate:" + filename[len(str(self.source)) + 1 :]
                break
            if "site-packages/" in filename:
                caller = "dependency:" + filename.split("site-packages/", 1)[1]
                break
            frame = frame.f_back
        data = {"category": category, "event": event, "caller": caller}
        if category == "process":
            executable = os.path.basename(str(args[0])) if args else ""
            data["executable_category"] = (
                "platform_or_availability_probe"
                if executable in {"sw_vers", "sysctl", "uname", "which", "git", "sh", "bash"}
                else "other"
            )
        self.emit("blocked", **data)
        raise PermissionError("Operation outside the isolated P0 policy")

    def __call__(self, event, args) -> None:
        if event == "socket.connect":
            address = args[1]
            if not (isinstance(address, tuple) and address[:2] == ("127.0.0.1", self.port)):
                self.reject("network", event, args)
        elif event == "socket.bind":
            self.reject("network", event, args)
        elif event in {
            "os.system",
            "os.exec",
            "os.posix_spawn",
            "subprocess.Popen",
            "os.fork",
            "os.forkpty",
        }:
            self.reject("process", event, args)
        elif event == "open":
            path, mode, flags = args
            writing = (isinstance(mode, str) and any(c in mode for c in "wax+")) or (
                isinstance(flags, int)
                and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)
            )
            # Existing descriptors are not paths; stdio is inherited by the host.
            if isinstance(path, int):
                return
            roots = [self.trial] if writing else self.read_roots
            if not self.within(path, roots):
                self.reject("file_write" if writing else "file_read", event, args)
        elif event in {"os.symlink", "os.link"}:
            self.reject("file_mutation", event, args)
        elif event in {"os.rename", "os.remove", "os.rmdir", "os.mkdir", "os.chmod", "os.utime"}:
            count = 2 if event == "os.rename" else 1
            paths = args[:count]
            # dir_fd-relative mutations could evade path resolution; do not admit them.
            fd_args = args[2:] if event in {"os.rename", "os.mkdir", "os.chmod"} else args[1:]
            if any(isinstance(v, int) and v >= 0 for v in fd_args) or not all(
                self.within(path, [self.trial]) for path in paths
            ):
                self.reject("file_mutation", event, args)
