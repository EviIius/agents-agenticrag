"""Synthetic policy checks before freezing the real-process candidate."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from policy import AuditPolicy
from runtime_probe import GateFailure, validate_wire


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.trial = self.root / "trial"
        self.trial.mkdir()
        self.outside = self.root / "outside"
        self.outside.mkdir()
        self.events = []
        self.policy = AuditPolicy(
            self.trial,
            self.root / "source",
            [self.trial],
            12345,
            lambda kind, **data: self.events.append({"kind": kind, **data}),
        )

    def test_mutations_reject_outside_and_directory_descriptors(self):
        for event, args in [
            ("os.mkdir", (str(self.outside / "new"), 0o700, -1)),
            ("os.remove", (str(self.outside / "file"), -1)),
            ("os.rmdir", (str(self.outside), -1)),
            ("os.rename", (str(self.trial / "a"), str(self.outside / "b"), -1, -1)),
            ("os.rename", (str(self.outside / "a"), str(self.trial / "b"), -1, -1)),
            ("os.mkdir", ("new", 0o700, 9)),
            ("os.remove", ("file", 9)),
            ("os.symlink", (str(self.outside), str(self.trial / "link"), -1)),
            ("os.link", (str(self.outside / "a"), str(self.trial / "b"), -1, -1)),
        ]:
            with self.subTest(event=event), self.assertRaises(PermissionError):
                self.policy(event, args)

    def test_trial_mutations_are_allowed(self):
        a, b = str(self.trial / "a"), str(self.trial / "b")
        for event, args in [
            ("os.mkdir", (a, 0o700, -1)),
            ("os.remove", (a, -1)),
            ("os.rmdir", (a, -1)),
            ("os.rename", (a, b, -1, -1)),
            ("os.chmod", (a, 0o600, -1)),
        ]:
            self.policy(event, args)

    def test_symlink_escape_read_and_write_rejected(self):
        link = self.trial / "escape"
        link.symlink_to(self.outside, target_is_directory=True)
        for mode, flags in [("r", os.O_RDONLY), ("w", os.O_WRONLY | os.O_CREAT)]:
            with self.assertRaises(PermissionError):
                self.policy("open", (str(link / "secret"), mode, flags))

    def test_network_and_process_diagnostics_do_not_record_targets(self):
        for event, args in [
            ("socket.connect", (None, ("127.0.0.1", 11434))),
            ("subprocess.Popen", ("/private/synthetic-secret", ["private text"], None, None)),
        ]:
            with self.assertRaises(PermissionError):
                self.policy(event, args)
        rendered = str(self.events)
        self.assertNotIn("synthetic-secret", rendered)
        self.assertNotIn("private text", rendered)

    def test_only_proxy_connect_allowed(self):
        self.policy("socket.connect", (None, ("127.0.0.1", 12345)))
        with self.assertRaises(PermissionError):
            self.policy("socket.bind", (None, ("0.0.0.0", 12345)))

    def test_other_trial_home_is_not_readable(self):
        with self.assertRaises(PermissionError):
            self.policy("open", (str(self.outside / "memory.md"), "r", os.O_RDONLY))

    def test_real_python_audit_hook_blocks_synthetic_mutations(self):
        script = r"""
import os,sys
from pathlib import Path
from policy import AuditPolicy
trial, outside = map(Path, sys.argv[1:])
secret=outside/'sentinel'
secret.write_text('synthetic')
events=[]
policy=AuditPolicy(trial,trial,[trial],12345,lambda kind, **data: events.append(data))
sys.addaudithook(policy)
for action in [lambda:(outside/'new').mkdir(),lambda:secret.unlink(),
               lambda:secret.rename(trial/'stolen'),lambda:(trial/'escape').symlink_to(outside)]:
    try: action()
    except PermissionError: pass
    else: raise AssertionError('Unauthorized mutation executed')
(trial/'allowed').mkdir()
(trial/'allowed'/'file').write_text('allowed')
assert len(events)==4
"""
        result = subprocess.run(
            [sys.executable, "-c", script, str(self.trial), str(self.outside)],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.outside / "sentinel").read_text(), "synthetic")
        self.assertFalse((self.trial / "stolen").exists())


class WireTests(unittest.TestCase):
    def test_context_control_preserves_body_and_rejects_extra_sampling(self):
        base = {"model": "synthetic", "messages": [{"role": "user", "content": "fake"}]}
        body = {**base, "options": {"num_ctx": 65536}}
        self.assertIs(validate_wire(body, "synthetic"), body)
        for options in [{"num_ctx": 32768}, {"num_ctx": 65536, "temperature": 0.1}, {}, None]:
            with self.subTest(options=options), self.assertRaises(GateFailure):
                validate_wire({**base, "options": options}, "synthetic")
        with self.assertRaises(GateFailure):
            validate_wire({**body, "temperature": 1}, "synthetic")
        with self.assertRaises(GateFailure):
            validate_wire({**base, "reasoning_effort": "medium"}, "synthetic")


if __name__ == "__main__":
    unittest.main()
