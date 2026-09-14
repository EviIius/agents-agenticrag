from __future__ import annotations

import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen

from _bootstrap import SRC  # noqa: F401
from agenticrag.server import WorkbenchState, make_handler


class _FakeRuntimeHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        body = json.dumps({"data": [{"id": "test-model"}]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers["Content-Length"])
        self.rfile.read(length)
        content = json.dumps({"answer": 18, "action": "calculate", "assumptions": []})
        body = json.dumps({"choices": [{"message": {"content": content}}]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        del format, args


class WorkbenchStateTests(unittest.TestCase):
    def test_bootstrap_exposes_real_capability_boundary_without_provider_setup(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "analysis" / "SKILL.md"
            skill.parent.mkdir()
            skill.write_text(
                "---\nname: analysis\ndescription: Inspect evidence.\n---\nUse cited evidence.",
                encoding="utf-8",
            )
            state = WorkbenchState(":memory:", root)
            payload = state.bootstrap()
        self.assertEqual(payload["version"], "0.4.0")
        self.assertEqual(
            [tool["id"] for tool in payload["capabilities"]["tools"]],
            ["search", "lookup", "calculate", "web_search"],
        )
        self.assertFalse(payload["capabilities"]["tools"][-1]["enabled"])
        self.assertIn("supervisor", [agent["id"] for agent in payload["capabilities"]["agents"]])
        self.assertEqual(payload["capabilities"]["skills"][0]["name"], "analysis")
        self.assertEqual(payload["capabilities"]["plugins"], [])

    def test_session_configuration_never_exposes_api_key(self) -> None:
        state = WorkbenchState(":memory:", Path("missing-skills"))
        public = state.configure(
            {
                "role": "chat",
                "runtime": "vllm",
                "base_url": "http://127.0.0.1:8000/v1",
                "model": "research-model",
                "structured_output_mode": "json_schema",
                "api_key": "secret-value",
            }
        )
        self.assertTrue(public["credential_configured"])
        self.assertNotIn("secret-value", repr(public))

    def test_http_api_probes_and_checks_an_openai_compatible_model(self) -> None:
        runtime = ThreadingHTTPServer(("127.0.0.1", 0), _FakeRuntimeHandler)
        state = WorkbenchState(":memory:", Path("missing-skills"))
        workbench = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(state))
        runtime_thread = threading.Thread(target=runtime.serve_forever, daemon=True)
        workbench_thread = threading.Thread(target=workbench.serve_forever, daemon=True)
        runtime_thread.start()
        workbench_thread.start()
        base = f"http://127.0.0.1:{workbench.server_port}"
        runtime_base = f"http://127.0.0.1:{runtime.server_port}/v1"
        try:
            configured = self._post(
                f"{base}/api/v1/configure",
                {
                    "role": "chat",
                    "runtime": "openai-compatible",
                    "base_url": runtime_base,
                    "model": "test-model",
                    "structured_output_mode": "json_schema",
                },
            )
            self.assertEqual(configured["provider"]["model"], "test-model")
            probe = self._post(
                f"{base}/api/v1/probe",
                {
                    "role": "chat",
                    "runtime": "openai-compatible",
                    "base_url": runtime_base,
                    "model": "",
                    "structured_output_mode": "json_schema",
                },
            )
            self.assertEqual(probe["models"], ["test-model"])
            contract = self._post(f"{base}/api/v1/check-model", {})
            self.assertTrue(contract["compatible"])
            self.assertTrue(contract["checks"]["host_validation"])
            with urlopen(f"{base}/") as response:
                self.assertIn("default-src 'self'", response.headers["Content-Security-Policy"])
                self.assertIn(b"AgenticRAG Workbench", response.read())
        finally:
            workbench.shutdown()
            runtime.shutdown()
            workbench.server_close()
            runtime.server_close()
            workbench_thread.join(timeout=2)
            runtime_thread.join(timeout=2)

    @staticmethod
    def _post(url: str, payload: dict[str, object]) -> dict[str, object]:
        data = json.dumps(payload).encode()
        request = Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=3) as response:
            return json.loads(response.read().decode())


if __name__ == "__main__":
    unittest.main()
