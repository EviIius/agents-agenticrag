"""Isolated H0 admission and fixture tools; never imported by the application."""

from __future__ import annotations

import ast
import contextlib
import fcntl
import hashlib
import json
import math
import operator
import os
import signal
import subprocess
import time
from pathlib import Path
from typing import Any

MAX_CALLS = 42
MAX_TASK_CALLS = 3
MAX_SECONDS = 180
MAX_SOURCE_CHARS = 12_000
TOOL_NAMES = frozenset({"web_search", "read_page", "library_search", "calculator"})
SAMPLING = frozenset(
    {
        "temperature",
        "top_p",
        "top_k",
        "seed",
        "max_tokens",
        "max_completion_tokens",
        "num_predict",
        "frequency_penalty",
        "presence_penalty",
        "repetition_penalty",
        "stop",
    }
)


class GateFailure(ValueError):
    """A refused request never reaches a model or tool."""


class Ledger:
    """Durable counters/stop state shared by workers and the controller."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)

    @contextlib.contextmanager
    def locked(self):
        with self.path.with_suffix(".lock").open("a+") as lock:
            os.chmod(lock.name, 0o600)
            fcntl.flock(lock, fcntl.LOCK_EX)
            state = (
                json.loads(self.path.read_text())
                if self.path.exists()
                else {"calls": 0, "tasks": {}, "stopped": None, "events": []}
            )
            try:
                yield state
            finally:
                temporary = self.path.with_suffix(".pending")
                temporary.write_text(json.dumps(state, indent=2) + "\n")
                temporary.chmod(0o600)
                os.replace(temporary, self.path)

    def stop(self, reason: str) -> None:
        with self.locked() as state:
            state["stopped"] = state["stopped"] or reason

    def admit(self, task: str, *, baseline: bool = False) -> int:
        with self.locked() as state:
            limit = 1 if baseline else MAX_TASK_CALLS
            if state["stopped"]:
                raise GateFailure("Trial is stopped")
            if state["calls"] >= MAX_CALLS or state["tasks"].get(task, 0) >= limit:
                state["stopped"] = "Native-call budget exhausted"
                raise GateFailure(state["stopped"])
            state["calls"] += 1
            state["tasks"][task] = state["tasks"].get(task, 0) + 1
            state["events"].append({"task": task, "call": state["calls"]})
            return state["calls"]


def validate_request(
    body: dict[str, Any], model: str, explicit: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Validate the actual wire body; do not silently repair SDK defaults."""
    explicit = explicit or {}
    if body.get("model") != model:
        raise GateFailure("Unexpected model or hidden fallback")
    if not isinstance(body.get("messages"), list) or not body["messages"]:
        raise GateFailure("Missing messages")
    allowed = {
        "model",
        "messages",
        "stream",
        "stream_options",
        "tools",
        "tool_choice",
        "parallel_tool_calls",
    } | SAMPLING
    if set(body) - allowed:
        raise GateFailure("Unexpected request fields")
    for name in SAMPLING:
        if name in body and (name not in explicit or body[name] != explicit[name]):
            raise GateFailure("Sampling was not explicitly selected")
    for name, value in explicit.items():
        if name not in SAMPLING or body.get(name) != value:
            raise GateFailure("Explicit sampling changed or disappeared")
    tools = body.get("tools", [])
    if not isinstance(tools, list) or len(tools) > len(TOOL_NAMES):
        raise GateFailure("Invalid tool collection")
    names = []
    for tool in tools:
        function = tool.get("function") if isinstance(tool, dict) else None
        if (
            not isinstance(function, dict)
            or tool.get("type") != "function"
            or function.get("name") not in TOOL_NAMES
        ):
            raise GateFailure("Unexpected tool schema")
        names.append(function["name"])
    if len(names) != len(set(names)):
        raise GateFailure("Duplicate tool schemas")
    choice = body.get("tool_choice", "auto")
    if isinstance(choice, dict):
        if choice.get("type") != "function" or choice.get("function", {}).get("name") not in names:
            raise GateFailure("Unexpected forced tool")
    elif choice not in ("auto", "none", "required"):
        raise GateFailure("Invalid tool choice")
    return body


class TaskGate:
    def __init__(self, ledger: Ledger, task: str, *, clock=time.monotonic) -> None:
        self.ledger = ledger
        self.task = task
        self.clock = clock
        self.deadline = clock() + MAX_SECONDS
        self.cancelled = False

    def check(self) -> None:
        if self.cancelled or self.clock() >= self.deadline:
            self.ledger.stop("Task cancelled or timed out")
            raise GateFailure("Task cancelled or timed out")

    def admit(self, body, model, *, baseline=False, explicit=None) -> int:
        self.check()
        try:
            validate_request(body, model, explicit)
        except GateFailure:
            self.ledger.stop("Request protocol rejected")
            raise
        return self.ledger.admit(self.task, baseline=baseline)


def calculate(expression: str) -> int | float:
    """Small arithmetic tool: no eval, calls, powers, names or unbounded integers."""
    if not isinstance(expression, str) or len(expression) > 200:
        raise GateFailure("Calculator input limit")
    try:
        root = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise GateFailure("Invalid arithmetic") from exc
    if len(list(ast.walk(root))) > 80:
        raise GateFailure("Calculator expression limit")
    operations = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
    }

    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            value = node.value
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = visit(node.operand) * (-1 if isinstance(node.op, ast.USub) else 1)
        elif isinstance(node, ast.BinOp) and type(node.op) in operations:
            try:
                value = operations[type(node.op)](visit(node.left), visit(node.right))
            except (ArithmeticError, OverflowError) as exc:
                raise GateFailure("Invalid arithmetic result") from exc
        else:
            raise GateFailure("Unsupported arithmetic")
        if abs(value) > 10**15 or not math.isfinite(value):
            raise GateFailure("Calculator result limit")
        return value

    return visit(root.body)


class FixtureTools:
    """Clearly synthetic sources. Never access the user's real Library or web."""

    def __init__(self, sources: list[dict[str, Any]]) -> None:
        self.sources = sources
        self.by_id = {row["id"]: row for row in sources}
        self.emitted_chars = 0

    def call(self, name: str, args: dict[str, Any]) -> dict[str, Any]:
        if name not in TOOL_NAMES or not isinstance(args, dict):
            raise GateFailure("Unauthorized tool")
        if name == "calculator":
            if set(args) != {"expression"}:
                raise GateFailure("Unexpected calculator arguments")
            return {"expression": args["expression"], "result": calculate(args["expression"])}
        if name == "read_page":
            if set(args) != {"source_id"} or args["source_id"] not in self.by_id:
                raise GateFailure("Unknown source reference")
            result = dict(self.by_id[args["source_id"]])
        else:
            if (
                set(args) != {"query"}
                or not isinstance(args["query"], str)
                or len(args["query"]) > 500
            ):
                raise GateFailure("Invalid search arguments")
            kind = "library" if name == "library_search" else "web"
            # Fixed corpus, equally available to each arm; no answer-key routing.
            result = {
                "synthetic": True,
                "sources": [row for row in self.sources if row["kind"] == kind],
            }
        self.emitted_chars += len(json.dumps(result))
        if self.emitted_chars > MAX_SOURCE_CHARS:
            raise GateFailure("Source budget exhausted")
        return result


def terminate(process: subprocess.Popen, timeout: float = 3) -> None:
    """Own only a session/process group created by the H0 runner."""
    if process.poll() is not None:
        process.wait()
        return
    if os.getpgid(process.pid) != process.pid:
        raise GateFailure("Child process group ownership mismatch")
    os.killpg(process.pid, signal.SIGTERM)
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=timeout)


def freeze(paths: list[Path]) -> dict[str, str]:
    return {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
