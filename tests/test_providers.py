from __future__ import annotations

import json
import unittest
from urllib.request import Request

from _bootstrap import SRC  # noqa: F401
from agenticrag.config import ProviderConfig, ProviderRole
from agenticrag.errors import ConfigurationError, ProviderError
from agenticrag.providers.base import ChatMessage
from agenticrag.providers.openai_compatible import OpenAICompatibleChat, OpenAICompatibleEmbedding


class ProviderAdapterTests(unittest.TestCase):
    def test_chat_sends_schema_and_local_request_has_no_authorization(self) -> None:
        captured: dict[str, object] = {}

        def transport(request: Request, timeout: float) -> bytes:
            captured["url"] = request.full_url
            captured["authorization"] = request.get_header("Authorization")
            captured["timeout"] = timeout
            captured["body"] = json.loads((request.data or b"").decode("utf-8"))
            return json.dumps({"choices": [{"message": {"content": "{\"ok\":true}"}}]}).encode()

        config = ProviderConfig(
            "local", ProviderRole.CHAT, "http://127.0.0.1:8080/v1", "qwen", None, 12.0
        )
        result = OpenAICompatibleChat(config, transport).complete(
            [ChatMessage("user", "hello")], response_schema={"type": "object"}
        )
        self.assertEqual(result, '{"ok":true}')
        self.assertIsNone(captured["authorization"])
        self.assertEqual(captured["url"], "http://127.0.0.1:8080/v1/chat/completions")
        self.assertIn("response_format", captured["body"])

    def test_embedding_response_is_ordered_by_index(self) -> None:
        def transport(request: Request, timeout: float) -> bytes:
            del request, timeout
            return json.dumps(
                {
                    "data": [
                        {"index": 1, "embedding": [3, 4]},
                        {"index": 0, "embedding": [1, 2]},
                    ]
                }
            ).encode()

        config = ProviderConfig(
            "local", ProviderRole.EMBEDDING, "http://127.0.0.1:8081/v1", "embed", None, 12.0
        )
        vectors = OpenAICompatibleEmbedding(config, transport).embed(["first", "second"])
        self.assertEqual(vectors, [[1.0, 2.0], [3.0, 4.0]])

    def test_prompt_structured_mode_embeds_schema_without_response_format(self) -> None:
        captured: dict[str, object] = {}

        def transport(request: Request, timeout: float) -> bytes:
            del timeout
            captured.update(json.loads((request.data or b"").decode("utf-8")))
            return json.dumps({"choices": [{"message": {"content": "{\"ok\":true}"}}]}).encode()

        config = ProviderConfig(
            "local",
            ProviderRole.CHAT,
            "http://127.0.0.1:8080/v1",
            "minimal-model",
            None,
            12.0,
            "prompt",
        )
        OpenAICompatibleChat(config, transport).complete(
            [ChatMessage("user", "hello")], response_schema={"type": "object"}
        )
        self.assertNotIn("response_format", captured)
        self.assertIn("JSON Schema", captured["messages"][0]["content"])

    def test_adapter_rejects_wrong_role(self) -> None:
        config = ProviderConfig(
            "local", ProviderRole.EMBEDDING, "http://127.0.0.1:8081/v1", "embed", None, 12.0
        )
        with self.assertRaises(ConfigurationError):
            OpenAICompatibleChat(config)

    def test_provider_error_does_not_trigger_a_second_transport(self) -> None:
        calls = 0

        def transport(request: Request, timeout: float) -> bytes:
            nonlocal calls
            del request, timeout
            calls += 1
            return json.dumps({"error": {"message": "offline"}}).encode()

        config = ProviderConfig(
            "local", ProviderRole.CHAT, "http://127.0.0.1:8080/v1", "qwen", None, 12.0
        )
        with self.assertRaises(ProviderError):
            OpenAICompatibleChat(config, transport).complete([ChatMessage("user", "hello")])
        self.assertEqual(calls, 1)


if __name__ == "__main__":
    unittest.main()
