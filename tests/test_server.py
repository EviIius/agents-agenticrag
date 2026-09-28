from __future__ import annotations

import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen

from _bootstrap import SRC  # noqa: F401
from agenticrag.server import WorkbenchState, _ProjectMemoryChat, _is_conversation_question, _validated_chat_image, make_handler
from agenticrag.providers.base import ChatMessage
from agenticrag.domain import RunEvent


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
        request = json.loads(self.rfile.read(length))
        if request.get("stream"):
            body = (
                'data: {"choices":[{"delta":{"content":"streamed "}}]}\n\n'
                'data: {"choices":[{"delta":{"content":"answer"}}]}\n\n'
                'data: [DONE]\n\n'
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
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
    def test_stream_emits_live_event_and_evidence_frames(self) -> None:
        state = WorkbenchState(":memory:", Path("missing-skills"))
        handler = make_handler(state)

        def fake_ask(self, payload, **kwargs):  # type: ignore[no-untyped-def]
            kwargs["on_event"](RunEvent("plan_created", {"obligation_count": 1}, at_ms=5))
            kwargs["on_evidence"]([{"chunk_id": "chunk_1", "logical_path": "note.md", "heading": "Summary"}])
            return {"answer": "Done"}

        handler._ask = fake_ask
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            request = Request(
                f"http://127.0.0.1:{server.server_port}/api/v1/ask-stream",
                data=json.dumps({"run_id": "c" * 32}).encode(),
                headers={"Content-Type": "application/json"}, method="POST",
            )
            with urlopen(request, timeout=5) as response:
                frames = response.read().decode()
            self.assertIn('"type":"event"', frames)
            self.assertIn('"at_ms":5', frames)
            self.assertIn('"type":"evidence"', frames)
            self.assertIn('"chunk_id":"chunk_1"', frames)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_run_cancellation_sets_cooperative_stop_event(self) -> None:
        state = WorkbenchState(":memory:", Path("missing-skills"))
        event = state.start_run("b" * 32)
        self.assertTrue(state.cancel_run("b" * 32))
        self.assertTrue(event.is_set())
        state.finish_run("b" * 32)
        self.assertFalse(state.cancel_run("b" * 32))

    def test_project_notes_reach_model_as_uncited_context(self) -> None:
        class Capture:
            label = "test"

            def complete(self, messages, **kwargs):  # type: ignore[no-untyped-def]
                self.messages = messages
                return "ok"

        provider = Capture()
        wrapped = _ProjectMemoryChat(provider, [{"content": "Prefer concise answers."}])
        self.assertEqual(wrapped.complete([ChatMessage("user", "Hello")]), "ok")
        self.assertIn("never cite them as source evidence", provider.messages[0].content)
        self.assertIn("Prefer concise answers.", provider.messages[0].content)
        self.assertEqual(provider.messages[-1].content, "Hello")

    def test_image_attachment_validates_content_and_size(self) -> None:
        import base64

        image = {"filename": "photo.png", "mime_type": "image/png", "data_base64": base64.b64encode(b"\x89PNG\r\n\x1a\nabc").decode()}
        data_url, name = _validated_chat_image(image)
        self.assertEqual(name, "photo.png")
        self.assertTrue(data_url.startswith("data:image/png;base64,"))
        with self.assertRaisesRegex(ValueError, "does not match"):
            _validated_chat_image({**image, "mime_type": "image/jpeg"})

    def test_history_recall_does_not_capture_source_version_questions(self) -> None:
        self.assertTrue(_is_conversation_question("What was my previous question?"))
        self.assertTrue(_is_conversation_question("Repeat what my questions were"))
        self.assertTrue(_is_conversation_question("Repeat the full text of my first message in this chat, exactly."))
        self.assertFalse(_is_conversation_question("What is the previous version of this source?"))
        self.assertFalse(_is_conversation_question("What is the first message in this document?"))

    def test_local_model_selection_survives_server_restart_without_secrets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db_path = str(Path(directory, "corpus.db"))
            state = WorkbenchState(db_path, Path("missing-skills"))
            state.configure({
                "role": "chat",
                "runtime": "ollama",
                "base_url": "http://127.0.0.1:11434/v1",
                "model": "gemma4:12b-mlx",
                "structured_output_mode": "json_object",
            })
            restored = WorkbenchState(db_path, Path("missing-skills"))
            self.assertEqual(restored.public_providers()["chat"]["model"], "gemma4:12b-mlx")
            saved = Path(directory, "workbench-providers.json").read_text()
            self.assertNotIn("api_key", saved)
            self.assertNotIn("secret", saved)

    def test_evaluation_report_is_read_from_corpus_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = WorkbenchState(str(root / "corpus.db"), Path("missing-skills"))
            self.assertEqual(state.evaluation_report(), {"available": False})
            (root / "workbench-evaluation.json").write_text(json.dumps({
                "schema_version": 1, "case_count": 3, "groups": [],
            }))
            report = state.evaluation_report()
            self.assertTrue(report["available"])
            self.assertEqual(report["case_count"], 3)

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
            with urlopen(f"{base}/api/v1/runtime-status") as response:
                runtime_status = json.load(response)
            self.assertTrue(runtime_status["chat"]["reachable"])
            self.assertTrue(runtime_status["chat"]["model_present"])
            self.assertFalse(runtime_status["embedding"]["configured"])
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
            stream_request = Request(
                f"{base}/api/v1/ask-stream",
                data=json.dumps({
                    "run_id": "a" * 32, "question": "Say hello", "collection": "research",
                    "scopes": ["private"], "workflow": "direct",
                }).encode(),
                headers={"Content-Type": "application/json"}, method="POST",
            )
            with urlopen(stream_request, timeout=5) as response:
                events = response.read().decode()
                self.assertEqual(response.headers["Content-Type"], "text/event-stream; charset=utf-8")
            self.assertIn('"type":"started"', events)
            self.assertIn('"type":"token"', events)
            self.assertIn('"answer":"streamed answer"', events)
            self.assertIn('"type":"completed"', events)
            self.assertEqual(state._active_runs, {})
            with urlopen(f"{base}/") as response:
                self.assertIn("default-src 'self'", response.headers["Content-Security-Policy"])
                self.assertIn(b"AgenticRAG Workbench", response.read())
            with urlopen(f"{base}/manifest.webmanifest") as response:
                self.assertEqual(response.headers["Content-Type"], "application/manifest+json; charset=utf-8")
                self.assertEqual(json.load(response)["display"], "standalone")
            with urlopen(f"{base}/tokens.css") as response:
                self.assertEqual(response.headers["Content-Type"], "text/css; charset=utf-8")
                self.assertIn(b"--primary", response.read())
            with urlopen(f"{base}/design-v2.css") as response:
                self.assertEqual(response.headers["Content-Type"], "text/css; charset=utf-8")
                self.assertIn(b".sidebar", response.read())
            with urlopen(f"{base}/fonts/Newsreader-Variable.woff2") as response:
                self.assertEqual(response.headers["Content-Type"], "font/woff2")
                self.assertIn("immutable", response.headers["Cache-Control"])
                self.assertTrue(response.read(4))
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
