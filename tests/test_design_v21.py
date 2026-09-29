from __future__ import annotations

import json
import subprocess
import sys
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from urllib.request import urlopen

from _bootstrap import SRC  # noqa: F401
from agenticrag.config import ProviderConfig, ProviderRole
from agenticrag.conversations import ConversationStore
from agenticrag.runtimes import RuntimeSelection
from agenticrag.server import WorkbenchState, make_handler


ROOT = Path(__file__).resolve().parents[1]


class DesignV21Tests(unittest.TestCase):
    def test_theme_contrast_matrix(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "docs/design-handoff/v2.1/tools/check_contrast.py"),
             str(ROOT / "src/agenticrag/ui/tokens.css")],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Checked 24 combinations.", result.stdout)

    def test_health_and_new_assets_are_served_with_correct_cache_headers(self) -> None:
        state = WorkbenchState(":memory:", Path("missing-skills"))
        server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(state))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f"http://127.0.0.1:{server.server_port}"
        try:
            started = time.perf_counter()
            with urlopen(base + "/api/v1/health", timeout=2) as response:
                health = json.load(response)
                self.assertEqual(response.headers["Cache-Control"], "no-store")
            self.assertLess(time.perf_counter() - started, 0.5)
            self.assertTrue(health["ok"])
            self.assertEqual(health["asset_version"], "21")
            for asset in ("/boot.js", "/sw.js"):
                with urlopen(base + asset + "?v=21", timeout=2) as response:
                    self.assertEqual(response.headers["Cache-Control"], "no-cache")
                    self.assertIn("javascript", response.headers["Content-Type"])
            for asset in ("/fonts/Literata-Variable.woff2", "/fonts/AtkinsonHyperlegibleNext-Variable.woff2"):
                with urlopen(base + asset, timeout=2) as response:
                    self.assertEqual(response.headers["Content-Type"], "font/woff2")
                    self.assertIn("immutable", response.headers["Cache-Control"])
        finally:
            server.shutdown()
            server.server_close()
            state.conversations.close()
            state.runs.close()

    def test_runtime_status_redacts_endpoint_and_limits_fresh_probe(self) -> None:
        state = WorkbenchState(":memory:", Path("missing-skills"))
        state._providers = {ProviderRole.CHAT: SimpleNamespace(
            runtime="ollama", base_url="http://user:secret@127.0.0.1:11434/v1/private?key=secret",
            model="example", provider_config=lambda: ProviderConfig(kind="local", role=ProviderRole.CHAT,
                base_url="http://127.0.0.1:11434/v1", model="example", api_key=None, timeout_seconds=2.0),
        )}
        probe = {"latency_ms": 4, "configured_model_available": False}
        with patch("agenticrag.server.discover_models", return_value=probe) as discover, patch("agenticrag.server._loaded_model_state", return_value=None):
            first = state.runtime_status(fresh=True)
            second = state.runtime_status(fresh=True)
            self.assertEqual(discover.call_count, 1)
            self.assertEqual(first, second)
        chat = first["chat"]
        self.assertEqual(chat["endpoint"], "127.0.0.1:11434")
        self.assertEqual(chat["error_kind"], "model_missing")
        self.assertNotIn("secret", json.dumps(first))
        state.conversations.close()
        state.runs.close()

    def test_chat_rename_pin_and_move_keep_messages(self) -> None:
        store = ConversationStore(":memory:")
        chat = store.create("research", ["private"])
        project = store.create_project("Another library")
        store.rename(chat["id"], "  A   better  name ")
        store.set_pinned(chat["id"], True)
        moved = store.move(chat["id"], project["id"])
        self.assertEqual(moved["title"], "A better name")
        self.assertTrue(moved["pinned"])
        self.assertEqual(moved["collection"], project["collection"])
        store.close()

    def test_warm_up_is_bounded_to_one_background_request(self) -> None:
        started = threading.Event()
        release = threading.Event()

        class Runtime(BaseHTTPRequestHandler):
            def do_POST(self) -> None:  # noqa: N802
                started.set()
                release.wait(2)
                self.send_response(200)
                self.send_header("Content-Length", "2")
                self.end_headers()
                self.wfile.write(b"{}")

            def log_message(self, *_args: object) -> None:
                pass

        runtime = ThreadingHTTPServer(("127.0.0.1", 0), Runtime)
        thread = threading.Thread(target=runtime.serve_forever, daemon=True)
        thread.start()
        state = WorkbenchState(":memory:", Path("missing-skills"))
        state._providers[ProviderRole.CHAT] = RuntimeSelection(
            runtime="ollama", role=ProviderRole.CHAT,
            base_url=f"http://127.0.0.1:{runtime.server_port}/v1", model="example",
        )
        try:
            self.assertEqual(state.warm_chat_model(), {"started": True})
            self.assertTrue(started.wait(1))
            self.assertEqual(state.warm_chat_model(), {"started": False})
            release.set()
            for _ in range(100):
                if not state._warm_active:
                    break
                time.sleep(0.01)
            self.assertFalse(state._warm_active)
        finally:
            release.set()
            runtime.shutdown()
            runtime.server_close()
            state.conversations.close()
            state.runs.close()


if __name__ == "__main__":
    unittest.main()
