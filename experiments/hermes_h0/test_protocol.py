"""Real host-policy controls with fake requests; zero inference/dependency install."""

import concurrent.futures
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from protocol import (
    FixtureTools,
    GateFailure,
    Ledger,
    TaskGate,
    calculate,
    terminate,
    validate_request,
)


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.ledger = Ledger(Path(self.temp.name) / "ledger.json")
        self.body = {
            "model": "synthetic-profile",
            "messages": [{"role": "user", "content": "fake"}],
        }

    def test_no_injected_sampling(self):
        self.assertEqual(validate_request(self.body, "synthetic-profile"), self.body)
        for key in ("temperature", "seed", "max_tokens", "top_p", "stop"):
            with self.subTest(key=key), self.assertRaises(GateFailure):
                validate_request({**self.body, key: 1}, "synthetic-profile")

    def test_explicit_parameters_must_match(self):
        request = {**self.body, "temperature": 0.2}
        self.assertEqual(
            validate_request(request, "synthetic-profile", {"temperature": 0.2}), request
        )
        for body in (self.body, {**self.body, "temperature": 0.7}):
            with self.assertRaises(GateFailure):
                validate_request(body, "synthetic-profile", {"temperature": 0.2})

    def test_model_fallback_is_rejected(self):
        with self.assertRaises(GateFailure):
            validate_request(self.body, "another-profile")

    def test_unknown_extensions_are_rejected(self):
        with self.assertRaises(GateFailure):
            validate_request(
                {**self.body, "extra_body": {"provider": "cloud"}}, "synthetic-profile"
            )

    def test_unknown_tool_is_rejected_before_admission(self):
        bad = {**self.body, "tools": [{"type": "function", "function": {"name": "terminal"}}]}
        with self.assertRaises(GateFailure):
            TaskGate(self.ledger, "one").admit(bad, "synthetic-profile")
        state = json.loads(self.ledger.path.read_text())
        self.assertEqual(state["calls"], 0)
        self.assertTrue(state["stopped"])

    def test_four_allowed_tool_names(self):
        for name in ("web_search", "read_page", "library_search", "calculator"):
            body = {**self.body, "tools": [{"type": "function", "function": {"name": name}}]}
            self.assertEqual(validate_request(body, "synthetic-profile"), body)

    def test_malformed_and_duplicate_schemas(self):
        tool = {"type": "function", "function": {"name": "calculator"}}
        for tools in (None, "calculator", [None], [{"function": []}], [tool, tool]):
            with self.subTest(tools=tools), self.assertRaises(GateFailure):
                validate_request({**self.body, "tools": tools}, "synthetic-profile")

    def test_forced_tool_must_be_in_the_actual_schema(self):
        tool = {"type": "function", "function": {"name": "calculator"}}
        good = {**self.body, "tools": [tool], "tool_choice": tool}
        self.assertEqual(validate_request(good, "synthetic-profile"), good)
        for choice in ("terminal", {"type": "function", "function": {"name": "terminal"}}):
            with self.assertRaises(GateFailure):
                validate_request(
                    {**self.body, "tools": [tool], "tool_choice": choice}, "synthetic-profile"
                )

    def test_three_calls_per_delegated_task_including_retries(self):
        self.assertEqual([self.ledger.admit("one") for _ in range(3)], [1, 2, 3])
        with self.assertRaises(GateFailure):
            self.ledger.admit("one")
        with self.assertRaises(GateFailure):
            Ledger(self.ledger.path).admit("fresh-task")
        self.assertEqual(json.loads(self.ledger.path.read_text())["calls"], 3)

    def test_baseline_only_one_call(self):
        self.ledger.admit("baseline", baseline=True)
        with self.assertRaises(GateFailure):
            self.ledger.admit("baseline", baseline=True)

    def test_global_42_call_ceiling_is_atomic(self):
        def admit(i):
            try:
                self.ledger.admit(f"synthetic-{i}")
                return True
            except GateFailure:
                return False

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            accepted = list(pool.map(admit, range(50)))
        self.assertEqual(sum(accepted), 42)
        state = json.loads(self.ledger.path.read_text())
        self.assertEqual([e["call"] for e in state["events"]], list(range(1, 43)))

    def test_timeout_stops_before_inference(self):
        now = [100.0]
        task = TaskGate(self.ledger, "slow", clock=lambda: now[0])
        now[0] = 280.0
        with self.assertRaises(GateFailure):
            task.admit(self.body, "synthetic-profile")
        self.assertEqual(json.loads(self.ledger.path.read_text())["calls"], 0)

    def test_cancellation_stops_before_inference(self):
        task = TaskGate(self.ledger, "cancelled")
        task.cancelled = True
        with self.assertRaises(GateFailure):
            task.admit(self.body, "synthetic-profile")
        self.assertEqual(json.loads(self.ledger.path.read_text())["calls"], 0)

    def test_calculator_exact_result(self):
        self.assertEqual(calculate("(120 * 3 + 180 * 2) / 12"), 60)
        self.assertEqual(calculate("300 / 480 * 100"), 62.5)

    def test_calculator_rejects_code_and_resource_abuse(self):
        for value in ("__import__('os').getcwd()", "2**999999", "1 / 0", "1e999", "10" * 110):
            with self.subTest(value=value[:30]), self.assertRaises(GateFailure):
                calculate(value)

    def test_fixture_tools_have_no_path_or_url_execution(self):
        tools = FixtureTools([{"id": "W1", "kind": "web", "text": "Synthetic"}])
        with self.assertRaises(GateFailure):
            tools.call("read_page", {"url": "file:///etc/passwd"})
        with self.assertRaises(GateFailure):
            tools.call("read_page", {"source_id": "/etc/passwd"})
        with self.assertRaises(GateFailure):
            tools.call("terminal", {"command": "anything"})

    def test_fixture_catalog_and_source_budget(self):
        source = {"id": "W1", "kind": "web", "text": "Synthetic " * 500}
        tools = FixtureTools([source])
        self.assertEqual(tools.call("read_page", {"source_id": "W1"}), source)
        self.assertEqual(tools.call("web_search", {"query": "any words"})["sources"], [source])
        with self.assertRaises(GateFailure):
            tools.call("web_search", {"query": "any words"})

    def test_owned_child_cancellation_is_reaped(self):
        process = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(60)"], start_new_session=True
        )
        self.addCleanup(lambda: terminate(process))
        terminate(process)
        self.assertIsNotNone(process.returncode)


if __name__ == "__main__":
    unittest.main()
