from __future__ import annotations

import json
import time
import threading
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ..config import ProviderConfig, ProviderRole
from ..domain import ExternalSource
from ..errors import ConfigurationError, ProviderError, WorkflowError
from .base import ChatMessage


Transport = Callable[[Request, float], bytes]


def _default_transport(request: Request, timeout: float) -> bytes:
    with urlopen(request, timeout=timeout) as response:  # noqa: S310 - config validates host
        return response.read(8 * 1024 * 1024 + 1)


@dataclass(frozen=True)
class WebSearchResult:
    answer: str
    sources: tuple[ExternalSource, ...]
    elapsed_ms: int


class OpenAIResponsesChat:
    """Stateless OpenAI Responses API chat adapter with structured-output support."""

    def __init__(self, config: ProviderConfig, *, transport: Transport | None = None) -> None:
        if config.kind != "openai" or config.role is not ProviderRole.CHAT:
            raise ConfigurationError("Responses chat requires the OpenAI chat provider")
        if not config.api_key:
            raise ConfigurationError("Responses chat requires an OpenAI API key")
        self.config = config
        self._transport = transport or _default_transport
        self._inference_slot = threading.Lock()

    @property
    def label(self) -> str:
        return self.config.label

    def complete(
        self,
        messages: Sequence[ChatMessage],
        *,
        response_schema: dict[str, Any] | None = None,
        max_tokens: int = 2_048,
        temperature: float = 0.0,
    ) -> str:
        del temperature  # Current reasoning models may not accept sampling controls.
        input_items = [
            {
                "role": "developer" if message.role == "system" else message.role,
                "content": message.content,
            }
            for message in messages
        ]
        payload: dict[str, Any] = {
            "model": self.config.model,
            "input": input_items,
            "max_output_tokens": max_tokens,
            "store": False,
        }
        if response_schema is not None:
            if self.config.structured_output_mode == "json_schema":
                payload["text"] = {
                    "format": {
                        "type": "json_schema",
                        "name": "agenticrag_response",
                        "strict": True,
                        "schema": response_schema,
                    }
                }
            else:
                schema_text = json.dumps(response_schema, separators=(",", ":"))
                input_items.insert(
                    0,
                    {
                        "role": "developer",
                        "content": (
                            "Return one JSON object only, without markdown fences. It must satisfy "
                            "this JSON Schema: " + schema_text
                        ),
                    },
                )
                if self.config.structured_output_mode == "json_object":
                    payload["text"] = {"format": {"type": "json_object"}}
        with self._inference_slot:
            response = _post(self.config, payload, self._transport)
        answer, _ = _response_content(response)
        if not answer:
            raise ProviderError("OpenAI Responses API returned no output text")
        return answer


class OpenAIResponsesWebSearch:
    """Explicit, stateless OpenAI Responses API web-search capability."""

    def __init__(
        self,
        config: ProviderConfig,
        *,
        transport: Transport | None = None,
        max_tool_calls: int = 2,
    ) -> None:
        if config.kind != "openai" or config.role is not ProviderRole.CHAT:
            raise ConfigurationError("Hosted web search requires the OpenAI chat provider")
        if not config.api_key:
            raise ConfigurationError("Hosted web search requires an OpenAI API key")
        if not 1 <= max_tool_calls <= 3:
            raise ValueError("max_tool_calls must be from 1 to 3")
        self.config = config
        self._transport = transport or _default_transport
        self.max_tool_calls = max_tool_calls

    def search(self, query: str) -> WebSearchResult:
        query = query.strip()
        if not query or len(query) > 12_000:
            raise WorkflowError("Web search query must contain 1 to 12000 characters")
        started = time.perf_counter()
        payload: dict[str, Any] = {
            "model": self.config.model,
            "input": query,
            "instructions": (
                "Research the request using web search. Prefer primary sources, distinguish facts "
                "from inference, and keep citations attached to the claims they support."
            ),
            "tools": [{"type": "web_search"}],
            "tool_choice": "required",
            "include": ["web_search_call.action.sources"],
            "max_tool_calls": self.max_tool_calls,
            "parallel_tool_calls": False,
            "max_output_tokens": 2_048,
            "store": False,
        }
        response = _post(self.config, payload, self._transport)
        answer, source_rows = _response_content(response)
        if not answer:
            raise ProviderError("OpenAI Responses API returned no output text")
        sources = tuple(
            ExternalSource(id=f"web_{index}", title=title or url, url=url)
            for index, (url, title) in enumerate(source_rows, start=1)
        )
        return WebSearchResult(
            answer=answer,
            sources=sources,
            elapsed_ms=max(0, round((time.perf_counter() - started) * 1_000)),
        )


def _post(
    config: ProviderConfig, payload: dict[str, Any], transport: Transport
) -> dict[str, Any]:
    request = Request(
        f"{config.base_url}/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "agenticrag/0.4",
        },
        method="POST",
    )
    try:
        raw = transport(request, config.timeout_seconds)
    except HTTPError as exc:
        raise ProviderError(f"OpenAI Responses API returned HTTP {exc.code}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise ProviderError(f"OpenAI Responses API request failed: {exc}") from exc
    if len(raw) > 8 * 1024 * 1024:
        raise ProviderError("OpenAI Responses API response exceeded 8 MiB")
    try:
        response = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProviderError("OpenAI Responses API returned invalid JSON") from exc
    if not isinstance(response, dict) or response.get("error"):
        raise ProviderError("OpenAI Responses API reported an error")
    return response


def _response_content(response: dict[str, Any]) -> tuple[str, list[tuple[str, str]]]:
    texts: list[str] = []
    sources: dict[str, str] = {}
    output = response.get("output")
    if not isinstance(output, list):
        return "", []
    for item in output:
        if not isinstance(item, dict):
            continue
        action = item.get("action")
        if isinstance(action, dict):
            action_sources = action.get("sources")
            if isinstance(action_sources, list):
                for source in action_sources:
                    if isinstance(source, dict) and isinstance(source.get("url"), str):
                        sources.setdefault(source["url"], str(source.get("title") or ""))
        content = item.get("content")
        if not isinstance(content, list):
            continue
        for part in content:
            if not isinstance(part, dict) or part.get("type") != "output_text":
                continue
            if isinstance(part.get("text"), str):
                texts.append(part["text"].strip())
            annotations = part.get("annotations")
            if isinstance(annotations, list):
                for annotation in annotations:
                    if not isinstance(annotation, dict):
                        continue
                    url = annotation.get("url")
                    if isinstance(url, str):
                        sources[url] = str(annotation.get("title") or sources.get(url, ""))
    return "\n\n".join(text for text in texts if text), list(sources.items())
