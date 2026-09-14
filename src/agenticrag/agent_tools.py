from __future__ import annotations

import ast
import math
import operator
from dataclasses import asdict, dataclass
from typing import Any, Sequence

from .domain import RankedChunk
from .errors import WorkflowError
from .retrieval import HybridRetriever
from .store import CorpusStore


@dataclass(frozen=True)
class ToolBudget:
    max_searches: int = 4
    max_lookups: int = 4
    max_calculations: int = 4
    max_evidence_chunks: int = 24
    max_query_chars: int = 500
    max_lookup_chars: int = 4_000
    max_expression_chars: int = 200

    def __post_init__(self) -> None:
        if min(asdict(self).values()) <= 0:
            raise ValueError("All tool budgets must be positive")


@dataclass(frozen=True)
class ToolResult:
    action: str
    output: dict[str, Any]
    evidence_delta: int = 0


class ReadOnlyToolGateway:
    """Host-owned allowlist for agent tools; no shell, writes, or network tools."""

    ALLOWED_ACTIONS = ("search", "lookup", "calculate")

    def __init__(
        self,
        retriever: HybridRetriever,
        store: CorpusStore,
        *,
        scopes: Sequence[str],
        collection: str,
        budget: ToolBudget | None = None,
    ) -> None:
        self.retriever = retriever
        self.store = store
        self.scopes = tuple(scopes)
        self.collection = collection
        self.budget = budget or ToolBudget()
        self.searches = 0
        self.lookups = 0
        self.calculations = 0
        self._evidence: dict[str, RankedChunk] = {}

    @property
    def evidence(self) -> tuple[RankedChunk, ...]:
        return tuple(self._evidence.values())

    def execute(self, action: str, arguments: dict[str, Any]) -> ToolResult:
        if action == "search":
            return self._search(arguments)
        if action == "lookup":
            return self._lookup(arguments)
        if action == "calculate":
            return self._calculate(arguments)
        raise WorkflowError(f"Tool action is not allowlisted: {action}")

    def _search(self, arguments: dict[str, Any]) -> ToolResult:
        self._exact_keys(arguments, {"query"})
        query = self._bounded_string(arguments["query"], "query", self.budget.max_query_chars)
        if self.searches >= self.budget.max_searches:
            raise WorkflowError("Search tool budget exhausted")
        self.searches += 1
        hits = self.retriever.retrieve(query, scopes=self.scopes, collection=self.collection)
        added = 0
        for hit in hits:
            if hit.chunk.id in self._evidence:
                continue
            if len(self._evidence) >= self.budget.max_evidence_chunks:
                break
            self._evidence[hit.chunk.id] = hit
            added += 1
        return ToolResult(
            "search",
            {
                "query": query,
                "hits": [_evidence_payload(hit) for hit in hits],
                "retained_evidence": len(self._evidence),
            },
            evidence_delta=added,
        )

    def _lookup(self, arguments: dict[str, Any]) -> ToolResult:
        self._exact_keys(arguments, {"source_version_id", "start_char", "end_char"})
        source_version_id = self._bounded_string(
            arguments["source_version_id"], "source_version_id", 128
        )
        allowed_versions = {item.chunk.source_version_id for item in self._evidence.values()}
        if source_version_id not in allowed_versions:
            raise WorkflowError("Lookup is restricted to source versions returned by search")
        start = _integer(arguments["start_char"], "start_char")
        end = _integer(arguments["end_char"], "end_char")
        if start < 0 or end <= start or end - start > self.budget.max_lookup_chars:
            raise WorkflowError("Lookup offsets are invalid or exceed the lookup budget")
        if self.lookups >= self.budget.max_lookups:
            raise WorkflowError("Lookup tool budget exhausted")
        self.lookups += 1
        source = self.store.get_source(source_version_id, scopes=self.scopes)
        if source.collection != self.collection:
            raise WorkflowError("Lookup source is outside the active collection")
        if source.text is None or end > len(source.text):
            raise WorkflowError("Lookup offsets fall outside the immutable parsed source")
        return ToolResult(
            "lookup",
            {
                "source_version_id": source_version_id,
                "logical_path": source.logical_path,
                "start_char": start,
                "end_char": end,
                "content": source.text[start:end],
            },
        )

    def _calculate(self, arguments: dict[str, Any]) -> ToolResult:
        self._exact_keys(arguments, {"expression"})
        expression = self._bounded_string(
            arguments["expression"], "expression", self.budget.max_expression_chars
        )
        if self.calculations >= self.budget.max_calculations:
            raise WorkflowError("Calculate tool budget exhausted")
        self.calculations += 1
        value = _safe_calculate(expression)
        return ToolResult("calculate", {"expression": expression, "result": value})

    @staticmethod
    def _exact_keys(arguments: dict[str, Any], expected: set[str]) -> None:
        if not isinstance(arguments, dict) or set(arguments) != expected:
            raise WorkflowError(f"Tool arguments must contain exactly: {sorted(expected)}")

    @staticmethod
    def _bounded_string(value: Any, name: str, limit: int) -> str:
        if not isinstance(value, str) or not value.strip() or len(value) > limit:
            raise WorkflowError(f"Tool argument {name} must contain 1 to {limit} characters")
        return value.strip()


def _evidence_payload(item: RankedChunk) -> dict[str, Any]:
    chunk = item.chunk
    return {
        "chunk_id": chunk.id,
        "source_version_id": chunk.source_version_id,
        "logical_path": chunk.logical_path,
        "content": chunk.text,
        "start_char": chunk.start_char,
        "end_char": chunk.end_char,
        "page_start": chunk.page_start,
        "page_end": chunk.page_end,
        "section_path": chunk.section_path,
    }


_BINARY = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _safe_calculate(expression: str) -> str:
    try:
        tree = ast.parse(expression, mode="eval")
        value = _evaluate_node(tree.body, depth=0)
    except (SyntaxError, ArithmeticError, OverflowError, ValueError, TypeError) as exc:
        raise WorkflowError("Calculation expression is invalid or unsafe") from exc
    if not math.isfinite(value) or abs(value) > 1e100:
        raise WorkflowError("Calculation result is not finite or exceeds the numeric limit")
    return format(value, ".15g")


def _evaluate_node(node: ast.AST, *, depth: int) -> float:
    if depth > 20:
        raise ValueError("expression is too deep")
    if isinstance(node, ast.Constant) and type(node.value) in {int, float}:
        value = float(node.value)
        if not math.isfinite(value) or abs(value) > 1e50:
            raise ValueError("numeric literal exceeds limit")
        return value
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY:
        return float(_UNARY[type(node.op)](_evaluate_node(node.operand, depth=depth + 1)))
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY:
        left = _evaluate_node(node.left, depth=depth + 1)
        right = _evaluate_node(node.right, depth=depth + 1)
        if isinstance(node.op, ast.Pow) and abs(right) > 12:
            raise ValueError("exponent exceeds limit")
        return float(_BINARY[type(node.op)](left, right))
    raise ValueError("unsupported expression")


def _integer(value: Any, name: str) -> int:
    if type(value) is not int:
        raise WorkflowError(f"Tool argument {name} must be an integer")
    return value
