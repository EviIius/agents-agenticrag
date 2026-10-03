import json
import os
import unittest

from localtranscribe.pipeline import transcribe_file

from .helpers import HAVE_FFMPEG, PipelineCase, make_recording, sha256


@unittest.skipUnless(HAVE_FFMPEG, "ffmpeg and ffprobe are required")
class PipelineTests(PipelineCase):
    def setUp(self):
        super().setUp()
        os.environ["FAKE_WHISPER_ARGS_LOG"] = str(self.args_log)
        self.addCleanup(os.environ.pop, "FAKE_WHISPER_ARGS_LOG", None)
        self.addCleanup(os.environ.pop, "FAKE_WHISPER_TEXT", None)
        self.out = self.tmp / "out"

    def test_field_recorder_file_becomes_three_outputs(self):
        # 96 kHz / 24-bit stereo, the kind of file a field recorder writes.
        src = make_recording(self.tmp / "meeting.wav", {0: [(0.5, 2.0)], 1: [(0.5, 2.0)]})
        before = sha256(src)
        os.environ["FAKE_WHISPER_TEXT"] = "Gismo feeds the bus cart and RASPy."

        result = transcribe_file(src, self.out, self.cfg)

        self.assertEqual(sha256(src), before, "source audio must not change")
        self.assertEqual((self.out / "meeting.txt").read_text(),
                         "GSMOS feeds the BUSCRT and RASP.\n")
        self.assertIn("00:00:00,500 --> 00:00:02,000\nGSMOS feeds", (self.out / "meeting.srt").read_text())
        data = json.loads((self.out / "meeting.json").read_text())
        self.assertEqual(data["source"]["sample_rate"], 96000)
        self.assertEqual(data["source"]["channels"], 2)
        self.assertEqual(data["source"]["bits_per_sample"], 24)
        self.assertEqual(data["channel_mode"], "mix")
        # The untouched Whisper wording is kept alongside the corrected text.
        self.assertEqual(data["raw_text"], "Gismo feeds the bus cart and RASPy.\n")
        self.assertEqual(data["segments"][0]["raw_text"], "Gismo feeds the bus cart and RASPy.")
        self.assertEqual(
            {(c["found"], c["replaced_with"]) for c in data["glossary_corrections"]},
            {("Gismo", "GSMOS"), ("bus cart", "BUSCRT"), ("RASPy", "RASP")})
        self.assertEqual(result.warnings, [])
        # Whisper got the vocabulary hint, and scratch files were cleaned up.
        (call,) = [c for c in self.whisper_calls() if "--help" not in c]
        self.assertEqual(call[call.index("--prompt") + 1],
                         "This recording mentions GSMOS, BUSCRT, RASP, Vera and FCTDS.")
        self.assertIn("--carry-initial-prompt", call)
        self.assertEqual(list(self.cfg.work_dir.iterdir()), [])

    def test_mix_keeps_speech_from_every_channel(self):
        # Left speaks at 0.5-1.5 s, right at 3-4 s: a mono mix must hold both.
        src = make_recording(self.tmp / "call.wav", {0: [(0.5, 1.5)], 1: [(3.0, 4.0)]})
        transcribe_file(src, self.out, self.cfg)
        data = json.loads((self.out / "call.json").read_text())
        self.assertEqual([(s["start"], s["end"]) for s in data["segments"]],
                         [(0.5, 1.5), (3.0, 4.0)])
        self.assertEqual(len([c for c in self.whisper_calls() if "-f" in c]), 1)

    def test_split_labels_each_channel_and_merges_by_time(self):
        src = make_recording(self.tmp / "call.wav",
                             {0: [(0.5, 1.5), (4.5, 5.5)], 1: [(2.0, 3.5)]})
        cfg = self.make_config(speaker_labels=["Me", "Them"])
        transcribe_file(src, self.out, cfg, channels="split")
        data = json.loads((self.out / "call.json").read_text())
        self.assertEqual(data["channel_mode"], "split")
        self.assertEqual([(s["speaker"], s["start"], s["end"]) for s in data["segments"]],
                         [("Me", 0.5, 1.5), ("Them", 2.0, 3.5), ("Me", 4.5, 5.5)])
        self.assertEqual((self.out / "call.txt").read_text(),
                         "Me: speech\n\nThem: speech\n\nMe: speech\n")
        self.assertEqual(len([c for c in self.whisper_calls() if "-f" in c]), 2)

    def test_four_track_file_mixes_every_track(self):
        src = make_recording(self.tmp / "multi.wav", {3: [(1.0, 2.0)]}, channels=4, rate=48000)
        transcribe_file(src, self.out, self.cfg)
        data = json.loads((self.out / "multi.json").read_text())
        self.assertEqual(data["source"]["channels"], 4)
        self.assertEqual([(s["start"], s["end"]) for s in data["segments"]], [(1.0, 2.0)])

    def test_other_formats(self):
        for name, codec in (("float.wav", "pcm_f32le"), ("voice.m4a", "aac"),
                            ("voice.flac", "flac"), ("voice.mp3", "libmp3lame")):
            with self.subTest(name):
                src = make_recording(self.tmp / name, {0: [(1.0, 2.0)]}, channels=1, rate=44100,
                                     codec=codec)
                transcribe_file(src, self.out, self.cfg)
                data = json.loads((self.out / (src.stem + ".json")).read_text())
                self.assertEqual(len(data["segments"]), 1)
                self.assertAlmostEqual(data["segments"][0]["start"], 1.0, delta=0.11)

    def test_silence_is_a_success_with_a_warning(self):
        src = make_recording(self.tmp / "quiet.wav", {})
        result = transcribe_file(src, self.out, self.cfg)
        self.assertEqual((self.out / "quiet.txt").read_text(), "")
        self.assertIn("No speech was detected in this recording.", result.warnings)

    def test_vad_model_is_used_when_present_and_reported_when_missing(self):
        src = make_recording(self.tmp / "a.wav", {0: [(1.0, 2.0)]}, channels=1)
        missing = self.make_config(use_vad=True)
        result = transcribe_file(src, self.out, missing)
        self.assertTrue(any("Voice-activity model not found" in w for w in result.warnings))
        self.assertNotIn("--vad", self.whisper_calls()[-1])
        vad = self.tmp / "vad.bin"
        vad.write_bytes(b"x")
        present = self.make_config(use_vad=True, vad_model=str(vad))
        transcribe_file(src, self.out, present)
        self.assertIn("--vad", self.whisper_calls()[-1])

    def test_older_whisper_build_still_works(self):
        # A build without --vad / --carry-initial-prompt must not fail the job.
        import shutil
        old_cli = self.tmp / "old-whisper-cli"       # separate path: flags are cached per binary
        shutil.copy2(self.cfg["whisper_cli"], old_cli)
        os.environ["FAKE_WHISPER_OLD_BUILD"] = "1"
        self.addCleanup(os.environ.pop, "FAKE_WHISPER_OLD_BUILD", None)
        vad = self.tmp / "vad.bin"
        vad.write_bytes(b"x")
        cfg = self.make_config(use_vad=True, vad_model=str(vad), whisper_cli=str(old_cli))
        src = make_recording(self.tmp / "a.wav", {0: [(1.0, 2.0)]}, channels=1)
        result = transcribe_file(src, self.out, cfg)
        self.assertEqual((self.out / "a.txt").read_text(), "speech\n")
        self.assertEqual(len(result.warnings), 2)
        call = self.whisper_calls()[-1]
        self.assertIn("--prompt", call)
        self.assertNotIn("--vad", call)
        self.assertNotIn("--carry-initial-prompt", call)

    def test_clear_errors(self):
        with self.assertRaisesRegex(FileNotFoundError, "No such audio file"):
            transcribe_file(self.tmp / "nope.wav", self.out, self.cfg)
        junk = self.tmp / "junk.wav"
        junk.write_bytes(b"this is not audio")
        with self.assertRaisesRegex(RuntimeError, "ffprobe could not read junk.wav"):
            transcribe_file(junk, self.out, self.cfg)
        src = make_recording(self.tmp / "a.wav", {0: [(1.0, 2.0)]}, channels=1)
        with self.assertRaisesRegex(FileNotFoundError, "Whisper model not found"):
            transcribe_file(src, self.out, self.make_config(model=str(self.tmp / "absent.bin")))
        os.environ["FAKE_WHISPER_FAIL"] = "1"
        self.addCleanup(os.environ.pop, "FAKE_WHISPER_FAIL", None)
        with self.assertRaisesRegex(RuntimeError, "failed to initialize whisper context"):
            transcribe_file(src, self.out, self.cfg)
        self.assertEqual(list(self.cfg.work_dir.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
