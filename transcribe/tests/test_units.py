import plistlib
import struct
import tempfile
import unittest
from pathlib import Path

from localtranscribe import audio, formats, launchd
from localtranscribe.config import load_config
from localtranscribe.glossary import Glossary
from localtranscribe.watcher import unique_stem
from localtranscribe.whisper import build_command, parse_segments


def glossary():
    return Glossary([("GSMOS", ["Gismo", "GISMO"]), ("BUSCRT", ["bus cart", "BuzzCART"]),
                     ("RASP", ["RASPy"]), ("Vera", ["Vira"]), ("FCTDS", [])])


class GlossaryTests(unittest.TestCase):
    def test_replaces_known_wrong_forms(self):
        text, counts = glossary().apply(
            "Gismo feeds the bus cart, and RASPy reads from Vira. GISMO again.")
        self.assertEqual(
            text, "GSMOS feeds the BUSCRT, and RASP reads from Vera. GSMOS again.")
        self.assertEqual(counts[("Gismo", "GSMOS")], 1)
        self.assertEqual(counts[("GISMO", "GSMOS")], 1)
        self.assertEqual(counts[("bus cart", "BUSCRT")], 1)

    def test_spacing_hyphen_and_case_variants(self):
        text, _ = glossary().apply("Bus-Cart, buscart, BUZZCART, gismo's, fctds")
        self.assertEqual(text, "BUSCRT, BUSCRT, BUSCRT, GSMOS's, FCTDS")

    def test_leaves_other_words_alone(self):
        original = "The omnibus cartel grasped the veranda."
        text, counts = glossary().apply(original)
        self.assertEqual(text, original)
        self.assertEqual(counts, {})

    def test_correct_text_counts_nothing(self):
        text, counts = glossary().apply("GSMOS and Vera are fine.")
        self.assertEqual(text, "GSMOS and Vera are fine.")
        self.assertEqual(counts, {})

    def test_prompt_lists_correct_forms(self):
        prompt = glossary().prompt("This recording mentions {terms}.")
        self.assertEqual(prompt, "This recording mentions GSMOS, BUSCRT, RASP, Vera and FCTDS.")
        self.assertEqual(Glossary([]).prompt("x {terms}"), "")

    def test_long_glossary_is_capped_for_the_prompt(self):
        big = Glossary([("Term%04d" % i, []) for i in range(500)])
        self.assertLessEqual(len(big.prompt("{terms}")), 620)
        self.assertTrue(big.prompt_truncated)

    def test_load_file_format(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "g.txt"
            path.write_text("# comment\n\nGSMOS = Gismo, GISMO\nORBO\n  Vera=Vira  \n")
            loaded = Glossary.load(path)
        self.assertEqual(loaded.entries,
                         [("GSMOS", ["Gismo", "GISMO"]), ("ORBO", []), ("Vera", ["Vira"])])


class FormatTests(unittest.TestCase):
    SEGS = [
        {"start": 0.0, "end": 2.5, "text": "Hello there.", "speaker": None},
        {"start": 2.6, "end": 4.0, "text": "Same paragraph.", "speaker": None},
        {"start": 7.0, "end": 3725.25, "text": "After a pause.", "speaker": None},
    ]

    def test_srt(self):
        srt = formats.to_srt(self.SEGS)
        self.assertIn("1\n00:00:00,000 --> 00:00:02,500\nHello there.\n", srt)
        self.assertIn("3\n00:00:07,000 --> 01:02:05,250\nAfter a pause.\n", srt)

    def test_text_paragraphs_on_pause(self):
        self.assertEqual(formats.to_text(self.SEGS, 2.0),
                         "Hello there. Same paragraph.\n\nAfter a pause.\n")

    def test_text_with_speakers(self):
        segs = [
            {"start": 0, "end": 1, "text": "Hi.", "speaker": "Me"},
            {"start": 1, "end": 2, "text": "How are you?", "speaker": "Me"},
            {"start": 2, "end": 3, "text": "Fine.", "speaker": "Them"},
        ]
        self.assertEqual(formats.to_text(segs, 2.0), "Me: Hi. How are you?\n\nThem: Fine.\n")
        self.assertIn("Them: Fine.", formats.to_srt(segs))

    def test_empty(self):
        self.assertEqual(formats.to_text([], 2.0), "")
        self.assertEqual(formats.to_srt([]), "")


class WhisperTests(unittest.TestCase):
    def test_parse_segments_matches_whisper_cpp_json(self):
        data = {"transcription": [
            {"timestamps": {"from": "00:00:00,000", "to": "00:00:11,000"},
             "offsets": {"from": 0, "to": 11000}, "text": " And so,  my fellow Americans"},
            {"offsets": {"from": 11000, "to": 12000}, "text": " [BLANK_AUDIO]"},
            {"offsets": {"from": 12000, "to": 13000}, "text": "  "},
        ]}
        self.assertEqual(parse_segments(data),
                         [{"start": 0.0, "end": 11.0, "text": "And so, my fellow Americans"}])

    def test_command(self):
        cmd = build_command("whisper-cli", Path("a.wav"), Path("out"), Path("m.bin"),
                            "en", 6, "hint", Path("vad.bin"), ["-bs", "8"])
        self.assertEqual(cmd[:5], ["whisper-cli", "-m", "m.bin", "-f", "a.wav"])
        for flag in ("-oj", "--carry-initial-prompt", "--vad"):
            self.assertIn(flag, cmd)
        self.assertEqual(cmd[cmd.index("--prompt") + 1], "hint")
        self.assertEqual(cmd[-2:], ["-bs", "8"])
        plain = build_command("whisper-cli", Path("a.wav"), Path("out"), Path("m.bin"),
                              "en", 6, "", None, [])
        self.assertNotIn("--prompt", plain)
        self.assertNotIn("--vad", plain)


class WavHeaderTests(unittest.TestCase):
    def _wav(self, tmp, declared, actual_payload):
        path = Path(tmp) / "x.wav"
        path.write_bytes(b"RIFF" + struct.pack("<I", declared) + b"WAVE" + b"\0" * actual_payload)
        return path

    def test_complete_truncated_and_unknown(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(audio.wav_missing_bytes(self._wav(tmp, 1004, 1000)), 0)
            self.assertEqual(audio.wav_missing_bytes(self._wav(tmp, 5004, 1000)), 4000)
            self.assertEqual(audio.wav_missing_bytes(self._wav(tmp, 0, 1000)), 0)
            self.assertEqual(audio.wav_missing_bytes(self._wav(tmp, 0xFFFFFFFF, 1000)), 0)
            other = Path(tmp) / "x.mp3"
            other.write_bytes(b"ID3" + b"\0" * 50)
            self.assertEqual(audio.wav_missing_bytes(other), 0)


class MiscTests(unittest.TestCase):
    def test_unique_stem(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            self.assertEqual(unique_stem(folder, "a", (".wav", ".txt")), "a")
            (folder / "a.txt").write_text("x")
            self.assertEqual(unique_stem(folder, "a", (".wav", ".txt")), "a-2")
            (folder / "a-2.wav").write_text("x")
            self.assertEqual(unique_stem(folder, "a", (".wav", ".txt")), "a-3")

    def test_launchd_plist(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg_path = Path(tmp) / "config.json"
            cfg_path.write_text('{"data_dir": "%s/data"}' % tmp)
            cfg = load_config(str(cfg_path))
            dest = launchd.write_plist(cfg, Path(tmp) / "agent.plist", python="/usr/bin/python3")
            with open(dest, "rb") as fh:
                plist = plistlib.load(fh)
        self.assertEqual(plist["Label"], "com.localtranscribe.watcher")
        self.assertEqual(plist["ProgramArguments"],
                         ["/usr/bin/python3", "-m", "localtranscribe",
                          "--config", str(cfg_path.resolve()), "watch"])
        self.assertTrue(plist["RunAtLoad"] and plist["KeepAlive"])
        self.assertIn("/opt/homebrew/bin", plist["EnvironmentVariables"]["PATH"])
        self.assertTrue(plist["StandardErrorPath"].endswith("logs/watcher.launchd.log"))

    def test_config_rejects_unknown_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg_path = Path(tmp) / "config.json"
            cfg_path.write_text('{"modle": "x"}')
            with self.assertRaises(ValueError):
                load_config(str(cfg_path))


if __name__ == "__main__":
    unittest.main()
