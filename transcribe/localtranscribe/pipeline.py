"""One recording in, three files out: <name>.txt, <name>.srt, <name>.json."""
from __future__ import annotations

import fcntl
import json
import logging
import os
import shutil
import tempfile
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from . import __version__, audio, formats, whisper
from .config import Config
from .glossary import Glossary

log = logging.getLogger("localtranscribe")

OUTPUT_SUFFIXES = (".txt", ".srt", ".json")


@dataclass
class Result:
    stem: str
    files: Dict[str, Path]
    text: str
    duration_seconds: float
    elapsed_seconds: float
    warnings: List[str] = field(default_factory=list)


@contextmanager
def job_lock(cfg: Config):
    """Only one transcription at a time, across every process using this
    config, so two jobs never load the model together."""
    cfg.data_dir.mkdir(parents=True, exist_ok=True)
    with open(cfg.lock_file, "w") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def _speaker_label(cfg: Config, index: int) -> str:
    labels = cfg["speaker_labels"] or []
    return labels[index] if index < len(labels) else "Speaker %d" % (index + 1)


def _write(path: Path, content: str) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)


def transcribe_file(src: Path, out_dir: Path, cfg: Config,
                    channels: Optional[str] = None, stem: Optional[str] = None,
                    warnings: Optional[List[str]] = None) -> Result:
    """Transcribe src and write <stem>.txt/.srt/.json into out_dir.

    src is only read, never changed.
    """
    src = Path(src)
    out_dir = Path(out_dir)
    stem = stem or src.stem
    warnings = list(warnings or [])
    if not src.is_file():
        raise FileNotFoundError("No such audio file: %s" % src)

    ffmpeg = cfg.require_binary("ffmpeg")
    ffprobe = cfg.require_binary("ffprobe")
    whisper_cli = cfg.require_binary("whisper_cli")
    model = cfg.path("model")
    if not model.exists():
        raise FileNotFoundError(
            "Whisper model not found at %s. Run ./install.sh to download it." % model)

    vad_model: Optional[Path] = None
    if cfg["use_vad"]:
        candidate = cfg.path("vad_model")
        if candidate.exists():
            vad_model = candidate
        else:
            warnings.append("Voice-activity model not found at %s; ran without it."
                            % candidate)

    info = audio.probe(src, ffprobe)
    if info.audio_streams > 1:
        warnings.append("File has %d audio streams; only the first was transcribed."
                        % info.audio_streams)

    glossary = Glossary.load(cfg.path("glossary"))
    prompt = glossary.prompt(cfg["prompt_template"])
    if glossary.prompt_truncated:
        warnings.append("Glossary is too long for Whisper's vocabulary hint; "
                        "later terms were left out of the hint (corrections still apply).")

    mode = channels or cfg["channels"]
    if mode not in ("mix", "split"):
        raise ValueError("channels must be 'mix' or 'split', not %r" % mode)
    if mode == "split" and info.channels < 2:
        mode = "mix"
    tracks = list(range(info.channels)) if mode == "split" else [None]

    flags = whisper.supported_flags(whisper_cli)
    if vad_model is not None and "--vad" not in flags:
        warnings.append("This whisper-cli build has no voice-activity support; "
                        "ran without it. Update with: brew upgrade whisper-cpp")
        vad_model = None
    if prompt and "--carry-initial-prompt" not in flags:
        warnings.append("This whisper-cli build cannot repeat the vocabulary hint, so it "
                        "only covers the start of the recording (glossary corrections "
                        "still apply). Update with: brew upgrade whisper-cpp")

    timeout = cfg["timeout_base_seconds"] + cfg["timeout_factor"] * info.duration_seconds
    started = time.time()
    segments: List[Dict] = []

    with job_lock(cfg):
        cfg.work_dir.mkdir(parents=True, exist_ok=True)
        scratch = Path(tempfile.mkdtemp(prefix="job-", dir=str(cfg.work_dir)))
        try:
            for track in tracks:
                name = "track%d" % track if track is not None else "mix"
                wav = scratch / (name + ".wav")
                audio.normalize(src, wav, ffmpeg, info.channels, track)
                cmd = whisper.build_command(
                    whisper_cli, wav, scratch / name, model, cfg["language"],
                    cfg["threads"], prompt, vad_model, cfg["extra_whisper_args"], flags)
                for seg in whisper.run(cmd, scratch / name, timeout):
                    seg["speaker"] = _speaker_label(cfg, track) if track is not None else None
                    seg["channel"] = track
                    segments.append(seg)
                wav.unlink()
        finally:
            shutil.rmtree(scratch, ignore_errors=True)

    segments.sort(key=lambda s: (s["start"], s["channel"] if s["channel"] is not None else 0))
    elapsed = time.time() - started

    # Glossary corrections. The untouched Whisper output is kept as raw_text.
    gap = float(cfg["paragraph_gap_seconds"])
    corrections: Dict = {}
    for seg in segments:
        seg["raw_text"] = seg["text"]
        if cfg["apply_glossary_corrections"]:
            seg["text"], _ = glossary.apply(seg["raw_text"])
    raw_text = formats.to_text(segments, gap, key="raw_text")
    if cfg["apply_glossary_corrections"]:
        # Applied to the joined text too, which also catches a name that
        # Whisper split across two segments.
        text, corrections = glossary.apply(raw_text)
    else:
        text = raw_text

    if not segments:
        warnings.append("No speech was detected in this recording.")

    payload = {
        "source": dict(info.as_dict(), file=src.name),
        "engine": {
            "pipeline_version": __version__,
            "runtime": "whisper.cpp",
            "model": model.name,
            "vad": vad_model.name if vad_model else None,
            "language": cfg["language"],
            "prompt": prompt,
        },
        "channel_mode": mode,
        "processing": {
            "finished_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "elapsed_seconds": round(elapsed, 1),
            "speed_x_realtime": round(info.duration_seconds / elapsed, 1) if elapsed > 0 else None,
        },
        "warnings": warnings,
        "glossary_corrections": [
            {"found": found, "replaced_with": correct, "count": count}
            for (found, correct), count in sorted(corrections.items())
        ],
        "text": text,
        "raw_text": raw_text,
        "segments": [
            {"start": round(s["start"], 3), "end": round(s["end"], 3),
             "speaker": s["speaker"], "text": s["text"], "raw_text": s["raw_text"]}
            for s in segments
        ],
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    files = {suffix: out_dir / (stem + suffix) for suffix in OUTPUT_SUFFIXES}
    _write(files[".txt"], text)
    _write(files[".srt"], formats.to_srt(segments))
    _write(files[".json"], json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    return Result(stem=stem, files=files, text=text,
                  duration_seconds=info.duration_seconds,
                  elapsed_seconds=elapsed, warnings=warnings)
