"""Configuration: defaults, plus whatever config.json overrides.

Paths may use ~ and may be relative; relative paths resolve against the repo
root, so the repo can live anywhere.
"""
from __future__ import annotations

import copy
import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent

DEFAULTS: Dict[str, Any] = {
    # Where the inbox / done / failed / logs folders live.
    "data_dir": "~/Transcription",
    # Override any single folder here; otherwise they sit under data_dir.
    "inbox_dir": None,
    "done_dir": None,
    "failed_dir": None,
    "logs_dir": None,
    # Whisper model (ggml format) and the Silero voice-activity model.
    "model": "models/ggml-large-v3-turbo.bin",
    "vad_model": "models/ggml-silero-v6.2.0.bin",
    "use_vad": True,
    "language": "en",
    # Glossary: correct spellings of names Whisper tends to garble.
    "glossary": "glossary.txt",
    "apply_glossary_corrections": True,
    "prompt_template": "This recording mentions {terms}.",
    # "mix": fold all channels into one transcript.
    # "split": transcribe each channel separately and merge by timestamp.
    "channels": "mix",
    "speaker_labels": ["Speaker 1", "Speaker 2"],
    # A pause this long starts a new paragraph in the .txt output.
    "paragraph_gap_seconds": 2.0,
    "threads": 6,
    # Binaries; bare names are looked up on PATH and in Homebrew's bin folders.
    "whisper_cli": "whisper-cli",
    "ffmpeg": "ffmpeg",
    "ffprobe": "ffprobe",
    "extra_whisper_args": [],
    # A job is killed if it runs longer than base + factor * audio duration.
    "timeout_base_seconds": 600,
    "timeout_factor": 4.0,
    "watcher": {
        "poll_seconds": 5,
        # A file must be unchanged this long before it is picked up.
        "settle_seconds": 10,
        # A WAV whose header promises more data than is on disk waits this
        # long for the rest, then is transcribed as-is with a warning.
        "stalled_seconds": 300,
    },
}

AUDIO_EXTENSIONS = {
    ".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg", ".oga", ".opus",
    ".aif", ".aiff", ".caf", ".wma", ".mp4", ".mov", ".webm", ".mka", ".amr",
}

_EXTRA_BIN_DIRS = ["/opt/homebrew/bin", "/usr/local/bin"]


def _merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    out = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = value
    return out


class Config:
    def __init__(self, values: Dict[str, Any], source: Optional[Path] = None):
        self.values = values
        self.source = source

    def __getitem__(self, key: str) -> Any:
        return self.values[key]

    def get(self, key: str, default: Any = None) -> Any:
        return self.values.get(key, default)

    # -- paths ------------------------------------------------------------
    @staticmethod
    def _path(value: str) -> Path:
        p = Path(os.path.expanduser(str(value)))
        return p if p.is_absolute() else (REPO_ROOT / p)

    def path(self, key: str) -> Path:
        return self._path(self.values[key])

    @property
    def data_dir(self) -> Path:
        return self.path("data_dir")

    def _folder(self, key: str, name: str) -> Path:
        value = self.values.get(key)
        return self._path(value) if value else self.data_dir / name

    @property
    def inbox_dir(self) -> Path:
        return self._folder("inbox_dir", "inbox")

    @property
    def done_dir(self) -> Path:
        return self._folder("done_dir", "done")

    @property
    def failed_dir(self) -> Path:
        return self._folder("failed_dir", "failed")

    @property
    def logs_dir(self) -> Path:
        return self._folder("logs_dir", "logs")

    @property
    def work_dir(self) -> Path:
        return self.data_dir / ".work"

    @property
    def lock_file(self) -> Path:
        return self.data_dir / ".transcribe.lock"

    def ensure_dirs(self) -> None:
        for d in (self.data_dir, self.inbox_dir, self.done_dir,
                  self.failed_dir, self.logs_dir, self.work_dir):
            d.mkdir(parents=True, exist_ok=True)

    # -- binaries ---------------------------------------------------------
    def binary(self, key: str) -> Optional[str]:
        """Absolute path of a configured binary, or None if it can't be found."""
        value = os.path.expanduser(str(self.values[key]))
        if os.sep in value:
            return value if os.access(value, os.X_OK) else None
        search = os.pathsep.join(
            [os.environ.get("PATH", "")] + _EXTRA_BIN_DIRS)
        return shutil.which(value, path=search)

    def require_binary(self, key: str) -> str:
        found = self.binary(key)
        if not found:
            raise FileNotFoundError(
                "%s not found (config key %r = %r). Run ./install.sh or fix "
                "the path in config.json." % (key, key, self.values[key]))
        return found


def load_config(path: Optional[str] = None) -> Config:
    """Load config.json (explicit path, $LOCALTRANSCRIBE_CONFIG, or repo root)."""
    candidate = path or os.environ.get("LOCALTRANSCRIBE_CONFIG")
    source = (Path(os.path.expanduser(candidate)).resolve() if candidate
              else REPO_ROOT / "config.json")
    if source.exists():
        with open(source, "r", encoding="utf-8") as fh:
            override = json.load(fh)
        if not isinstance(override, dict):
            raise ValueError("%s must contain a JSON object" % source)
        unknown = sorted(set(override) - set(DEFAULTS))
        if unknown:
            raise ValueError("Unknown key(s) in %s: %s" % (source, ", ".join(unknown)))
        return Config(_merge(DEFAULTS, override), source)
    if candidate:
        raise FileNotFoundError("Config file not found: %s" % source)
    return Config(copy.deepcopy(DEFAULTS), None)
