"""Read-only tool contracts. Real retrieval adapters belong to checkpoint N2."""

import ast
import ipaddress
import math
import operator
import re
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any, Literal, cast
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..schemas import Source, WebRead
from ..search.merge import canonical


class Arguments(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    @field_validator("*", mode="after")
    @classmethod
    def nonempty(cls, value: Any) -> Any:
        if isinstance(value, str) and not value.strip():
            raise ValueError("Empty argument")
        return value


class WebSearch(Arguments):
    query: str = Field(min_length=1, max_length=200)


class LibrarySearch(WebSearch):
    pass


class ReadPage(Arguments):
    url: str = Field(min_length=1, max_length=2048)
    focus: str = Field(min_length=1, max_length=500)


class Calculate(Arguments):
    expression: str = Field(min_length=1, max_length=200)


@dataclass
class ToolOutput:
    text: str = ""
    sources: list[Source] = field(default_factory=list)
    urls: list[str] = field(default_factory=list)
    read: WebRead | None = None


Handler = Callable[[Arguments], Awaitable[ToolOutput]]
MODELS: dict[str, type[Arguments]] = {
    "web_search": WebSearch,
    "read_page": ReadPage,
    "library_search": LibrarySearch,
    "calculate": Calculate,
}
DESCRIPTIONS = {
    "web_search": "Find public pages relevant to a query.",
    "read_page": "Read an allowed page, focusing on the requested facts.",
    "library_search": "Search the user's own files.",
    "calculate": "Calculate bounded arithmetic.",
}


def public_url(url: str) -> str:
    """Syntax/literal guard only. N2's fetcher must also pin and validate DNS/redirects."""
    parsed = urlsplit(url)
    host = (parsed.hostname or "").rstrip(".").casefold()
    if (
        parsed.scheme != "https"
        or not host
        or parsed.username
        or parsed.password
        or parsed.port not in (None, 443)
        or host == "localhost"
        or host.endswith((".local", ".localhost", ".internal"))
    ):
        raise ValueError("Page is not an allowed public HTTPS URL")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        if not address.is_global:
            raise ValueError("Page is not an allowed public HTTPS URL")
    return canonical(url)


def words(text: str) -> list[str]:
    return re.findall(r"\w+", text.casefold())


class Tools:
    def __init__(
        self,
        kind: Literal["web", "library"],
        handlers: dict[str, Handler],
        *,
        user_urls: list[str] | None = None,
        private_context: list[str] | None = None,
        block_web: bool = False,
    ) -> None:
        self.kind, self.handlers, self.block_web = kind, handlers, block_web
        self.user_urls = list(user_urls or [])
        self.private_context = list(private_context or [])
        self.allowed_urls: set[str] = set()
        for url in user_urls or []:
            self.allow(url)
        self.private_sequences = {
            tuple(tokens[i : i + 8])
            for text in private_context or []
            for tokens in [words(text)]
            for i in range(len(tokens) - 7)
        }

    @property
    def names(self) -> list[str]:
        return (["web_search", "read_page"] if self.kind == "web" else ["library_search"]) + [
            "calculate"
        ]

    def for_run(self) -> "Tools":
        return Tools(
            self.kind,
            self.handlers,
            user_urls=self.user_urls,
            private_context=self.private_context,
            block_web=self.block_web,
        )

    def schemas(self) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": DESCRIPTIONS[name],
                    "parameters": MODELS[name].model_json_schema(),
                },
            }
            for name in self.names
        ]

    def allow(self, url: str) -> None:
        try:
            self.allowed_urls.add(public_url(url))
        except ValueError:
            pass  # Search results may contain links the fetcher must never visit.

    def validate(self, name: str, raw: str) -> Arguments:
        if name not in self.names or len(raw) > 10_000:
            raise ValueError("Tool is not available")
        value = MODELS[name].model_validate_json(raw)
        if name in {"web_search", "read_page"} and self.block_web:
            raise ValueError("Web tools are blocked for this recording chat")
        if isinstance(value, WebSearch) and not isinstance(value, LibrarySearch):
            tokens = words(value.query)
            if any(
                tuple(tokens[i : i + 8]) in self.private_sequences for i in range(len(tokens) - 7)
            ):
                raise ValueError("Web query contains private context")
        if isinstance(value, ReadPage) and public_url(value.url) not in self.allowed_urls:
            raise ValueError("URL is not in the run's allowlist")
        return value

    async def execute(self, name: str, value: Arguments) -> ToolOutput:
        if isinstance(value, Calculate):
            return ToolOutput(text=str(calculate(value.expression)))
        if name not in self.handlers:
            raise ValueError("Tool is not connected in this checkpoint")
        result = await self.handlers[name](value)
        if name == "web_search":
            for url in [*result.urls, *(source.url for source in result.sources)]:
                self.allow(url)
        return result


def calculate(expression: str) -> int | float:
    """Port of the reviewed H0 AST calculator at 4acc379f; no eval or names."""
    root = ast.parse(expression, mode="eval")
    if len(expression) > 200 or len(list(ast.walk(root))) > 80:
        raise ValueError("Calculator input limit")
    operations = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
    }

    def visit(node: ast.AST) -> int | float:
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            value = cast(int | float, node.value)
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = visit(node.operand) * (-1 if isinstance(node.op, ast.USub) else 1)
        elif isinstance(node, ast.BinOp) and type(node.op) in operations:
            value = operations[type(node.op)](visit(node.left), visit(node.right))
        else:
            raise ValueError("Unsupported arithmetic")
        if abs(value) > 10**15 or not math.isfinite(value):
            raise ValueError("Calculator result limit")
        return value

    return visit(root.body)
