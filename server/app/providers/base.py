from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any, Literal, Protocol

from ..errors import AppError
from ..schemas import ModelInfo


def validate_reasoning(model: ModelInfo, level: object) -> None:
    if level is None or level == "off" and not model.reasoning:
        return
    if not model.reasoning or level not in model.reasoning.options:
        raise AppError(
            "reasoning_unsupported",
            "This model does not offer that thinking level. "
            "Choose a supported level or Model default.",
            422,
        )


@dataclass
class ProviderMessage:
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    images: list[bytes] = field(default_factory=list)
    tool_calls: list[dict[str, Any]] | None = None  # Reserved for a later agent spec.


@dataclass
class ChatRequest:
    model_id: str
    messages: list[ProviderMessage]
    params: dict[str, Any] = field(default_factory=dict)
    context_length: int | None = None
    reasoning: str | None = None
    json_schema: dict[str, Any] | None = None


@dataclass
class TextDelta:
    text: str


@dataclass
class ReasoningDelta:
    text: str


@dataclass
class Usage:
    prompt_tokens: int
    completion_tokens: int


@dataclass
class Timing:
    load_ms: float
    prompt_ms: float
    gen_ms: float


@dataclass
class Finish:
    reason: Literal["stop", "length", "error"]
    detail: str | None = None


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: str  # Reserved; never emitted by current chat.


ProviderEvent = TextDelta | ReasoningDelta | Usage | Timing | Finish | ToolCall


class Adapter(Protocol):
    async def list_models(self) -> list[ModelInfo]: ...
    async def load(self, model_id: str, context_length: int | None) -> None: ...
    async def unload(self, model_id: str) -> None: ...
    def stream(self, req: ChatRequest) -> AsyncIterator[ProviderEvent]: ...
    async def complete_json(self, req: ChatRequest) -> dict[str, Any]: ...
    async def embed(self, model_id: str, texts: list[str]) -> list[list[float]]: ...
