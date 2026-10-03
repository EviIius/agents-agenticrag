import os
import shutil
import unittest

from localtranscribe.watcher import Watcher

from .helpers import HAVE_FFMPEG, PipelineCase, make_recording, sha256


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


@unittest.skipUnless(HAVE_FFMPEG, "ffmpeg and ffprobe are required")
class WatcherTests(PipelineCase):
    def setUp(self):
        super().setUp()
        self.clock = FakeClock()
        self.watcher = Watcher(self.cfg, clock=self.clock)
        self.inbox, self.done, self.failed = (
            self.cfg.inbox_dir, self.cfg.done_dir, self.cfg.failed_dir)

    def names(self, folder):
        return sorted(p.name for p in folder.iterdir())

    def drop(self, name="meeting.wav", **kwargs):
        staged = make_recording(self.tmp / name, kwargs.pop("bursts", {0: [(0.5, 1.5)]}), **kwargs)
        dest = self.inbox / name
        shutil.copy2(staged, dest)
        return dest

    def settle(self):
        """One pass to notice files, then enough quiet time for them to count."""
        self.watcher.run_once()
        self.clock.advance(11)
        return self.watcher.run_once()

    def test_file_moves_to_done_with_its_transcripts(self):
        src = self.drop()
        before = sha256(src)
        self.assertEqual(self.watcher.run_once(), 0, "must wait before touching a new file")
        self.assertEqual(self.names(self.inbox), ["meeting.wav"])
        self.clock.advance(11)
        self.assertEqual(self.watcher.run_once(), 1)
        self.assertEqual(self.names(self.inbox), [])
        self.assertEqual(self.names(self.done),
                         ["meeting.json", "meeting.srt", "meeting.txt", "meeting.wav"])
        self.assertEqual(sha256(self.done / "meeting.wav"), before)
        self.assertEqual(self.names(self.failed), [])
        self.assertEqual(list(self.cfg.work_dir.iterdir()), [])

    def test_file_still_growing_is_left_alone(self):
        src = self.drop()
        self.watcher.run_once()
        for _ in range(5):                      # another chunk lands every 8 s
            self.clock.advance(8)
            with open(src, "ab") as fh:
                fh.write(b"\0" * 1024)
            self.assertEqual(self.watcher.run_once(), 0)
        self.assertEqual(self.names(self.done), [])
        self.clock.advance(11)                  # copy finished
        self.assertEqual(self.watcher.run_once(), 1)

    def test_half_copied_wav_waits_for_the_rest(self):
        whole = make_recording(self.tmp / "long.wav", {0: [(0.5, 1.5)]})
        data = whole.read_bytes()
        dest = self.inbox / "long.wav"
        dest.write_bytes(data[: len(data) // 2])   # header promises twice this
        self.assertEqual(self.settle(), 0)
        self.clock.advance(120)
        self.assertEqual(self.watcher.run_once(), 0)
        dest.write_bytes(data)                     # the rest arrives
        self.assertEqual(self.settle(), 1)
        self.assertIn("long.txt", self.names(self.done))

    def test_wav_that_never_completes_is_transcribed_with_a_warning(self):
        whole = make_recording(self.tmp / "cut.wav", {0: [(0.5, 1.5)]})
        data = whole.read_bytes()
        (self.inbox / "cut.wav").write_bytes(data[: len(data) // 2])
        self.watcher.run_once()
        self.clock.advance(301)
        self.assertEqual(self.watcher.run_once(), 1)
        report = (self.done / "cut.json").read_text()
        self.assertIn("recording may be cut short", report)

    def test_unreadable_audio_goes_to_failed_with_a_log(self):
        bad = self.inbox / "broken.mp3"
        bad.write_bytes(b"definitely not an mp3")
        self.assertEqual(self.settle(), 1)
        self.assertEqual(self.names(self.inbox), [])
        self.assertEqual(self.names(self.failed), ["broken.log", "broken.mp3"])
        self.assertEqual((self.failed / "broken.mp3").read_bytes(), b"definitely not an mp3")
        log = (self.failed / "broken.log").read_text()
        self.assertIn("ffprobe could not read broken.mp3", log)
        self.assertEqual(self.names(self.done), [])

    def test_whisper_failure_goes_to_failed(self):
        self.drop()
        os.environ["FAKE_WHISPER_FAIL"] = "1"
        self.addCleanup(os.environ.pop, "FAKE_WHISPER_FAIL", None)
        self.settle()
        self.assertEqual(self.names(self.failed), ["meeting.log", "meeting.wav"])
        self.assertIn("failed to initialize whisper context",
                      (self.failed / "meeting.log").read_text())

    def test_same_name_twice_does_not_overwrite(self):
        self.drop()
        self.settle()
        first = (self.done / "meeting.txt").read_text()
        self.drop(bursts={0: [(2.0, 3.0)]})
        self.settle()
        self.assertEqual(self.names(self.done), [
            "meeting-2.json", "meeting-2.srt", "meeting-2.txt", "meeting-2.wav",
            "meeting.json", "meeting.srt", "meeting.txt", "meeting.wav"])
        self.assertEqual((self.done / "meeting.txt").read_text(), first)
        self.assertIn("00:00:02,000", (self.done / "meeting-2.srt").read_text())

    def test_ignores_temp_hidden_and_non_audio_files(self):
        for name in (".hidden.wav", "upload.wav.part", "notes.txt", ".DS_Store",
                     "x.wav.crdownload"):
            (self.inbox / name).write_bytes(b"x")
        (self.inbox / "subfolder").mkdir()
        self.assertEqual(self.settle(), 0)
        self.assertEqual(len(self.names(self.inbox)), 6)
        self.assertEqual(self.names(self.done) + self.names(self.failed), [])

    def test_files_wait_in_inbox_while_setup_is_broken(self):
        self.drop()
        self.model.unlink()                       # e.g. model not downloaded yet
        self.assertEqual(self.settle(), 0)
        self.assertEqual(self.names(self.inbox), ["meeting.wav"])
        self.assertEqual(self.names(self.failed), [])
        self.model.write_bytes(b"model is back")
        self.assertEqual(self.watcher.run_once(), 1)
        self.assertIn("meeting.txt", self.names(self.done))

    def test_oldest_file_is_handled_first(self):
        a = self.drop("b-first.wav")
        b = self.drop("a-second.wav")
        os.utime(a, (1000, 1000))
        os.utime(b, (2000, 2000))
        order = []
        self.watcher.process = lambda src, warnings=None: order.append(src.name)
        self.settle()
        self.assertEqual(order, ["b-first.wav", "a-second.wav"])


if __name__ == "__main__":
    unittest.main()
