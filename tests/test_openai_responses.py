from __future__ import annotations

import json
import unittest

from _bootstrap import SRC  # noqa: F401
from agenticrag.config import ProviderConfig, ProviderRole
from agenticrag.providers.base import ChatMessage
from agenticrag.providers.openai_responses import OpenAIResponsesChat, OpenAIResponsesWebSearch


class OpenAIResponsesWebSearchTests(unittest.TestCase):
    def test_chat_uses_responses_structured_output_without_storage_or_temperature(self) -> None:
        observed: dict[str, object] = {}

        def transport(request, timeout):  # type: ignore[no-untyped-def]
            del timeout
            observed["payload"] = json.loads(request.data.decode())
            return json.dumps(
                {
                    "output": [
                        {
                            "type": "message",
                            "content": [{"type": "output_text", "text": '{"ok":true}'}],
                        }
                    ]
                }
            ).encode()

        config = ProviderConfig(
            kind="openai",
            role=ProviderRole.CHAT,
            base_url="https://api.openai.com/v1",
            model="test-model",
            api_key="test-secret",
            timeout_seconds=30,
        )
        schema = {
            "type": "object",
            "properties": {"ok": {"type": "boolean"}},
            "required": ["ok"],
            "additionalProperties": False,
        }
        answer = OpenAIResponsesChat(config, transport=transport).complete(
            [ChatMessage("system", "Be exact."), ChatMessage("user", "Return ok.")],
            response_schema=schema,
        )
        self.assertEqual(answer, '{"ok":true}')
        payload = observed["payload"]
        assert isinstance(payload, dict)
        self.assertFalse(payload["store"])
        self.assertNotIn("temperature", payload)
        self.assertEqual(payload["input"][0]["role"], "developer")
        self.assertEqual(payload["text"]["format"]["schema"], schema)

    def test_web_search_is_stateless_bounded_and_returns_sources(self) -> None:
        observed: dict[str, object] = {}

        def transport(request, timeout):  # type: ignore[no-untyped-def]
            observed["url"] = request.full_url
            observed["timeout"] = timeout
            observed["authorization"] = request.get_header("Authorization")
            observed["payload"] = json.loads(request.data.decode())
            return json.dumps(
                {
                    "output": [
                        {
                            "type": "web_search_call",
                            "action": {
                                "type": "search",
                                "sources": [{"type": "url", "url": "https://example.test/a"}],
                            },
                        },
                        {
                            "type": "message",
                            "content": [
                                {
                                    "type": "output_text",
                                    "text": "A cited finding.",
                                    "annotations": [
                                        {
                                            "type": "url_citation",
                                            "url": "https://example.test/a",
                                            "title": "Primary source",
                                        }
                                    ],
                                }
                            ],
                        },
                    ]
                }
            ).encode()

        config = ProviderConfig(
            kind="openai",
            role=ProviderRole.CHAT,
            base_url="https://api.openai.com/v1",
            model="test-model",
            api_key="test-secret",
            timeout_seconds=30,
        )
        result = OpenAIResponsesWebSearch(config, transport=transport).search("latest evidence")
        self.assertEqual(result.answer, "A cited finding.")
        self.assertEqual(result.sources[0].title, "Primary source")
        self.assertEqual(observed["url"], "https://api.openai.com/v1/responses")
        payload = observed["payload"]
        assert isinstance(payload, dict)
        self.assertFalse(payload["store"])
        self.assertEqual(payload["max_tool_calls"], 2)
        self.assertEqual(payload["tools"], [{"type": "web_search"}])


if __name__ == "__main__":
    unittest.main()
