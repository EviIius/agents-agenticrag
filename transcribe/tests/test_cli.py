"""The command line as another program would use it."""
import json
import os
import signal
import subprocess
import sys
import time
import unittest
from pathlib import Path

from .helpers import HAVE_FFMPEG, PipelineCase, make_recording

REPO = Path(__file__).resolve().parents[1]


class CliCase(PipelineCase):
    def cli(self, *args):
        env = dict(os.environ, PYTHONPATH=str(REPO))
        return [sys.executable, "-m", "localtranscribe", "--config", str(self.cfg.source), *args], env

    def run_cli(self, *args):
        cmd, env = self.cli(*args)
        return subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=120)


class DoctorJsonTests(CliCase):
    def test_reports_ready_setup_as_json(self):
        done = self.run_cli("doctor", "--json")
        data = json.loads(done.stdout)
        if not HAVE_FFMPEG:
            self.assertFalse(data["ok"])
            return
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertTrue(data["ok"])
        self.assertEqual(data["paths"]["glossary"], str(self.glossary))
        self.assertIn(".wav", data["audio_extensions"])
        self.assertEqual({c["name"] for c in data["checks"]} >= {"ffmpeg", "whisper_cli", "model"}, True)

    def test_reports_missing_model(self):
        self.model.unlink()
        done = self.run_cli("doctor", "--json")
        data = json.loads(done.stdout)
        self.assertEqual(done.returncode, 1)
        self.assertFalse(data["ok"])
        model = next(c for c in data["checks"] if c["name"] == "model")
        self.assertFalse(model["ok"])
        self.assertTrue(model["blocking"])


@unittest.skipUnless(HAVE_FFMPEG, "ffmpeg and ffprobe are required")
class RunTests(CliCase):
    def test_quiet_run_writes_json_and_prints_no_transcript(self):
        src = make_recording(self.tmp / "a.wav", {0: [(1.0, 2.0)]}, channels=1)
        done = self.run_cli("run", str(src), "--out-dir", str(self.tmp / "out"), "--quiet")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(done.stdout, "")
        data = json.loads((self.tmp / "out" / "a.json").read_text())
        self.assertEqual(data["text"], "speech\n")

    def test_failure_exits_1_with_a_message(self):
        junk = self.tmp / "junk.wav"
        junk.write_bytes(b"not audio")
        done = self.run_cli("run", str(junk), "--out-dir", str(self.tmp / "out"), "--quiet")
        self.assertEqual(done.returncode, 1)
        self.assertIn("Transcription failed: ffprobe could not read junk.wav", done.stderr)

    def test_sigterm_stops_children_and_cleans_up(self):
        src = make_recording(self.tmp / "a.wav", {0: [(1.0, 2.0)]}, channels=1)
        cmd, env = self.cli("run", str(src), "--out-dir", str(self.tmp / "out"), "--quiet")
        env["FAKE_WHISPER_SLEEP"] = "60"
        marker = self.tmp / "whisper.pid"
        env["FAKE_WHISPER_PID_FILE"] = str(marker)
        child = subprocess.Popen(cmd, env=env, stderr=subprocess.PIPE, text=True)
        deadline = time.time() + 30
        while not marker.exists() and time.time() < deadline:
            time.sleep(0.1)
        self.assertTrue(marker.exists(), "whisper stand-in never started")
        whisper_pid = int(marker.read_text())
        started = time.time()
        child.send_signal(signal.SIGTERM)
        _, err = child.communicate(timeout=20)
        self.assertLess(time.time() - started, 10)
        self.assertEqual(child.returncode, 130)
        self.assertIn("Transcription cancelled.", err)
        time.sleep(0.5)
        with self.assertRaises(ProcessLookupError, msg="whisper child must not outlive the run"):
            os.kill(whisper_pid, 0)
        self.assertEqual(list(self.cfg.work_dir.iterdir()), [])
        self.assertFalse((self.tmp / "out" / "a.json").exists())


if __name__ == "__main__":
    unittest.main()
