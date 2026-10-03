"""Shared test fixtures: synthetic recordings and a scratch config."""
import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from localtranscribe.config import load_config

FAKE_CLI = Path(__file__).with_name("fake_whisper_cli.py")
HAVE_FFMPEG = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def make_recording(path, bursts, channels=2, rate=96000, codec="pcm_s24le", seconds=6):
    """A recording in a field-recorder format (default 96 kHz / 24-bit stereo).

    bursts maps channel index -> list of (start, end) seconds that hold a tone;
    everything else is silence.
    """
    exprs = []
    for ch in range(channels):
        gates = "+".join("between(t,%s,%s)" % span for span in bursts.get(ch, [])) or "0"
        exprs.append("0.5*sin(2*PI*%d*t)*(%s)" % (300 + 200 * ch, gates))
    cmd = ["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-f", "lavfi",
           "-i", "aevalsrc='%s':s=%d:d=%s" % ("|".join(exprs), rate, seconds),
           "-c:a", codec, str(path)]
    subprocess.run(cmd, check=True)
    return Path(path)


class PipelineCase(unittest.TestCase):
    """Gives each test its own data folder, config, glossary and fake model."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="lt-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.model = self.tmp / "model.bin"
        self.model.write_bytes(b"not a real model")
        self.glossary = self.tmp / "glossary.txt"
        self.glossary.write_text(
            "GSMOS = Gismo, GISMO\nBUSCRT = bus cart, BuzzCART\n"
            "RASP = RASPy\nVera = Vira\nFCTDS\n")
        self.args_log = self.tmp / "args.log"
        self.cfg = self.make_config()
        self.cfg.ensure_dirs()

    def make_config(self, **overrides):
        values = {
            "data_dir": str(self.tmp / "data"),
            "model": str(self.model),
            "vad_model": str(self.tmp / "no-vad.bin"),
            "use_vad": False,
            "glossary": str(self.glossary),
            "whisper_cli": str(FAKE_CLI),
            "watcher": {"poll_seconds": 0.1, "settle_seconds": 10, "stalled_seconds": 300},
        }
        values.update(overrides)
        path = self.tmp / "config.json"
        path.write_text(json.dumps(values))
        return load_config(str(path))

    def whisper_calls(self):
        if not self.args_log.exists():
            return []
        return [json.loads(line) for line in self.args_log.read_text().splitlines()]
