from __future__ import annotations

import base64
import json
import mimetypes
import os
import re
import tempfile
import threading
import time
import webbrowser
from datetime import datetime, timezone
from contextlib import contextmanager
from dataclasses import asdict, replace
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import resources
from pathlib import Path
from typing import Any, Callable, Iterator, Sequence
from urllib.parse import parse_qs, unquote, urlsplit

from . import __version__
from .agent import AgentConfig, BoundedAgenticRAGWorkflow
from .agent_tools import ReadOnlyToolGateway, ToolBudget
from .config import (
    ProviderRole,
    StoreConfig,
    load_ingestion_config,
    load_provider_config,
    load_store_config,
)
from .conversations import ConversationStore
from .errors import AgenticRAGError, AuthorizationError, ConfigurationError, WorkflowError
from .ingestion import FileParser, IngestionLimits, Ingestor, parser_capabilities
from .postgres_store import PostgresCorpusStore
from .providers.openai_compatible import build_chat_provider, build_embedding_provider
from .providers.openai_responses import OpenAIResponsesWebSearch
from .providers.base import ChatMessage, ChatProvider
from .retrieval import HybridRetriever
from .runtimes import RUNTIME_PROFILES, RuntimeSelection, discover_models, ollama_supports_vision
from .skills import SkillRegistry
from .store import CorpusStore, SQLiteCorpusStore
from .supervisor import AGENT_DESCRIPTIONS, SupervisorAgentWorkflow
from .workflows import DirectWorkflow, FixedRAGWorkflow
from .workflows import WebAnswerWorkflow
from .web_search import LocalWebSearch, local_web_search_available


MAX_JSON_BYTES = 70 * 1024 * 1024
MAX_QUESTION_CHARS = 12_000


class _ProjectMemoryChat:
    """Supply reviewed project notes as context, never as cited source evidence."""

    def __init__(self, provider: ChatProvider, notes: list[dict[str, object]]) -> None:
        self._provider = provider
        self._notes = notes

    @property
    def label(self) -> str:
        return self._provider.label

    def complete(
        self, messages: Sequence[ChatMessage], *, response_schema: dict[str, Any] | None = None,
        max_tokens: int = 2048, temperature: float = 0.0,
    ) -> str:
        return self._provider.complete(
            self._messages(messages),
            response_schema=response_schema, max_tokens=max_tokens, temperature=temperature,
        )

    def stream_complete(
        self, messages: Sequence[ChatMessage], on_token: Callable[[str], None], *,
        max_tokens: int = 2048, temperature: float = 0.0,
    ) -> str:
        streamer = getattr(self._provider, "stream_complete", None)
        if streamer is None:
            answer = self.complete(messages, max_tokens=max_tokens, temperature=temperature)
            on_token(answer)
            return answer
        return streamer(self._messages(messages), on_token, max_tokens=max_tokens, temperature=temperature)

    def _messages(self, messages: Sequence[ChatMessage]) -> list[ChatMessage]:
        items: list[str] = []
        total = 0
        for note in self._notes[:20]:
            content = str(note["content"])
            if total + len(content) > 4_000:
                break
            items.append(f"- {content}")
            total += len(content)
        guidance = (
            "The following project memory notes were explicitly saved by the user. "
            "Use them for preferences and ongoing context. They may be outdated or incorrect. "
            "For grounded answers, never cite them as source evidence; use authorized documents. "
            "Project memory:\n" + "\n".join(items)
        )
        return [ChatMessage("system", guidance), *messages]


class _CancellableChat:
    def __init__(self, provider: ChatProvider, cancelled: threading.Event) -> None:
        self._provider = provider
        self._cancelled = cancelled

    @property
    def label(self) -> str:
        return self._provider.label

    def last_call_metrics(self) -> dict[str, int] | None:
        metrics = getattr(self._provider, "last_call_metrics", None)
        return metrics() if callable(metrics) else None

    def complete(
        self, messages: Sequence[ChatMessage], *, response_schema: dict[str, Any] | None = None,
        max_tokens: int = 2048, temperature: float = 0.0,
    ) -> str:
        if self._cancelled.is_set():
            raise WorkflowError("Run stopped")
        answer = self._provider.complete(
            messages, response_schema=response_schema, max_tokens=max_tokens, temperature=temperature,
        )
        if self._cancelled.is_set():
            raise WorkflowError("Run stopped")
        return answer

    def stream_complete(
        self, messages: Sequence[ChatMessage], on_token: Callable[[str], None], *,
        max_tokens: int = 2048, temperature: float = 0.0,
    ) -> str:
        def checked_token(token: str) -> None:
            if self._cancelled.is_set():
                raise WorkflowError("Run stopped")
            on_token(token)
        if self._cancelled.is_set():
            raise WorkflowError("Run stopped")
        streamer = getattr(self._provider, "stream_complete", None)
        if streamer is None:
            answer = self.complete(messages, max_tokens=max_tokens, temperature=temperature)
            checked_token(answer)
        else:
            answer = streamer(messages, checked_token, max_tokens=max_tokens, temperature=temperature)
        if self._cancelled.is_set():
            raise WorkflowError("Run stopped")
        return answer


UI_FILES = {
    "/": "index.html", "/index.html": "index.html", "/app.js": "app.js",
    "/styles.css": "styles.css", "/tokens.css": "tokens.css", "/design-v2.css": "design-v2.css",
    "/vendor/marked.umd.js": "vendor/marked.umd.js",
    "/vendor/purify.min.js": "vendor/purify.min.js",
    "/manifest.webmanifest": "manifest.webmanifest", "/icon-180.png": "icon-180.png",
    "/icon-192.png": "icon-192.png", "/icon-512.png": "icon-512.png",
    **{f"/fonts/{name}": f"fonts/{name}" for name in (
        "Geist-Variable.woff2", "Geist-Variable-LatinExt.woff2",
        "GeistMono-Variable.woff2", "GeistMono-Variable-LatinExt.woff2",
        "Newsreader-Variable.woff2", "Newsreader-Variable-LatinExt.woff2",
        "Newsreader-Variable-Italic.woff2",
    )},
}
MODEL_CONTRACT_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "answer": {"type": "integer"},
        "action": {"type": "string", "enum": ["calculate"]},
        "assumptions": {"type": "array", "items": {"type": "string"}, "maxItems": 3},
    },
    "required": ["answer", "action", "assumptions"],
    "additionalProperties": False,
}


class WorkbenchState:
    def __init__(self, db_path: str, skills_root: Path) -> None:
        self.db_path = db_path
        self._selection_path = (
            None if db_path == ":memory:" else Path(db_path).resolve().with_name("workbench-providers.json")
        )
        self._evaluation_path = (
            None if db_path == ":memory:" else Path(db_path).resolve().with_name("workbench-evaluation.json")
        )
        self.conversations = ConversationStore(
            ":memory:" if db_path == ":memory:" else str(Path(db_path).resolve().with_name("workbench-chats.db"))
        )
        self.skills_root = skills_root.expanduser().resolve()
        default_skills_root = Path(".agenticrag/skills").resolve()
        self.agent_skills_root = (
            Path(".agents/skills").resolve()
            if self.skills_root == default_skills_root
            else None
        )
        self._lock = threading.RLock()
        self._active_runs: dict[str, threading.Event] = {}
        self._runtime_status_cache: tuple[float, dict[str, object]] | None = None
        self._providers: dict[ProviderRole, RuntimeSelection] = {}
        for role in ProviderRole:
            try:
                configured = load_provider_config(role)
            except ConfigurationError:
                continue
            ollama_url = next(
                item[f"{role.value}_base_url"]
                for item in RUNTIME_PROFILES if item["id"] == "ollama"
            )
            self._providers[role] = RuntimeSelection(
                runtime=(
                    "openai" if configured.kind == "openai"
                    else "ollama" if configured.base_url == ollama_url
                    else "openai-compatible"
                ),
                role=role,
                base_url=configured.base_url,
                model=configured.model,
                structured_output_mode=configured.structured_output_mode,
                api_key=configured.api_key,
                timeout_seconds=configured.timeout_seconds,
                provider_kind=configured.kind,  # type: ignore[arg-type]
            )
        self._load_local_selections()

    def start_run(self, run_id: str) -> threading.Event:
        with self._lock:
            if run_id in self._active_runs or len(self._active_runs) >= 8:
                raise ValueError("Too many active runs or duplicate run identifier")
            event = threading.Event()
            self._active_runs[run_id] = event
            return event

    def cancel_run(self, run_id: str) -> bool:
        with self._lock:
            event = self._active_runs.get(run_id)
            if event is None:
                return False
            event.set()
            return True

    def finish_run(self, run_id: str) -> None:
        with self._lock:
            self._active_runs.pop(run_id, None)

    def _load_local_selections(self) -> None:
        if self._selection_path is None or not self._selection_path.exists():
            return
        try:
            payload = json.loads(self._selection_path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict) or payload.get("version") != 1:
                return
            selections = payload.get("providers", {})
            if not isinstance(selections, dict):
                return
            for role in ProviderRole:
                item = selections.get(role.value)
                if not isinstance(item, dict):
                    continue
                self._providers[role] = RuntimeSelection(
                    runtime=item["runtime"],
                    role=role,
                    base_url=item["base_url"],
                    model=item["model"],
                    structured_output_mode=item["structured_output_mode"],
                    timeout_seconds=item["timeout_seconds"],
                    provider_kind="local",
                )
        except (OSError, ValueError, KeyError, TypeError, ConfigurationError):
            # An invalid local preference cannot grant access or block environment defaults.
            return

    def _save_local_selections(self) -> None:
        if self._selection_path is None:
            return
        payload = {
            "version": 1,
            "providers": {
                role.value: {
                    "runtime": selection.runtime,
                    "base_url": selection.base_url,
                    "model": selection.model,
                    "structured_output_mode": selection.structured_output_mode,
                    "timeout_seconds": selection.timeout_seconds,
                }
                for role, selection in self._providers.items()
                if selection.provider_kind == "local" and not selection.api_key
            },
        }
        self._selection_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=self._selection_path.parent, delete=False
            ) as temporary:
                temporary_path = Path(temporary.name)
                os.chmod(temporary_path, 0o600)
                json.dump(payload, temporary, separators=(",", ":"))
            os.replace(temporary_path, self._selection_path)
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

    def skill_registry(self) -> SkillRegistry:
        additional = () if self.agent_skills_root is None else (self.agent_skills_root,)
        return SkillRegistry(self.skills_root, additional_roots=additional)

    def provider(self, role: ProviderRole) -> RuntimeSelection:
        with self._lock:
            try:
                return self._providers[role]
            except KeyError as exc:
                raise ConfigurationError(
                    f"Configure the {role.value} runtime in Models before using this action"
                ) from exc

    def evaluation_report(self) -> dict[str, object]:
        path = self._evaluation_path
        if path is None or not path.exists():
            return {"available": False}
        if path.stat().st_size > 2_000_000:
            raise ValueError("Evaluation report is too large")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or payload.get("schema_version") != 1:
            raise ValueError("Evaluation report has an unsupported format")
        return {"available": True, **payload}

    def runtime_status(self) -> dict[str, object]:
        now = time.monotonic()
        with self._lock:
            cached = self._runtime_status_cache
            if cached and now - cached[0] < 15:
                return cached[1]
            providers = dict(self._providers)
        result: dict[str, object] = {"checked_at": datetime.now(timezone.utc).isoformat()}
        for role in ProviderRole:
            selection = providers.get(role)
            if selection is None:
                result[role.value] = {"configured": False, "reachable": False, "latency_ms": None, "model_present": None, "error": None}
                continue
            try:
                probe = discover_models(replace(selection.provider_config(), timeout_seconds=2.0))
                result[role.value] = {
                    "configured": True, "reachable": True, "latency_ms": probe["latency_ms"],
                    "model_present": probe["configured_model_available"], "error": None,
                }
            except (AgenticRAGError, OSError, ValueError) as exc:
                result[role.value] = {"configured": True, "reachable": False, "latency_ms": None, "model_present": None, "error": str(exc)[:240]}
        with self._lock:
            self._runtime_status_cache = (time.monotonic(), result)
        return result

    def configure(self, payload: dict[str, Any]) -> dict[str, object]:
        role = _role(payload.get("role"))
        timeout = payload.get("timeout_seconds", 90)
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
            raise ConfigurationError("timeout_seconds must be numeric")
        selection = RuntimeSelection(
            runtime=_bounded_string(payload.get("runtime"), "runtime", 64),
            role=role,
            base_url=_bounded_string(payload.get("base_url"), "base_url", 2_048),
            model=_bounded_string(payload.get("model"), "model", 512),
            structured_output_mode=_structured_mode(payload.get("structured_output_mode")),
            api_key=_optional_secret(payload.get("api_key")),
            timeout_seconds=float(timeout),
            provider_kind=_provider_kind(payload.get("provider_kind")),
        )
        with self._lock:
            previous = self._providers.get(role)
            self._providers[role] = selection
            self._runtime_status_cache = None
            try:
                self._save_local_selections()
            except OSError:
                if previous is None:
                    del self._providers[role]
                else:
                    self._providers[role] = previous
                raise
        return selection.public_dict()

    def public_providers(self) -> dict[str, object]:
        with self._lock:
            return {
                role.value: (
                    self._providers[role].public_dict()
                    if role in self._providers
                    else {"role": role.value, "configured": False}
                )
                for role in ProviderRole
            }

    @contextmanager
    def store(self) -> Iterator[CorpusStore]:
        config = load_store_config(self.db_path)
        store: SQLiteCorpusStore | PostgresCorpusStore
        if config.backend == "sqlite":
            store = SQLiteCorpusStore(config.sqlite_path)
        else:
            assert config.postgres_dsn is not None
            store = PostgresCorpusStore.connect(config.postgres_dsn, config.objects_root)
        try:
            store.initialize()
            yield store
        finally:
            store.close()

    def bootstrap(self) -> dict[str, object]:
        skills = self.skill_registry().metadata()
        ingestion = load_ingestion_config()
        store_config = load_store_config(self.db_path)
        return {
            "version": __version__,
            "local_web_search_available": local_web_search_available(),
            "providers": self.public_providers(),
            "runtimes": RUNTIME_PROFILES,
            "store": store_config.public_dict(),
            "capabilities": {
                "tools": [
                    {
                        "id": "search",
                        "name": "Corpus search",
                        "description": "Hybrid lexical and vector retrieval inside the active collection and scopes.",
                        "access": "read-only",
                        "enabled": True,
                    },
                    {
                        "id": "lookup",
                        "name": "Source lookup",
                        "description": "Bounded text lookup, restricted to source versions already returned by search.",
                        "access": "read-only",
                        "enabled": True,
                    },
                    {
                        "id": "calculate",
                        "name": "Safe calculator",
                        "description": "Arithmetic expressions only; no functions, names, filesystem, shell, or network.",
                        "access": "sandboxed",
                        "enabled": True,
                    },
                    {
                        "id": "web_search",
                        "name": "Web search",
                        "description": (
                            "Opt-in public web search. Local models use a metasearch service; hosted OpenAI "
                            "uses Responses web search. Search queries leave this Mac."
                        ),
                        "access": "external · per-run consent",
                        "enabled": self._web_search_available(),
                    },
                ],
                "skills": [{**item, "enabled": True} for item in skills],
                "agents": [
                    {
                        "id": "supervisor",
                        "name": "Supervisor coordinator",
                        "description": "Plans up to three bounded assignments, calls specialists, synthesizes, and runs a final critic.",
                        "access": "can delegate · no recursion",
                        "enabled": True,
                    },
                    *[
                        {
                            "id": identifier,
                            "name": identifier.replace("_", " ").title(),
                            "description": description,
                            "access": (
                                "external · opt-in"
                                if identifier == "web_researcher"
                                else "bounded specialist"
                            ),
                            "enabled": (
                                self._web_search_available()
                                if identifier == "web_researcher"
                                else True
                            ),
                        }
                        for identifier, description in AGENT_DESCRIPTIONS.items()
                    ],
                    {
                        "id": "evidence_critic",
                        "name": "Evidence critic",
                        "description": "Independently rejects unsupported or incomplete specialist and final answers.",
                        "access": "internal review",
                        "enabled": True,
                    },
                ],
                "plugins": [],
                "plugin_status": "Plugin adapters are not installed; the capability boundary is reserved.",
                "agent": {
                    "planning": "obligation decomposition",
                    "review": "independent cited-evidence critic pass",
                    "tool_allowlist": list(ReadOnlyToolGateway.ALLOWED_ACTIONS),
                    "default_limits": asdict(AgentConfig()),
                    "tool_budget": asdict(ToolBudget()),
                },
            },
            "ingestion": {
                "limits": {
                    "max_file_bytes": ingestion.max_file_bytes,
                    "max_pages": ingestion.max_pages,
                    "max_segments": ingestion.max_segments,
                },
                "formats": parser_capabilities(ingestion.docling_artifacts_path),
            },
            "workflows": [
                {"id": "fixed", "name": "Fixed RAG", "description": "One retrieval and evidence-grounded answer."},
                {"id": "agent", "name": "Agentic RAG", "description": "Plan, use bounded tools and skills, then run a critic review."},
                {"id": "supervisor", "name": "Supervisor", "description": "A manager calls bounded specialist agents, synthesizes their findings, and runs a final critic."},
                {"id": "direct", "name": "Direct model", "description": "No retrieval; useful as an experimental baseline."},
            ],
        }

    def _web_search_available(self) -> bool:
        with self._lock:
            selection = self._providers.get(ProviderRole.CHAT)
            return bool(selection and (
                (selection.provider_kind == "openai" and selection.api_key)
                or (selection.provider_kind == "local" and local_web_search_available())
            ))


def make_handler(state: WorkbenchState) -> type[BaseHTTPRequestHandler]:
    class WorkbenchHandler(BaseHTTPRequestHandler):
        server_version = "AgenticRAGWorkbench/0.3"

        def do_GET(self) -> None:  # noqa: N802
            try:
                parsed = urlsplit(self.path)
                if parsed.path == "/healthz":
                    self._json(HTTPStatus.OK, {"status": "ok", "version": __version__})
                    return
                if parsed.path in UI_FILES:
                    self._asset(UI_FILES[parsed.path])
                    return
                if parsed.path == "/api/v1/bootstrap":
                    self._json(HTTPStatus.OK, state.bootstrap())
                    return
                if parsed.path == "/api/v1/runtime-status":
                    self._json(HTTPStatus.OK, state.runtime_status())
                    return
                if parsed.path == "/api/v1/evaluation":
                    self._json(HTTPStatus.OK, state.evaluation_report())
                    return
                if parsed.path == "/api/v1/projects":
                    self._json(HTTPStatus.OK, {"projects": state.conversations.list_projects()})
                    return
                project_notes = re.fullmatch(r"/api/v1/projects/(default|[0-9a-f]{32})/notes", parsed.path)
                if project_notes:
                    self._json(HTTPStatus.OK, {"notes": state.conversations.list_project_notes(project_notes[1])})
                    return
                project_activity = re.fullmatch(r"/api/v1/projects/(default|[0-9a-f]{32})/memory-activity", parsed.path)
                if project_activity:
                    self._json(HTTPStatus.OK, {"activity": state.conversations.list_project_note_activity(project_activity[1])})
                    return
                if parsed.path == "/api/v1/chats":
                    query = parse_qs(parsed.query)
                    self._json(HTTPStatus.OK, {"chats": state.conversations.list(
                        collection=_optional_query(query, "collection"),
                        query=_optional_query(query, "q"),
                    )})
                    return
                if parsed.path.startswith("/api/v1/chats/"):
                    chat_id = parsed.path.removeprefix("/api/v1/chats/")
                    if not re.fullmatch(r"[0-9a-f]{32}", chat_id):
                        raise ValueError("Invalid conversation identifier")
                    self._json(HTTPStatus.OK, state.conversations.get(chat_id))
                    return
                if parsed.path == "/api/v1/sources":
                    query = parse_qs(parsed.query)
                    scopes = _scopes_from_query(query)
                    collection = _optional_query(query, "collection")
                    with state.store() as store:
                        sources = store.list_sources(scopes=scopes, collection=collection)
                    self._json(
                        HTTPStatus.OK,
                        {
                            "sources": [asdict(source) for source in sources],
                            "collections": sorted({source.collection for source in sources}),
                        },
                    )
                    return
                if parsed.path.startswith("/api/v1/sources/"):
                    source_id = unquote(parsed.path.removeprefix("/api/v1/sources/"))
                    if not source_id or "/" in source_id:
                        raise ValueError("Invalid source identifier")
                    query = parse_qs(parsed.query)
                    with state.store() as store:
                        source = store.get_source(source_id, scopes=_scopes_from_query(query))
                    self._json(HTTPStatus.OK, asdict(source))
                    return
                self._json(HTTPStatus.NOT_FOUND, {"error": "Route not found"})
            except (AgenticRAGError, OSError, ValueError) as exc:
                self._error(exc)

        def do_POST(self) -> None:  # noqa: N802
            try:
                self._require_same_origin()
                payload = self._read_json()
                path = urlsplit(self.path).path
                if path == "/api/v1/configure":
                    self._json(HTTPStatus.OK, {"provider": state.configure(payload)})
                    return
                if path == "/api/v1/probe":
                    role = _role(payload.get("role"))
                    if payload.get("base_url"):
                        candidate = RuntimeSelection(
                            runtime=_bounded_string(payload.get("runtime"), "runtime", 64),
                            role=role,
                            base_url=_bounded_string(payload.get("base_url"), "base_url", 2_048),
                            model=(str(payload.get("model", "")).strip() or "__discovery__"),
                            structured_output_mode=(
                                "json_schema"
                                if role is ProviderRole.EMBEDDING
                                else _structured_mode(payload.get("structured_output_mode"))
                            ),
                            api_key=_optional_secret(payload.get("api_key")),
                            provider_kind=_provider_kind(payload.get("provider_kind")),
                        )
                    else:
                        candidate = state.provider(role)
                    result = discover_models(candidate.provider_config())
                    self._json(HTTPStatus.OK, {"role": role.value, **result})
                    return
                if path == "/api/v1/check-model":
                    self._json(HTTPStatus.OK, self._check_model())
                    return
                if path == "/api/v1/ingest":
                    self._json(HTTPStatus.CREATED, self._ingest(payload))
                    return
                if path == "/api/v1/ask":
                    self._json(HTTPStatus.OK, self._ask(payload))
                    return
                if path == "/api/v1/ask-stream":
                    self._stream_ask(payload)
                    return
                cancel = re.fullmatch(r"/api/v1/runs/([0-9a-f]{32})/cancel", path)
                if cancel:
                    self._json(HTTPStatus.OK, {"cancelled": state.cancel_run(cancel[1])})
                    return
                if path == "/api/v1/chats":
                    collection = _bounded_string(payload.get("collection"), "collection", 128)
                    scopes = _string_list(payload.get("scopes"), "scopes", max_items=16, max_chars=128)
                    self._json(HTTPStatus.CREATED, state.conversations.create(collection, list(scopes)))
                    return
                if path == "/api/v1/projects":
                    name = _bounded_string(payload.get("name"), "name", 64)
                    self._json(HTTPStatus.CREATED, state.conversations.create_project(name))
                    return
                project_notes = re.fullmatch(r"/api/v1/projects/(default|[0-9a-f]{32})/notes", path)
                if project_notes:
                    content = _bounded_string(payload.get("content"), "content", 1_000)
                    source_chat_id = payload.get("source_chat_id")
                    if source_chat_id is not None and (not isinstance(source_chat_id, str) or not re.fullmatch(r"[0-9a-f]{32}", source_chat_id)):
                        raise ValueError("Invalid source conversation identifier")
                    self._json(HTTPStatus.CREATED, state.conversations.create_project_note(project_notes[1], content, source_chat_id))
                    return
                self._json(HTTPStatus.NOT_FOUND, {"error": "Route not found"})
            except (AgenticRAGError, OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
                self._error(exc)

        def do_PUT(self) -> None:  # noqa: N802
            try:
                self._require_same_origin()
                path = urlsplit(self.path).path
                note = re.fullmatch(r"/api/v1/project-notes/([0-9a-f]{32})", path)
                if note:
                    payload = self._read_json()
                    content = _bounded_string(payload.get("content"), "content", 1_000)
                    self._json(HTTPStatus.OK, state.conversations.update_project_note(note[1], content))
                    return
                self._json(HTTPStatus.NOT_FOUND, {"error": "Route not found"})
            except (AgenticRAGError, OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
                self._error(exc)

        def do_DELETE(self) -> None:  # noqa: N802
            try:
                self._require_same_origin()
                path = urlsplit(self.path).path
                if path.startswith("/api/v1/chats/"):
                    chat_id = path.removeprefix("/api/v1/chats/")
                    if not re.fullmatch(r"[0-9a-f]{32}", chat_id):
                        raise ValueError("Invalid conversation identifier")
                    state.conversations.delete(chat_id)
                    self._json(HTTPStatus.OK, {"deleted": chat_id})
                    return
                note = re.fullmatch(r"/api/v1/project-notes/([0-9a-f]{32})", path)
                if note:
                    state.conversations.delete_project_note(note[1])
                    self._json(HTTPStatus.OK, {"deleted": note[1]})
                    return
                self._json(HTTPStatus.NOT_FOUND, {"error": "Route not found"})
            except (AgenticRAGError, OSError, ValueError) as exc:
                self._error(exc)

        def _ingest(self, payload: dict[str, Any]) -> dict[str, object]:
            filename = Path(_bounded_string(payload.get("filename"), "filename", 255)).name
            if filename in {"", ".", ".."}:
                raise ValueError("filename is invalid")
            encoded = _bounded_string(payload.get("content_base64"), "content_base64", MAX_JSON_BYTES)
            try:
                data = base64.b64decode(encoded, validate=True)
            except ValueError as exc:
                raise ValueError("content_base64 is invalid") from exc
            ingestion = load_ingestion_config()
            if len(data) > ingestion.max_file_bytes:
                raise ValueError(f"File exceeds the configured {ingestion.max_file_bytes}-byte limit")
            collection = _bounded_string(payload.get("collection"), "collection", 128)
            scopes = _string_list(payload.get("scopes"), "scopes", max_items=16, max_chars=128)
            ocr = payload.get("ocr", "auto")
            if ocr not in {"auto", "never", "always"}:
                raise ValueError("ocr must be auto, never, or always")
            parser = FileParser(
                limits=IngestionLimits(
                    max_file_bytes=ingestion.max_file_bytes,
                    max_pages=ingestion.max_pages,
                    max_segments=ingestion.max_segments,
                ),
                ocr=ocr,
                docling_artifacts_path=ingestion.docling_artifacts_path,
            )
            suffix = Path(filename).suffix
            temporary_path: Path | None = None
            try:
                with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temporary:
                    temporary.write(data)
                    temporary_path = Path(temporary.name)
                draft = parser.parse(temporary_path, collection, scopes)
                draft = replace(draft, logical_path=filename)
                embedding = build_embedding_provider(
                    state.provider(ProviderRole.EMBEDDING).provider_config()
                )
                with state.store() as store:
                    version = Ingestor(store, embedding, parser=parser).ingest_source(draft)
                return {"status": "published", "embedding_provider": embedding.label, **asdict(version)}
            finally:
                if temporary_path is not None:
                    temporary_path.unlink(missing_ok=True)

        def _stream_ask(self, payload: dict[str, Any]) -> None:
            run_id = payload.get("run_id")
            if not isinstance(run_id, str) or not re.fullmatch(r"[0-9a-f]{32}", run_id):
                raise ValueError("Invalid run identifier")
            cancelled = state.start_run(run_id)
            self.send_response(HTTPStatus.OK)
            self._security_headers()
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Accel-Buffering", "no")
            self.end_headers()

            def emit(kind: str, detail: dict[str, object]) -> None:
                data = json.dumps({"type": kind, **detail}, ensure_ascii=False, separators=(",", ":"))
                self.wfile.write(f"data: {data}\n\n".encode("utf-8"))
                self.wfile.flush()

            try:
                emit("started", {"run_id": run_id, "limits": {"max_steps": payload.get("max_steps", 8), "max_seconds": 180}})
                emit("progress", {"message": "Working with the selected model…"})
                result = self._ask(payload, cancelled=cancelled,
                                   on_token=lambda token: emit("token", {"text": token}),
                                   on_event=lambda event: emit("event", {"event": asdict(event)}),
                                   on_evidence=lambda items: emit("evidence", {"items": items}))
                emit("completed", {"result": result})
            except (BrokenPipeError, ConnectionResetError):
                cancelled.set()
            except (AgenticRAGError, OSError, ValueError, TypeError) as exc:
                try:
                    emit("stopped" if cancelled.is_set() else "error", {"message": str(exc)})
                except (BrokenPipeError, ConnectionResetError):
                    pass
            finally:
                state.finish_run(run_id)

        def _ask(
            self, payload: dict[str, Any], *, cancelled: threading.Event | None = None,
            on_token: Callable[[str], None] | None = None,
            on_event: Callable[[Any], None] | None = None,
            on_evidence: Callable[[list[dict[str, str | None]]], None] | None = None,
        ) -> dict[str, object]:
            if cancelled and cancelled.is_set():
                raise WorkflowError("Run stopped")
            question = _bounded_string(payload.get("question"), "question", MAX_QUESTION_CHARS)
            collection = _bounded_string(payload.get("collection"), "collection", 128)
            scopes = _string_list(payload.get("scopes"), "scopes", max_items=16, max_chars=128)
            workflow_name = payload.get("workflow", "agent")
            if workflow_name not in {"agent", "supervisor", "fixed", "direct"}:
                raise ValueError("workflow must be agent, supervisor, fixed, or direct")
            chat_id = payload.get("chat_id")
            if chat_id is not None and (not isinstance(chat_id, str) or not re.fullmatch(r"[0-9a-f]{32}", chat_id)):
                raise ValueError("Invalid conversation identifier")
            history = state.conversations.history(chat_id, collection, list(scopes)) if chat_id else []
            allow_web = payload.get("allow_web", False)
            if not isinstance(allow_web, bool):
                raise ValueError("allow_web must be boolean")
            if allow_web and workflow_name not in {"direct", "supervisor"}:
                raise ValueError("Web search is available in Direct and Supervisor modes")
            if allow_web and not state._web_search_available():
                raise ConfigurationError("Web search is unavailable; install agenticrag[web] or configure hosted search")
            chat_config = state.provider(ProviderRole.CHAT).provider_config()
            image_data_url, image_name = _validated_chat_image(payload.get("image"))
            if image_data_url:
                if workflow_name != "direct" or allow_web:
                    raise ValueError("Image questions currently require Direct mode with web search off")
                if not ollama_supports_vision(chat_config):
                    raise ValueError("Selected model cannot read images. Choose a vision model such as gemma4:12b-mlx")
            chat = build_chat_provider(chat_config)
            if cancelled:
                chat = _CancellableChat(chat, cancelled)
            memory_notes: list[dict[str, object]] = []
            if not allow_web:
                project = state.conversations.project_for_context(collection, list(scopes))
                if project:
                    memory_notes = state.conversations.list_project_notes(str(project["id"]))
                    if memory_notes:
                        chat = _ProjectMemoryChat(chat, memory_notes)
            with state.store() as store:
                if allow_web and workflow_name == "direct":
                    result = WebAnswerWorkflow(chat, history=history).run(
                        question, scopes=scopes, collection=collection
                    )
                elif workflow_name == "direct" or (history and _is_conversation_question(question)):
                    if not chat_id:
                        history_payload = payload.get("history", [])
                        if not isinstance(history_payload, list):
                            raise ValueError("Direct chat history must be an array")
                        for item in history_payload:
                            if (
                                not isinstance(item, dict)
                                or set(item) != {"role", "content"}
                                or not isinstance(item["role"], str)
                                or not isinstance(item["content"], str)
                            ):
                                raise ValueError("Direct chat history has an invalid message")
                            history.append(ChatMessage(item["role"], item["content"]))
                    direct = DirectWorkflow(
                        chat, history=history, model_id=chat_config.model,
                        image_data_url=image_data_url,
                    )
                    result = (
                        direct.run_stream(question, on_token, scopes=scopes, collection=collection)
                        if on_token else direct.run(question, scopes=scopes, collection=collection)
                    )
                else:
                    embedding = build_embedding_provider(
                        state.provider(ProviderRole.EMBEDDING).provider_config()
                    )
                    retriever = HybridRetriever(store, embedding)
                    if workflow_name == "fixed":
                        workflow = FixedRAGWorkflow(retriever, chat)
                    else:
                        skills = _string_list(
                            payload.get("skills", []), "skills", max_items=16, max_chars=64, allow_empty=True
                        )
                        max_steps = payload.get("max_steps", 8)
                        if type(max_steps) is not int or not 1 <= max_steps <= 20:
                            raise ValueError("max_steps must be an integer from 1 to 20")
                        registry = state.skill_registry()
                        if workflow_name == "supervisor":
                            web_search = None
                            if allow_web:
                                web_search = (
                                    OpenAIResponsesWebSearch(chat_config)
                                    if chat_config.kind == "openai" else LocalWebSearch()
                                )
                            workflow = SupervisorAgentWorkflow(
                                retriever,
                                chat,
                                store,
                                skill_registry=registry,
                                selected_skills=skills,
                                web_search=web_search,
                            )
                        else:
                            workflow = BoundedAgenticRAGWorkflow(
                                retriever,
                                chat,
                                store,
                                skill_registry=registry,
                                selected_skills=skills,
                                config=AgentConfig(max_steps=max_steps),
                            )
                    result = workflow.run(question, scopes=scopes, collection=collection,
                                          on_event=on_event, on_evidence=on_evidence)
            response = result.to_dict()
            if cancelled and cancelled.is_set():
                raise WorkflowError("Run stopped")
            response["memory_notes_used"] = len(memory_notes)
            if chat_id:
                recorded_question = question + (f"\n[Attached image: {image_name}]" if image_name else "")
                state.conversations.record(chat_id, recorded_question, response, workflow_name)
                response["chat_id"] = chat_id
            return response

        def _check_model(self) -> dict[str, object]:
            chat = build_chat_provider(state.provider(ProviderRole.CHAT).provider_config())
            started = time.perf_counter()
            raw = chat.complete(
                [
                    ChatMessage(
                        "system",
                        "Solve the bounded check and select the one allowlisted action that would "
                        "verify the arithmetic. Return only the requested structured result.",
                    ),
                    ChatMessage(
                        "user",
                        "There are 3 trials with 8 cases each. Exactly 2 cases are excluded from "
                        "each trial. How many cases remain? The available action is calculate.",
                    ),
                ],
                response_schema=MODEL_CONTRACT_SCHEMA,
                max_tokens=256,
                temperature=0.0,
            )
            value = raw.strip()
            if value.startswith("```") and value.endswith("```"):
                lines = value.splitlines()
                value = "\n".join(lines[1:-1])
            try:
                result = json.loads(value)
            except json.JSONDecodeError as exc:
                raise ValueError("Model returned invalid JSON for the agent contract check") from exc
            if not isinstance(result, dict) or set(result) != {"answer", "action", "assumptions"}:
                raise ValueError("Model response did not match the agent contract fields")
            if result["answer"] != 18 or result["action"] != "calculate":
                raise ValueError("Model did not solve the bounded reasoning/tool-selection check")
            if not isinstance(result["assumptions"], list) or not all(
                isinstance(item, str) for item in result["assumptions"]
            ):
                raise ValueError("Model assumptions did not match the agent contract")
            return {
                "compatible": True,
                "model": chat.config.model,
                "structured_output_mode": chat.config.structured_output_mode,
                "latency_ms": max(0, round((time.perf_counter() - started) * 1_000)),
                "checks": {
                    "structured_json": True,
                    "bounded_reasoning": True,
                    "tool_selection": True,
                    "host_validation": True,
                },
            }

        def _read_json(self) -> dict[str, Any]:
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError as exc:
                raise ValueError("Invalid Content-Length") from exc
            if not 0 < length <= MAX_JSON_BYTES:
                raise ValueError(f"JSON request must contain 1 to {MAX_JSON_BYTES} bytes")
            if self.headers.get_content_type() != "application/json":
                raise ValueError("Content-Type must be application/json")
            value = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(value, dict):
                raise ValueError("JSON request must be an object")
            return value

        def _require_same_origin(self) -> None:
            origin = self.headers.get("Origin")
            if origin is None:
                return
            parsed = urlsplit(origin)
            if parsed.scheme not in {"http", "https"} or parsed.netloc != self.headers.get("Host"):
                raise AuthorizationError("Cross-origin write request rejected")

        def _asset(self, name: str) -> None:
            try:
                data = resources.files("agenticrag.ui").joinpath(name).read_bytes()
            except (FileNotFoundError, ModuleNotFoundError):
                self._json(HTTPStatus.NOT_FOUND, {"error": "UI asset not found"})
                return
            content_type = mimetypes.guess_type(name)[0] or "application/octet-stream"
            self.send_response(HTTPStatus.OK)
            self._security_headers()
            if name.endswith(".webmanifest"):
                content_type = "application/manifest+json"
            if name.endswith(".woff2"):
                content_type = "font/woff2"
            self.send_header("Content-Type", content_type if name.endswith((".png", ".woff2")) else f"{content_type}; charset=utf-8")
            self.send_header("Cache-Control", "public, max-age=31536000, immutable" if name.endswith(".woff2") else "no-cache")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _json(self, status: HTTPStatus, payload: object) -> None:
            data = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            self.send_response(status)
            self._security_headers()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _error(self, exc: Exception) -> None:
            if isinstance(exc, AuthorizationError):
                status = HTTPStatus.FORBIDDEN
            elif isinstance(exc, (ConfigurationError, ValueError, TypeError, json.JSONDecodeError)):
                status = HTTPStatus.BAD_REQUEST
            else:
                status = HTTPStatus.UNPROCESSABLE_ENTITY
            self._json(status, {"error": str(exc), "error_type": type(exc).__name__})

        def _security_headers(self) -> None:
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
                "connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'",
            )

        def log_message(self, format: str, *args: object) -> None:
            print(f"{self.client_address[0]} - {format % args}")

    return WorkbenchHandler


def serve(
    *,
    host: str = "127.0.0.1",
    port: int = 8787,
    db_path: str = ".data/corpus.db",
    skills_root: Path = Path(".agenticrag/skills"),
    open_browser: bool = True,
    allow_remote: bool = False,
) -> None:
    if not 1 <= port <= 65_535:
        raise ConfigurationError("Port must be between 1 and 65535")
    if host not in {"127.0.0.1", "localhost", "::1"} and not allow_remote:
        raise ConfigurationError(
            "Non-loopback UI binding requires --allow-remote and a trusted reverse proxy"
        )
    state = WorkbenchState(db_path, skills_root)
    server = ThreadingHTTPServer((host, port), make_handler(state))
    url_host = "127.0.0.1" if host in {"0.0.0.0", "::"} else host
    url = f"http://{url_host}:{port}"
    print(json.dumps({"status": "serving", "url": url, "local_only": not allow_remote}))
    if open_browser:
        threading.Timer(0.35, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        state.conversations.close()


def _role(value: object) -> ProviderRole:
    try:
        return ProviderRole(str(value))
    except ValueError as exc:
        raise ConfigurationError("role must be chat or embedding") from exc


def _structured_mode(value: object) -> str:
    if value not in {"json_schema", "json_object", "prompt"}:
        raise ConfigurationError("structured_output_mode is invalid")
    return str(value)


def _provider_kind(value: object) -> str:
    if value in {None, ""}:
        return "local"
    if value not in {"local", "openai"}:
        raise ConfigurationError("provider_kind must be local or openai")
    return str(value)


def _optional_secret(value: object) -> str | None:
    if value in {None, ""}:
        return None
    return _bounded_string(value, "api_key", 4_096)


def _bounded_string(value: object, name: str, limit: int) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f"{name} must contain 1 to {limit} characters")
    if any(char == "\x00" for char in value):
        raise ValueError(f"{name} cannot contain NUL bytes")
    return value.strip()


def _string_list(
    value: object,
    name: str,
    *,
    max_items: int,
    max_chars: int,
    allow_empty: bool = False,
) -> tuple[str, ...]:
    if not isinstance(value, list) or (not allow_empty and not value) or len(value) > max_items:
        raise ValueError(f"{name} must be a list containing at most {max_items} values")
    result = tuple(_bounded_string(item, name, max_chars) for item in value)
    if len(set(result)) != len(result):
        raise ValueError(f"{name} cannot contain duplicates")
    return result


def _scopes_from_query(query: dict[str, list[str]]) -> tuple[str, ...]:
    values: list[str] = []
    for raw in query.get("scope", []):
        values.extend(item for item in raw.split(",") if item)
    return _string_list(values, "scope", max_items=16, max_chars=128)


def _optional_query(query: dict[str, list[str]], name: str) -> str | None:
    values = query.get(name, [])
    if not values or not values[0].strip():
        return None
    return _bounded_string(values[0], name, 128)


def _validated_chat_image(value: object) -> tuple[str | None, str | None]:
    if value is None:
        return None, None
    if not isinstance(value, dict) or set(value) != {"filename", "mime_type", "data_base64"}:
        raise ValueError("Image attachment must include filename, mime_type, and data_base64")
    name = _bounded_string(value["filename"], "image filename", 150)
    name = Path(name).name
    mime = value["mime_type"]
    signatures = {
        "image/png": lambda data: data.startswith(b"\x89PNG\r\n\x1a\n"),
        "image/jpeg": lambda data: data.startswith(b"\xff\xd8\xff"),
        "image/webp": lambda data: data.startswith(b"RIFF") and data[8:12] == b"WEBP",
    }
    if not isinstance(mime, str) or mime not in signatures:
        raise ValueError("Image must be PNG, JPEG, or WebP")
    encoded = value["data_base64"]
    if not isinstance(encoded, str) or len(encoded) > 11_200_000:
        raise ValueError("Image exceeds the 8 MiB limit")
    try:
        data = base64.b64decode(encoded, validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise ValueError("Image data is not valid base64") from exc
    if len(data) > 8 * 1024 * 1024 or not signatures[mime](data):
        raise ValueError("Image content does not match its type or exceeds 8 MiB")
    return f"data:{mime};base64,{encoded}", name


def _is_conversation_question(question: str) -> bool:
    text = question.casefold()
    asks_recall = re.search(r"\b(repeat|remind|recap|list|what|which|summarize|tell)\b", text)
    names_chat = re.search(
        r"\b(?:my|our)\s+(?:(?:first|last|previous|earlier|prior|past)\s+)?(?:user\s+)?(?:questions?|messages?|prompts?)\b"
        r"|\b(?:i|we)\s+ask(?:ed)?\b"
        r"|\b(?:this|our|the)\s+(?:conversation|chat(?:\s+history)?)\b",
        text,
    )
    return bool(asks_recall and names_chat)
