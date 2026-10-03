"""Checks that everything the pipeline needs is in place."""
from __future__ import annotations

import json
import os
import subprocess
from typing import Dict, List, NamedTuple

from . import __version__
from .config import AUDIO_EXTENSIONS, Config
from .glossary import Glossary


class Check(NamedTuple):
    name: str
    ok: bool
    detail: str
    blocking: bool  # True: transcription cannot run without this


def _version(binary: str, flag: str) -> str:
    try:
        proc = subprocess.run([binary, flag], capture_output=True, text=True, timeout=20)
        lines = (proc.stdout or proc.stderr).strip().splitlines()
        return lines[0] if lines else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def run_checks(cfg: Config, versions: bool = True) -> List[Check]:
    checks: List[Check] = []
    for key, flag in (("ffmpeg", "-version"), ("ffprobe", "-version"),
                      ("whisper_cli", "--version")):
        path = cfg.binary(key)
        if path:
            detail = path
            version = _version(path, flag) if versions else ""
            if version:
                detail += "  (%s)" % version[:60]
            checks.append(Check(key, True, detail, True))
        else:
            checks.append(Check(key, False, "not found: %s" % cfg[key], True))

    model = cfg.path("model")
    if model.exists():
        size = model.stat().st_size / 1e9
        checks.append(Check("model", True, "%s  (%.2f GB)" % (model, size), True))
    else:
        checks.append(Check("model", False, "missing: %s" % model, True))

    vad = cfg.path("vad_model")
    if not cfg["use_vad"]:
        checks.append(Check("vad_model", True, "disabled in config", False))
    elif vad.exists():
        checks.append(Check("vad_model", True, str(vad), False))
    else:
        checks.append(Check("vad_model", False,
                            "missing: %s (transcription still runs, without "
                            "silence filtering)" % vad, False))

    glossary_path = cfg.path("glossary")
    if glossary_path.exists():
        count = len(Glossary.load(glossary_path).entries)
        checks.append(Check("glossary", True, "%s  (%d terms)" % (glossary_path, count), False))
    else:
        checks.append(Check("glossary", False, "missing: %s (no vocabulary hint "
                            "or corrections)" % glossary_path, False))

    for label, folder in (("inbox", cfg.inbox_dir), ("done", cfg.done_dir),
                          ("failed", cfg.failed_dir), ("logs", cfg.logs_dir)):
        if folder.is_dir() and os.access(folder, os.W_OK):
            checks.append(Check(label, True, str(folder), True))
        else:
            checks.append(Check(label, False, "missing or not writable: %s" % folder, True))
    return checks


def blocking_problems(cfg: Config) -> List[str]:
    return ["%s: %s" % (c.name, c.detail) for c in run_checks(cfg, versions=False)
            if c.blocking and not c.ok]


def report(cfg: Config) -> int:
    checks = run_checks(cfg)
    print("Config: %s" % (cfg.source or "built-in defaults (no config.json)"))
    for c in checks:
        mark = "ok  " if c.ok else ("FAIL" if c.blocking else "warn")
        print("  [%s] %-12s %s" % (mark, c.name, c.detail))
    failed = [c for c in checks if c.blocking and not c.ok]
    print("\n%s" % ("Ready." if not failed else
                    "%d problem(s) must be fixed before transcription can run." % len(failed)))
    return 1 if failed else 0


def report_json(cfg: Config) -> int:
    """The same checks as report(), as one JSON object on stdout.

    This is the interface other programs use to ask "is the engine ready?"
    and to find the glossary file. Keys are only ever added, never renamed.
    """
    checks = run_checks(cfg)
    failed = [c for c in checks if c.blocking and not c.ok]
    payload: Dict = {
        "ok": not failed,
        "version": __version__,
        "config": str(cfg.source) if cfg.source else None,
        "checks": [c._asdict() for c in checks],
        "paths": {
            "data_dir": str(cfg.data_dir),
            "glossary": str(cfg.path("glossary")),
            "model": str(cfg.path("model")),
        },
        "channels": cfg["channels"],
        "audio_extensions": sorted(AUDIO_EXTENSIONS),
    }
    print(json.dumps(payload, indent=2))
    return 1 if failed else 0
