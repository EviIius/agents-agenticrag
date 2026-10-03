"""launchd agent so the watcher starts at login and restarts if it exits."""
from __future__ import annotations

import os
import plistlib
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional

from .config import REPO_ROOT, Config

WATCHER_LABEL = "com.localtranscribe.watcher"


def agent_path(label: str = WATCHER_LABEL) -> Path:
    return Path.home() / "Library" / "LaunchAgents" / (label + ".plist")


def watcher_plist(cfg: Config, python: Optional[str] = None) -> Dict:
    python = python or sys.executable
    args = [python, "-m", "localtranscribe"]
    if cfg.source:
        args += ["--config", str(cfg.source)]
    args.append("watch")
    launchd_log = str(cfg.logs_dir / "watcher.launchd.log")
    return {
        "Label": WATCHER_LABEL,
        "ProgramArguments": args,
        "WorkingDirectory": str(REPO_ROOT),
        "EnvironmentVariables": {
            "PYTHONPATH": str(REPO_ROOT),
            "PYTHONUNBUFFERED": "1",
            # launchd starts with a bare PATH; Homebrew's bin must be on it.
            "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
        },
        "RunAtLoad": True,
        "KeepAlive": True,
        "ThrottleInterval": 10,
        "StandardOutPath": launchd_log,
        "StandardErrorPath": launchd_log,
    }


def write_plist(cfg: Config, dest: Path, python: Optional[str] = None) -> Path:
    cfg.ensure_dirs()
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "wb") as fh:
        plistlib.dump(watcher_plist(cfg, python), fh)
    return dest


def _launchctl(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["launchctl", *args], capture_output=True, text=True)


def install(cfg: Config, python: Optional[str] = None) -> int:
    if sys.platform != "darwin":
        print("launchd is macOS-only; use --plist-only to just write the file.")
        return 1
    dest = write_plist(cfg, agent_path(), python)
    domain = "gui/%d" % os.getuid()
    _launchctl("bootout", "%s/%s" % (domain, WATCHER_LABEL))  # replace any old copy
    proc = _launchctl("bootstrap", domain, str(dest))
    if proc.returncode != 0:
        print("launchctl bootstrap failed: %s" % (proc.stderr.strip() or proc.stdout.strip()))
        return 1
    _launchctl("enable", "%s/%s" % (domain, WATCHER_LABEL))
    print("Watcher installed and started: %s" % dest)
    print("Watching: %s" % cfg.inbox_dir)
    return 0


def uninstall() -> int:
    if sys.platform != "darwin":
        print("launchd is macOS-only.")
        return 1
    _launchctl("bootout", "gui/%d/%s" % (os.getuid(), WATCHER_LABEL))
    dest = agent_path()
    if dest.exists():
        dest.unlink()
    print("Watcher stopped and removed. Your recordings and transcripts are untouched.")
    return 0


def status() -> int:
    if sys.platform != "darwin":
        print("launchd is macOS-only.")
        return 1
    proc = _launchctl("print", "gui/%d/%s" % (os.getuid(), WATCHER_LABEL))
    if proc.returncode != 0:
        print("Watcher is not loaded. Run ./install.sh (or: bin/transcribe install-agent).")
        return 1
    wanted = ("state =", "pid =", "last exit code =")
    for line in proc.stdout.splitlines():
        if line.strip().startswith(wanted):
            print(line.strip())
    return 0
