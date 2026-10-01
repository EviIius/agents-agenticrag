from __future__ import annotations

import hashlib
from collections.abc import Sequence
from typing import Any

from _bootstrap import SRC  # noqa: F401
from agenticrag.providers.base import ChatMessage


class DeterministicEmbedding:
    label = "test:embedding"

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            digest = hashlib.sha256(text.lower().encode("utf-8")).digest()
            vectors.append(
                [
                    1.0 + text.lower().count("atlas"),
                    1.0 + text.lower().count("memory"),
                    1.0 + digest[0] / 255.0,
                ]
            )
        return vectors


class StaticChat:
    label = "test:chat"

    def __init__(self, response: str) -> None:
        self.response = response
        self.calls: list[tuple[Sequence[ChatMessage], dict[str, Any]]] = []

    def complete(
        self,
        messages: Sequence[ChatMessage],
        *,
        response_schema: dict[str, Any] | None = None,
        max_tokens: int = 2048,
        temperature: float = 0.0,
    ) -> str:
        self.calls.append(
            (
                messages,
                {
                    "response_schema": response_schema,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
            )
        )
        return self.response
