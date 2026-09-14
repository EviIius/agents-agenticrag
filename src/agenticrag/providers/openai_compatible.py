from __future__ import annotations

import json
import threading
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

    def complete(
        self,
        messages: Sequence[ChatMessage],
        *,
        response_schema: dict[str, Any] | None = None,
        max_tokens: int = 2048,
        temperature: float = 0.0,
    ) -> str:
        request_messages = list(messages)
        payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": [],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
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
            {"role": message.role, "content": message.content} for message in request_messages
        ]
        with self._inference_slot:
            response = self._post("/chat/completions", payload)
        try:
            content = response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError("Chat response is missing choices[0].message.content") from exc
        if not isinstance(content, str) or not content.strip():
            raise ProviderError("Chat response content is empty")
        return content


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
