"""Running whisper.cpp (whisper-cli) on a normalised WAV file.

The model is loaded for each job and released when the job ends, so nothing
stays resident between recordings.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from . import proc as _proc

BLANK_MARKERS = {"[BLANK_AUDIO]", "[ Silence ]", "[silence]"}


class WhisperError(RuntimeError):
    pass


_flag_cache: Dict[Tuple[str, float], Set[str]] = {}


def supported_flags(whisper_cli: str) -> Set[str]:
    """Flags this whisper-cli build advertises in --help.

    Older builds lack --vad or --carry-initial-prompt; passing a flag a build
    does not know makes every job fail, so only advertised ones are used.
    Cached per binary, and refreshed when the binary changes (brew upgrade).
    """
    try:
        key = (whisper_cli, os.stat(whisper_cli).st_mtime)
    except OSError:
        key = (whisper_cli, 0.0)
    if key not in _flag_cache:
        proc = _proc.run([whisper_cli, "--help"], timeout=30)
        text = proc.stdout + proc.stderr
        _flag_cache.clear()
        _flag_cache[key] = set(re.findall(r"(?<![\w-])(--?[a-zA-Z][\w-]*)", text))
    return _flag_cache[key]


def build_command(whisper_cli: str, wav: Path, out_base: Path, model: Path,
                  language: str, threads: int, prompt: str,
                  vad_model: Optional[Path], extra: List[str],
                  flags: Optional[Set[str]] = None) -> List[str]:
    """flags: what the binary supports (None = assume a current build)."""
    def has(flag: str) -> bool:
        return flags is None or flag in flags

    cmd = [whisper_cli, "-m", str(model), "-f", str(wav),
           "-oj", "-of", str(out_base), "-np",
           "-l", language, "-t", str(int(threads))]
    if prompt:
        cmd += ["--prompt", prompt]
        if has("--carry-initial-prompt"):
            # Keeps the vocabulary hint in force for the whole recording,
            # not just the first 30 seconds.
            cmd.append("--carry-initial-prompt")
    if vad_model is not None and has("--vad"):
        cmd += ["--vad", "-vm", str(vad_model)]
    return cmd + [str(a) for a in extra]


def run(cmd: List[str], out_base: Path, timeout: float) -> List[Dict]:
    """Run whisper-cli and return segments as [{start, end, text}] (seconds)."""
    proc = _proc.run(cmd, timeout=timeout)
    if proc.timed_out:
        raise WhisperError("whisper-cli exceeded the %d s time limit and was stopped"
                           % timeout)
    if proc.returncode != 0:
        tail = "\n".join(proc.stderr.strip().splitlines()[-15:])
        raise WhisperError("whisper-cli exited with code %s:\n%s"
                           % (proc.returncode, tail or "(no output)"))
    json_path = Path(str(out_base) + ".json")
    if not json_path.exists():
        raise WhisperError("whisper-cli finished but wrote no JSON output")
    with open(json_path, "r", encoding="utf-8", errors="replace") as fh:
        data = json.load(fh)
    return parse_segments(data)


def parse_segments(data: Dict) -> List[Dict]:
    segments = []
    for item in data.get("transcription", []):
        text = " ".join(str(item.get("text", "")).split())
        if not text or text in BLANK_MARKERS:
            continue
        offsets = item.get("offsets", {})
        segments.append({
            "start": float(offsets.get("from", 0)) / 1000.0,
            "end": float(offsets.get("to", 0)) / 1000.0,
            "text": text,
        })
    return segments
