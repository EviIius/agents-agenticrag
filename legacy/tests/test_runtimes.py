from __future__ import annotations

import json
import os
import unittest
from unittest.mock import patch

from _bootstrap import SRC  # noqa: F401
from agenticrag.config import ProviderRole
from agenticrag.errors import ConfigurationError
from agenticrag.runtimes import RuntimeSelection, discover_models


class _Response:
    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload

    def __enter__(self) -> _Response:
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def read(self, limit: int) -> bytes:
        del limit
        return json.dumps(self.payload).encode()


class RuntimeSelectionTests(unittest.TestCase):
    def test_remote_runtime_is_rejected_without_explicit_local_allowlist(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ConfigurationError, "LOCAL_RUNTIME_HOSTS"):
                RuntimeSelection(
                    "openai-compatible",
                    ProviderRole.CHAT,
                    "http://models.example.test/v1",
                    "model",
                )

    def test_explicit_container_hostname_is_allowed(self) -> None:
        with patch.dict(
            os.environ, {"AGENTICRAG_LOCAL_RUNTIME_HOSTS": "host.docker.internal"}, clear=True
        ):
            selection = RuntimeSelection(
                "lm-studio",
                ProviderRole.CHAT,
                "http://host.docker.internal:1234/v1/",
                "local-chat",
            )
        self.assertEqual(selection.base_url, "http://host.docker.internal:1234/v1")

    def test_model_discovery_reports_configured_model_and_latency(self) -> None:
        selection = RuntimeSelection(
            "ollama",
            ProviderRole.CHAT,
            "http://127.0.0.1:11434/v1",
            "qwen:test",
        )
        with patch(
            "agenticrag.runtimes.urlopen",
            return_value=_Response({"data": [{"id": "other"}, {"id": "qwen:test"}]}),
        ):
            result = discover_models(selection.provider_config())
        self.assertTrue(result["reachable"])
        self.assertTrue(result["configured_model_available"])
        self.assertEqual(result["models"], ["other", "qwen:test"])

    def test_openai_profile_is_explicit_and_restricts_key_destination(self) -> None:
        selection = RuntimeSelection(
            "openai",
            ProviderRole.CHAT,
            "https://api.openai.com/v1/",
            "test-model",
            api_key="secret",
            provider_kind="openai",
        )
        self.assertEqual(selection.provider_config().kind, "openai")
        self.assertNotIn("secret", repr(selection.public_dict()))
        with self.assertRaisesRegex(ConfigurationError, "only be sent"):
            RuntimeSelection(
                "openai",
                ProviderRole.CHAT,
                "https://lookalike.example/v1",
                "test-model",
                api_key="secret",
                provider_kind="openai",
            )


if __name__ == "__main__":
    unittest.main()
