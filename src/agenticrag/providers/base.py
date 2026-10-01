from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Protocol, Sequence, Callable

@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str
    image_data_url: str | None = None

class ChatProvider(Protocol):
    @property
    def label(self) -> str: ...
    def complete(self, messages: Sequence[ChatMessage], *, response_schema: dict[str, Any] | None = None,
                 max_tokens: int = 2048, temperature: float = 0.0) -> str: ...
    def stream_complete(self, messages: Sequence[ChatMessage], on_token: Callable[[str], None], *,
                        max_tokens: int = 2048, temperature: float = 0.0) -> str: ...

class EmbeddingProvider(Protocol):
    @property
    def label(self) -> str: ...
    def embed(self, texts: Sequence[str]) -> list[list[float]]: ...
