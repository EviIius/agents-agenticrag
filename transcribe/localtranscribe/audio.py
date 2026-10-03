"""Inspecting audio with ffprobe and normalising it with ffmpeg.

The source file is only ever read. Normalised copies (16 kHz, mono, 16-bit
PCM, which is what Whisper expects) are written to a scratch folder.
"""
from __future__ import annotations

import json
import struct
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional

from . import proc as _proc


class AudioError(RuntimeError):
    pass


@dataclass
class AudioInfo:
    duration_seconds: float
    sample_rate: int
    channels: int
    codec: str
    bits_per_sample: Optional[int]
    container: str
    audio_streams: int
    size_bytes: int

    def as_dict(self):
        return asdict(self)


def probe(src: Path, ffprobe: str) -> AudioInfo:
    cmd = [ffprobe, "-v", "error", "-print_format", "json",
           "-show_format", "-show_streams", str(src)]
    proc = _proc.run(cmd, timeout=120)
    if proc.returncode != 0:
        raise AudioError("ffprobe could not read %s: %s"
                         % (src.name, proc.stderr.strip() or "unknown error"))
    try:
        data = json.loads(proc.stdout)
    except ValueError as exc:
        raise AudioError("ffprobe returned unreadable output for %s" % src.name) from exc
    streams = [s for s in data.get("streams", []) if s.get("codec_type") == "audio"]
    if not streams:
        raise AudioError("%s contains no audio stream" % src.name)
    first = streams[0]
    fmt = data.get("format", {})
    duration = first.get("duration") or fmt.get("duration") or 0
    bits = first.get("bits_per_raw_sample") or first.get("bits_per_sample") or 0
    return AudioInfo(
        duration_seconds=float(duration),
        sample_rate=int(first.get("sample_rate") or 0),
        channels=int(first.get("channels") or 0),
        codec=str(first.get("codec_name") or "unknown"),
        bits_per_sample=int(bits) or None,
        container=str(fmt.get("format_name") or "unknown"),
        audio_streams=len(streams),
        size_bytes=src.stat().st_size,
    )


def _pan_filter(total_channels: int, channel: Optional[int]) -> Optional[str]:
    """ffmpeg pan filter: one channel, or an equal-weight mix of all of them.

    An explicit mix avoids ffmpeg guessing a surround layout for multitrack
    files (which would drop or attenuate some tracks).
    """
    if channel is not None:
        return "pan=mono|c0=c%d" % channel
    if total_channels <= 1:
        return None
    weight = 1.0 / total_channels
    terms = "+".join("%.6f*c%d" % (weight, i) for i in range(total_channels))
    return "pan=mono|c0=" + terms


def normalize(src: Path, dst: Path, ffmpeg: str, total_channels: int,
              channel: Optional[int] = None) -> None:
    """Write a 16 kHz mono 16-bit WAV copy of src (or of one channel) to dst."""
    cmd: List[str] = [ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "error",
                      "-y", "-i", str(src), "-map", "0:a:0", "-vn", "-sn", "-dn"]
    pan = _pan_filter(total_channels, channel)
    if pan:
        cmd += ["-af", pan]
    cmd += ["-ar", "16000", "-c:a", "pcm_s16le", str(dst)]
    proc = _proc.run(cmd)
    if proc.returncode != 0 or not dst.exists() or dst.stat().st_size <= 44:
        raise AudioError("ffmpeg could not convert %s: %s"
                         % (src.name, proc.stderr.strip() or "no audio produced"))


def wav_missing_bytes(path: Path) -> int:
    """How many bytes a WAV's header says are still missing (0 if complete).

    A file that is still being copied has its full length in the header but
    not yet on disk. Headers that carry no usable length (streamed recordings,
    RF64, non-WAV files) return 0.
    """
    try:
        with open(path, "rb") as fh:
            head = fh.read(12)
        actual = path.stat().st_size
    except OSError:
        return 0
    if len(head) < 12 or head[:4] != b"RIFF" or head[8:12] != b"WAVE":
        return 0
    declared = struct.unpack("<I", head[4:8])[0]
    if declared in (0, 0xFFFFFFFF):
        return 0
    return max(0, declared + 8 - actual)
