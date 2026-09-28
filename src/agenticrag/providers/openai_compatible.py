from __future__ import annotations

import json
import threading
import time
from collections.abc import Callable, Sequence
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ..config import ProviderConfig, ProviderRole
from ..errors import ConfigurationError, ProviderError
from .base import ChatMessage


Transport = Callable[[Request, float], bytes]


def _default_transport(request: Request, timeout: float) -> bytes:
    with urlopen(request, timeout=timeout) as response:  # noqa: S310 - URL is validated in config
        return response.read()


class _OpenAICompatibleBase:
    def __init__(self, config: ProviderConfig, transport: Transport | None = None) -> None:
        self.config = config
        self._transport = transport or _default_transport

    @property
    def label(self) -> str:
        return self.config.label

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        headers = {"Content-Type": "application/json", "User-Agent": "agenticrag/0.2"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        request = Request(
            f"{self.config.base_url}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            raw = self._transport(request, self.config.timeout_seconds)
        except HTTPError as exc:
            raise ProviderError(f"Provider returned HTTP {exc.code}") from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise ProviderError(f"Provider request failed: {exc}") from exc
        try:
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ProviderError("Provider returned a non-JSON response") from exc
        if not isinstance(value, dict):
            raise ProviderError("Provider response must be a JSON object")
        if "error" in value:
            raise ProviderError("Provider reported an error")
        return value


class OpenAICompatibleChat(_OpenAICompatibleBase):
    """Small explicit client shared by local servers and opt-in OpenAI comparisons."""

    def __init__(self, config: ProviderConfig, transport: Transport | None = None) -> None:
        if config.role is not ProviderRole.CHAT:
            raise ConfigurationError("Chat adapter requires a chat provider configuration")
        super().__init__(config, transport)
        self._inference_slot = threading.Lock()
        self._call_state = threading.local()

    def last_call_metrics(self) -> dict[str, int] | None:
        """Return counts for this thread's most recent non-streaming completion."""
        value = getattr(self._call_state, "metrics", None)
        return dict(value) if value is not None else None

    def complete(
        self,
        messages: Sequence[ChatMessage],
        *,
        response_schema: dict[str, Any] | None = None,
        max_tokens: int = 2048,
        temperature: float = 0.0,
    ) -> str:
        self._call_state.metrics = None
        started = time.perf_counter()
        responses: list[dict[str, Any]] = []
        request_messages = list(messages)
        payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": [],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if self.config.runtime == "ollama":
            # Ollama's thinking models can exhaust max_tokens before writing final content.
            # These bounded workflows need the final answer, not a reasoning trace.
            payload["reasoning_effort"] = "none"
        if response_schema is not None:
            schema_text = json.dumps(response_schema, separators=(",", ":"))
            if self.config.structured_output_mode == "json_schema":
                payload["response_format"] = {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "agenticrag_response",
                        "strict": True,
                        "schema": response_schema,
                    },
                }
            elif self.config.structured_output_mode == "json_object":
                payload["response_format"] = {"type": "json_object"}
                request_messages.insert(
                    0,
                    ChatMessage(
                        "system",
                        "Return one JSON object only. It must satisfy this JSON Schema: "
                        + schema_text,
                    ),
                )
            else:
                request_messages.insert(
                    0,
                    ChatMessage(
                        "system",
                        "Return one JSON object only, without markdown fences or commentary. "
                        "It must satisfy this JSON Schema: "
                        + schema_text,
                    ),
                )
        payload["messages"] = [
            {
                "role": message.role,
                "content": (
                    [{"type": "text", "text": message.content},
                     {"type": "image_url", "image_url": message.image_data_url}]
                    if message.image_data_url else message.content
                ),
            }
            for message in request_messages
        ]
        with self._inference_slot:
            response = self._post("/chat/completions", payload)
            responses.append(response)
            content = _chat_content(response)
            invalid_structured = response_schema is not None and not _is_json_object(content)
            if self.config.runtime == "ollama" and (content is None or invalid_structured):
                retry_payload = {**payload, "max_tokens": min(max_tokens * 2, 8_192)}
                if response_schema is not None and self.config.structured_output_mode == "json_schema":
                    # Some Ollama models emit a native tool call or malformed text even
                    # though the request asks for schema-constrained final content.
                    retry_payload["response_format"] = {"type": "json_object"}
                    retry_payload["messages"] = [
                        {
                            "role": "system",
                            "content": (
                                "Return one JSON object as final message content. Do not call tools. "
                                "It must satisfy this JSON Schema: " + schema_text
                            ),
                        },
                        *payload["messages"],
                    ]
                elif content is None:
                    retry_payload["messages"] = [
                        {"role": "system", "content": "Answer the user's request in final message text. Do not call tools."},
                        *payload["messages"],
                    ]
                response = self._post("/chat/completions", retry_payload)
                responses.append(response)
                content = _chat_content(response)
        if content is None:
            choice = response.get("choices", [{}])[0]
            finish = choice.get("finish_reason", "unknown") if isinstance(choice, dict) else "unknown"
            raise ProviderError(f"Model returned no final answer (finish reason: {finish})")
        if response_schema is not None and not _is_json_object(content):
            raise ProviderError("Model returned invalid structured JSON after the bounded retry")
        metrics = {
            "elapsed_ms": max(0, round((time.perf_counter() - started) * 1_000)),
            "request_attempts": len(responses),
        }
        for metric, usage_key in (
            ("prompt_tokens", "prompt_tokens"),
            ("completion_tokens", "completion_tokens"),
        ):
            values = [item.get("usage", {}).get(usage_key) if isinstance(item.get("usage"), dict) else None for item in responses]
            if all(type(value) is int and value >= 0 for value in values):
                metrics[metric] = sum(values)
        cached = [
            item["usage"].get("prompt_tokens_details", {}).get("cached_tokens")
            if isinstance(item.get("usage"), dict)
            and isinstance(item["usage"].get("prompt_tokens_details"), dict)
            else None
            for item in responses
        ]
        if all(type(value) is int and value >= 0 for value in cached):
            metrics["cached_prompt_tokens"] = sum(cached)
        self._call_state.metrics = metrics
        return content

    def stream_complete(
        self, messages: Sequence[ChatMessage], on_token: Callable[[str], None], *,
        max_tokens: int = 2048, temperature: float = 0.0,
    ) -> str:
        """Stream final answer text from an OpenAI-compatible chat endpoint."""
        if self._transport is not _default_transport:
            answer = self.complete(messages, max_tokens=max_tokens, temperature=temperature)
            on_token(answer)
            return answer
        payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": [
                {"role": item.role, "content": (
                    [{"type": "text", "text": item.content},
                     {"type": "image_url", "image_url": item.image_data_url}]
                    if item.image_data_url else item.content
                )} for item in messages
            ],
            "max_tokens": max_tokens, "temperature": temperature, "stream": True,
        }
        if self.config.runtime == "ollama":
            payload["reasoning_effort"] = "none"
        headers = {"Content-Type": "application/json", "Accept": "text/event-stream", "User-Agent": "agenticrag/0.4"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        request = Request(
            f"{self.config.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST",
        )
        parts: list[str] = []
        total_chars = 0
        started = time.monotonic()
        try:
            with self._inference_slot, urlopen(request, timeout=self.config.timeout_seconds) as response:  # noqa: S310 - configured endpoint is validated
                for line in response:
                    if time.monotonic() - started > self.config.timeout_seconds * 2:
                        raise ProviderError("Streaming answer exceeded the time limit")
                    if not line.startswith(b"data: "):
                        continue
                    data = line[6:].strip()
                    if data == b"[DONE]":
                        break
                    try:
                        event = json.loads(data)
                        token = event["choices"][0]["delta"].get("content")
                    except (UnicodeDecodeError, json.JSONDecodeError, KeyError, IndexError, TypeError):
                        continue
                    if not isinstance(token, str) or not token:
                        continue
                    parts.append(token)
                    total_chars += len(token)
                    if total_chars > 120_000:
                        raise ProviderError("Streaming answer exceeded the text limit")
                    on_token(token)
        except HTTPError as exc:
            raise ProviderError(f"Provider returned HTTP {exc.code}") from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise ProviderError(f"Provider stream failed: {exc}") from exc
        answer = "".join(parts).strip()
        if not answer:
            raise ProviderError("Model streamed no final answer")
        return answer


def _chat_content(response: dict[str, Any]) -> str | None:
    try:
        content = response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ProviderError("Chat response is missing choices[0].message.content") from exc
    return content if isinstance(content, str) and content.strip() else None


def _is_json_object(content: str | None) -> bool:
    if content is None:
        return False
    try:
        return isinstance(json.loads(content), dict)
    except json.JSONDecodeError:
        return False


class OpenAICompatibleEmbedding(_OpenAICompatibleBase):
    def __init__(self, config: ProviderConfig, transport: Transport | None = None) -> None:
        if config.role is not ProviderRole.EMBEDDING:
            raise ConfigurationError("Embedding adapter requires an embedding provider configuration")
        super().__init__(config, transport)

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        response = self._post("/embeddings", {"model": self.config.model, "input": list(texts)})
        try:
            rows = sorted(response["data"], key=lambda row: row["index"])
            vectors = [row["embedding"] for row in rows]
        except (KeyError, TypeError) as exc:
            raise ProviderError("Embedding response is missing indexed vectors") from exc
        if len(vectors) != len(texts):
            raise ProviderError("Embedding response count does not match input count")
        dimension: int | None = None
        normalized: list[list[float]] = []
        for vector in vectors:
            if not isinstance(vector, list) or not vector:
                raise ProviderError("Embedding vectors must be non-empty arrays")
            try:
                numeric = [float(value) for value in vector]
            except (TypeError, ValueError) as exc:
                raise ProviderError("Embedding vectors must contain numeric values") from exc
            dimension = len(numeric) if dimension is None else dimension
            if len(numeric) != dimension:
                raise ProviderError("Embedding response contains inconsistent dimensions")
            normalized.append(numeric)
        return normalized


def build_chat_provider(config: ProviderConfig) -> OpenAICompatibleChat | Any:
    if config.kind == "openai":
        from .openai_responses import OpenAIResponsesChat

        return OpenAIResponsesChat(config)
    return OpenAICompatibleChat(config)


def build_embedding_provider(config: ProviderConfig) -> OpenAICompatibleEmbedding:
    return OpenAICompatibleEmbedding(config)
