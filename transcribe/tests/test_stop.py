import threading
import time
import unittest

from localtranscribe import proc
from localtranscribe.watcher import Watcher

from .helpers import HAVE_FFMPEG, PipelineCase, make_recording


class ProcTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(proc.reset)

    def test_timeout_kills_the_child(self):
        started = time.time()
        result = proc.run(["sleep", "30"], timeout=0.5)
        self.assertTrue(result.timed_out)
        self.assertLess(time.time() - started, 5)

    def test_stop_request_ends_the_running_child(self):
        threading.Timer(0.5, proc.request_stop).start()
        started = time.time()
        with self.assertRaises(proc.Stopped):
            proc.run(["sleep", "30"])
        self.assertLess(time.time() - started, 5)
        with self.assertRaises(proc.Stopped):     # and nothing new starts
            proc.run(["true"])


@unittest.skipUnless(HAVE_FFMPEG, "ffmpeg and ffprobe are required")
class StopDuringJobTests(PipelineCase):
    def test_shutdown_mid_job_leaves_the_recording_in_the_inbox(self):
        self.addCleanup(proc.reset)
        src = make_recording(self.cfg.inbox_dir / "meeting.wav", {0: [(0.5, 1.5)]})
        watcher = Watcher(self.cfg)
        watcher.stop()                       # shutdown arrives as the job starts
        self.assertFalse(watcher.process(src))
        self.assertTrue(src.exists())
        self.assertEqual(list(self.cfg.failed_dir.iterdir()), [])
        self.assertEqual(list(self.cfg.done_dir.iterdir()), [])
        self.assertEqual(list(self.cfg.work_dir.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
