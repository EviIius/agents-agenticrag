from __future__ import annotations
import json
import time
from collections.abc import Callable, Sequence
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
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
    """Plain completion adapter. Ollama uses an explicitly bounded context."""
    def __init__(self, config: ProviderConfig, transport: Transport | None = None):
        if config.role is not ProviderRole.CHAT:
            raise ConfigurationError("Chat adapter requires a chat provider configuration")
        super().__init__(config, transport)
        self._metrics = {}

    def last_call_metrics(self):
        return dict(self._metrics)

    def _request(self, messages, max_tokens, temperature, stream, response_schema=None):
        native = self.config.runtime == "ollama"
        rows = []
        for m in messages:
            if m.role not in {"system", "user", "assistant"}:
                raise ValueError("Invalid chat role")
            row = {"role": m.role, "content": m.content}
            if m.image_data_url:
                if native:
                    row["images"] = [m.image_data_url.split(",", 1)[1]]
                else:
                    row["content"] = [{"type": "text", "text": m.content},
                                      {"type": "image_url", "image_url": {"url": m.image_data_url}}]
            rows.append(row)
        payload = {"model": self.config.model, "messages": rows, "stream": stream}
        if native:
            origin = urlsplit(self.config.base_url)
            url = f"{origin.scheme}://{origin.netloc}/api/chat"
            payload["options"] = {"num_ctx": 16384, "num_predict": max_tokens, "temperature": temperature}
            payload["think"] = "low" if "gpt-oss" in self.config.model else False
            if response_schema:
                payload["format"] = response_schema
        else:
            url = self.config.base_url + "/chat/completions"
            payload.update(max_tokens=max_tokens, temperature=temperature)
            if response_schema:
                payload["response_format"] = {"type": "json_object"}
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        return Request(url, data=json.dumps(payload).encode(), headers=headers, method="POST"), native

    def complete(self, messages, *, response_schema=None, max_tokens=2048, temperature=0.0):
        request, native = self._request(messages, max_tokens, temperature, False, response_schema)
        started = time.monotonic()
        try:
            value = json.loads(self._transport(request, self.config.timeout_seconds))
            if value.get("error"):
                raise ProviderError("Provider reported an error")
            finish = value.get("done_reason") if native else value.get("choices", [{}])[0].get("finish_reason")
            if finish == "length":
                raise ProviderError("Answer reached the model output limit; the text is incomplete")
            answer = value["message"]["content"] if native else value["choices"][0]["message"]["content"]
        except HTTPError as exc:
            raise ProviderError(f"Chat provider returned HTTP {exc.code}") from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise ProviderError(f"Chat provider connection failed: {type(exc).__name__}") from exc
        except (KeyError, TypeError, ValueError, IndexError) as exc:
            raise ProviderError("Chat provider returned an invalid completion") from exc
        if not isinstance(answer, str) or not answer.strip():
            raise ProviderError("Chat provider returned no answer text")
        self._metrics = {"call_count": 1, "elapsed_ms": round((time.monotonic()-started)*1000)}
        return answer

    def stream_complete(self, messages, on_token, *, max_tokens=2048, temperature=0.0):
        if self._transport is not _default_transport:
            answer = self.complete(messages, max_tokens=max_tokens, temperature=temperature)
            on_token(answer)
            return answer
        request, native = self._request(messages, max_tokens, temperature, True)
        answer = ""
        completed = False
        started = time.monotonic()
        try:
            with urlopen(request, timeout=self.config.timeout_seconds) as response:
                if response.headers.get_content_type() == "application/json" and not native:
                    value = json.loads(response.read(2_000_001))
                    answer = value["choices"][0]["message"]["content"]
                    on_token(answer)
                    completed = True
                else:
                    for line in response:
                        if time.monotonic()-started > self.config.timeout_seconds:
                            raise ProviderError("Chat completion exceeded its time limit")
                        if len(line) > 1_000_000:
                            raise ProviderError("Chat stream frame is too large")
                        line = line.strip()
                        if not line or (not native and not line.startswith(b"data:")):
                            continue
                        raw = line if native else line[5:].strip()
                        if raw == b"[DONE]":
                            completed = True
                            break
                        value = json.loads(raw)
                        if value.get("error"):
                            raise ProviderError("Chat provider reported a stream error")
                        choices = value.get("choices") or [{}]
                        if not native and choices[0].get("finish_reason") == "length":
                            raise ProviderError("Answer reached the model output limit; the streamed text is incomplete")
                        token = value.get("message", {}).get("content", "") if native else (
                            choices[0].get("delta", {}).get("content") or "")
                        if not isinstance(token, str):
                            raise ProviderError("Invalid chat stream content")
                        answer += token
                        if len(answer) > 100_000:
                            raise ProviderError("Chat answer exceeds the size limit")
                        if token:
                            on_token(token)
                        if native and value.get("done"):
                            if value.get("done_reason") == "length":
                                raise ProviderError("Answer reached the model output limit; the streamed text is incomplete")
                            completed = True
                            break
        except HTTPError as exc:
            raise ProviderError(f"Chat provider returned HTTP {exc.code}") from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise ProviderError(f"Chat stream connection failed: {type(exc).__name__}") from exc
        except (ValueError, KeyError, TypeError, IndexError) as exc:
            raise ProviderError("Chat provider returned an invalid stream") from exc
        if not completed:
            raise ProviderError("Chat stream ended before completion")
        if not answer.strip():
            raise ProviderError("Chat provider returned no answer text")
        self._metrics = {"call_count": 1, "elapsed_ms": round((time.monotonic()-started)*1000)}
        return answer

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


def build_chat_provider(config: ProviderConfig):
    if config.kind == "openai":
        from .openai_responses import OpenAIResponsesChat
        return OpenAIResponsesChat(config)
    return OpenAICompatibleChat(config)

def build_embedding_provider(config: ProviderConfig):
    return OpenAICompatibleEmbedding(config)
