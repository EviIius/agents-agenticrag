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
    def test_chat_records_token_counts_and_retry_attempts(self) -> None:
        calls = 0

        def transport(request: Request, timeout: float) -> bytes:
            nonlocal calls
            del request, timeout
            calls += 1
            if calls == 1:
                return json.dumps({
                    "choices": [{"message": {"content": ""}, "finish_reason": "length"}],
                    "usage": {"prompt_tokens": 10, "completion_tokens": 4, "prompt_tokens_details": {"cached_tokens": 2}},
                }).encode()
            return json.dumps({
                "choices": [{"message": {"content": "Ready"}}],
                "usage": {"prompt_tokens": 12, "completion_tokens": 3, "prompt_tokens_details": {"cached_tokens": 4}},
            }).encode()

        config = ProviderConfig(
            "local", ProviderRole.CHAT, "http://127.0.0.1:11434/v1", "gpt-oss:20b",
            None, 12.0, runtime="ollama",
        )
        chat = OpenAICompatibleChat(config, transport)
        self.assertEqual(chat.complete([ChatMessage("user", "Reply")]), "Ready")
        self.assertEqual(chat.last_call_metrics()["request_attempts"], 2)
        self.assertEqual(chat.last_call_metrics()["prompt_tokens"], 22)
        self.assertEqual(chat.last_call_metrics()["completion_tokens"], 7)
        self.assertEqual(chat.last_call_metrics()["cached_prompt_tokens"], 6)

    def test_chat_sends_image_as_multimodal_user_content(self) -> None:
        captured = {}

        def transport(request: Request, timeout: float) -> bytes:
            del timeout
            captured.update(json.loads((request.data or b"").decode()))
            return b'{"choices":[{"message":{"content":"A red dot."}}]}'

        config = ProviderConfig("local", ProviderRole.CHAT, "http://127.0.0.1:11434/v1", "gemma4", None, 12.0)
        answer = OpenAICompatibleChat(config, transport).complete([
            ChatMessage("user", "Describe this", "data:image/png;base64,AAAA"),
        ])
        self.assertEqual(answer, "A red dot.")
        self.assertEqual(captured["messages"][0]["content"][1]["type"], "image_url")

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

    def test_ollama_requests_final_content_and_retries_an_empty_reply_once(self) -> None:
        requests: list[dict[str, object]] = []

        def transport(request: Request, timeout: float) -> bytes:
            del timeout
            requests.append(json.loads((request.data or b"").decode("utf-8")))
            content = "" if len(requests) == 1 else "Ready."
            return json.dumps({"choices": [{"message": {"content": content}, "finish_reason": "stop"}]}).encode()

        config = ProviderConfig(
            "local", ProviderRole.CHAT, "http://127.0.0.1:11434/v1", "gemma4:12b-mlx",
            None, 12.0, runtime="ollama",
        )
        self.assertEqual(
            OpenAICompatibleChat(config, transport).complete([ChatMessage("user", "hello")], max_tokens=128),
            "Ready.",
        )
        self.assertEqual(len(requests), 2)
        self.assertEqual(requests[0]["reasoning_effort"], "none")
        self.assertEqual(requests[1]["max_tokens"], 256)

    def test_empty_ollama_retry_reports_a_clear_bounded_error(self) -> None:
        calls = 0

        def transport(request: Request, timeout: float) -> bytes:
            nonlocal calls
            del request, timeout
            calls += 1
            return json.dumps({"choices": [{"message": {"content": ""}, "finish_reason": "length"}]}).encode()

        config = ProviderConfig(
            "local", ProviderRole.CHAT, "http://127.0.0.1:11434/v1", "gemma4:12b-mlx",
            None, 12.0, runtime="ollama",
        )
        with self.assertRaisesRegex(ProviderError, "no final answer.*length"):
            OpenAICompatibleChat(config, transport).complete([ChatMessage("user", "hello")])
        self.assertEqual(calls, 2)

    def test_ollama_tool_call_for_schema_falls_back_to_json_text(self) -> None:
        requests: list[dict[str, object]] = []

        def transport(request: Request, timeout: float) -> bytes:
            del timeout
            requests.append(json.loads((request.data or b"").decode("utf-8")))
            if len(requests) == 1:
                return json.dumps({"choices": [{"message": {"content": "", "tool_calls": [{"function": {"name": "browser.search"}}]}, "finish_reason": "tool_calls"}]}).encode()
            return json.dumps({"choices": [{"message": {"content": '{"action":"search"}'}, "finish_reason": "stop"}]}).encode()

        config = ProviderConfig(
            "local", ProviderRole.CHAT, "http://127.0.0.1:11434/v1", "gpt-oss:20b",
            None, 12.0, "json_schema", "ollama",
        )
        answer = OpenAICompatibleChat(config, transport).complete(
            [ChatMessage("user", "Search my corpus")], response_schema={"type": "object"}
        )
        self.assertEqual(answer, '{"action":"search"}')
        self.assertEqual(requests[1]["response_format"], {"type": "json_object"})
        self.assertIn("Do not call tools", requests[1]["messages"][0]["content"])

    def test_ollama_unrequested_tool_call_retries_as_final_text(self) -> None:
        requests: list[dict[str, object]] = []

        def transport(request: Request, timeout: float) -> bytes:
            del timeout
            requests.append(json.loads((request.data or b"").decode("utf-8")))
            if len(requests) == 1:
                return json.dumps({"choices": [{"message": {"content": "", "tool_calls": [{"function": {"name": "search"}}]}, "finish_reason": "tool_calls"}]}).encode()
            return json.dumps({"choices": [{"message": {"content": "The answer is ready."}, "finish_reason": "stop"}]}).encode()

        config = ProviderConfig(
            "local", ProviderRole.CHAT, "http://127.0.0.1:11434/v1", "gpt-oss:20b",
            None, 12.0, runtime="ollama",
        )
        answer = OpenAICompatibleChat(config, transport).complete([ChatMessage("user", "Answer directly")])
        self.assertEqual(answer, "The answer is ready.")
        self.assertIn("Do not call tools", requests[1]["messages"][0]["content"])

    def test_ollama_malformed_schema_text_retries_as_json_object(self) -> None:
        requests: list[dict[str, object]] = []

        def transport(request: Request, timeout: float) -> bytes:
            del timeout
            requests.append(json.loads((request.data or b"").decode("utf-8")))
            content = "Answer: scopes come from the app" if len(requests) == 1 else '{"answer":"app"}'
            return json.dumps({"choices": [{"message": {"content": content}}]}).encode()

        config = ProviderConfig(
            "local", ProviderRole.CHAT, "http://127.0.0.1:11434/v1", "gemma4:12b-mlx",
            None, 12.0, "json_schema", "ollama",
        )
        answer = OpenAICompatibleChat(config, transport).complete(
            [ChatMessage("user", "Who supplies scopes?")], response_schema={"type": "object"}
        )
        self.assertEqual(answer, '{"answer":"app"}')
        self.assertEqual(requests[1]["response_format"], {"type": "json_object"})


if __name__ == "__main__":
    unittest.main()
