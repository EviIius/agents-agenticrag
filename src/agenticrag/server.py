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
from contextlib import contextmanager, nullcontext
from dataclasses import asdict, replace
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import resources
from pathlib import Path
from typing import Any, Callable, Iterator, Sequence
from urllib.parse import parse_qs, unquote, urlsplit
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from . import __version__
from .config import (
    ProviderRole,
    StoreConfig,
    load_ingestion_config,
    load_provider_config,
    load_store_config,
)
from .conversations import ConversationStore
from .domain import RunEvent, SourceDraft
from .errors import AgenticRAGError, AuthorizationError, ConfigurationError, WorkflowError
from .followup_query import build_retrieval_query
from .web_chat import WebChat
from .ingestion import FileParser, IngestionLimits, Ingestor, parser_capabilities
from .postgres_store import PostgresCorpusStore
from .providers.openai_compatible import build_chat_provider, build_embedding_provider
from .providers.base import ChatMessage, ChatProvider
from .run_store import WorkbenchRunStore
from .runtimes import RUNTIME_PROFILES, RuntimeSelection, discover_models, ollama_supports_vision
from .store import CorpusStore, SQLiteCorpusStore
from .web_search import (configured_search_label,
                         configured_search_provider, local_web_search_available)


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

    @property
    def config(self):
        return getattr(self._provider, "config", None)

    def last_call_metrics(self):
        metrics = getattr(self._provider, "last_call_metrics", None)
        return metrics() if callable(metrics) else None

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
    def __init__(self, provider: ChatProvider, cancelled: threading.Event, slot=None) -> None:
        self._provider = provider
        self._cancelled = cancelled
        self._slot = slot

    @property
    def label(self) -> str:
        return self._provider.label

    def last_call_metrics(self) -> dict[str, int] | None:
        metrics = getattr(self._provider, "last_call_metrics", None)
        return metrics() if callable(metrics) else None

    @property
    def config(self):
        return getattr(self._provider, "config", None)

    @contextmanager
    def _completion(self):
        acquired = False
        try:
            if self._slot is not None:
                while not self._cancelled.is_set():
                    if self._slot.acquire(timeout=0.25):
                        acquired = True
                        break
            if self._cancelled.is_set():
                raise WorkflowError("Run stopped")
            yield
        finally:
            if acquired:
                self._slot.release()

    def complete(self, messages, *, response_schema=None, max_tokens=2048, temperature=0.0):
        with self._completion():
            answer = self._provider.complete(messages, response_schema=response_schema,
                                             max_tokens=max_tokens, temperature=temperature)
            if self._cancelled.is_set():
                raise WorkflowError("Run stopped")
            return answer

    def stream_complete(self, messages, on_token, *, max_tokens=2048, temperature=0.0):
        def token(text):
            if self._cancelled.is_set():
                raise WorkflowError("Run stopped")
            on_token(text)
        with self._completion():
            streamer = getattr(self._provider, "stream_complete", None)
            if streamer:
                answer = streamer(messages, token, max_tokens=max_tokens, temperature=temperature)
            else:
                answer = self._provider.complete(messages, max_tokens=max_tokens, temperature=temperature)
                token(answer)
            if self._cancelled.is_set():
                raise WorkflowError("Run stopped")
            return answer


UI_FILES = {
    "/": "index.html", "/index.html": "index.html", "/app.js": "app.js", "/boot.js": "boot.js", "/sw.js": "sw.js",
    "/tokens.css": "tokens.css", "/chat.css": "chat.css",
    "/vendor/marked.umd.js": "vendor/marked.umd.js",
    "/vendor/purify.min.js": "vendor/purify.min.js",
    "/manifest.webmanifest": "manifest.webmanifest", "/icon-180.png": "icon-180.png",
    "/icon-192.png": "icon-192.png", "/icon-512.png": "icon-512.png",
    **{f"/fonts/{name}": f"fonts/{name}" for name in (
        "Geist-Variable.woff2", "Geist-Variable-LatinExt.woff2",
        "GeistMono-Variable.woff2", "GeistMono-Variable-LatinExt.woff2",
        "Newsreader-Variable.woff2", "Newsreader-Variable-LatinExt.woff2",
        "Newsreader-Variable-Italic.woff2",
        "Literata-Variable.woff2", "Literata-Variable-LatinExt.woff2", "Literata-Variable-Italic.woff2",
        "AtkinsonHyperlegibleNext-Variable.woff2", "AtkinsonHyperlegibleNext-Variable-LatinExt.woff2", "AtkinsonHyperlegibleNext-Variable-Italic.woff2",
    )},
}


def _loaded_model_state(selection: RuntimeSelection) -> bool | None:
    """Best-effort memory state; unknown runtimes must not be reported as unloaded."""
    if selection.runtime not in {"ollama", "lm-studio"}:
        return None
    parsed = urlsplit(selection.base_url)
    if parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        return None
    origin = f"{parsed.scheme}://{parsed.netloc}"
    path = "/api/ps" if selection.runtime == "ollama" else "/api/v0/models"
    try:
        with urlopen(Request(origin + path, headers={"Accept": "application/json"}), timeout=1.5) as response:  # noqa: S310
            payload = json.loads(response.read(256_000))
        rows = payload.get("models", []) if selection.runtime == "ollama" else payload.get("data", [])
        if not isinstance(rows, list):
            return None
        if selection.runtime == "ollama":
            return any(row.get("name") == selection.model or row.get("model") == selection.model for row in rows if isinstance(row, dict))
        for row in rows:
            if isinstance(row, dict) and row.get("id") == selection.model:
                state = row.get("state") or row.get("status")
                return state in {"loaded", "ready"} if isinstance(state, str) else None
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, TypeError, json.JSONDecodeError):
        pass
    return None
class WorkbenchState:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._selection_path = (
            None if db_path == ":memory:" else Path(db_path).resolve().with_name("workbench-providers.json")
        )
        self.conversations = ConversationStore(
            ":memory:" if db_path == ":memory:" else str(Path(db_path).resolve().with_name("workbench-chats.db"))
        )
        self.runs = WorkbenchRunStore(
            ":memory:" if db_path == ":memory:" else str(Path(db_path).resolve().with_name("workbench-runs.db"))
        )
        self._lock = threading.RLock()
        self._active_runs: dict[str, threading.Event] = {}
        self._web_approvals: dict[str, tuple[threading.Event, bool | None]] = {}
        self._model_slot = threading.Semaphore(1)
        self._warm_active = False
        self._runtime_status_cache: tuple[float, dict[str, object]] | None = None
        self._last_fresh_runtime_probe = 0.0
        self.started_at = datetime.now(timezone.utc).isoformat()
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
            approval = self._web_approvals.get(run_id)
            if approval:
                approval[0].set()
            run = self.runs.get(run_id)
            if run:
                self.runs.update(run_id, cancel_requested=True,
                                 status="stopped" if run["status"] == "queued" else None,
                                 error="Run stopped" if run["status"] == "queued" else None)
            return True

    def request_web_approval(self, run_id: str, cancelled: threading.Event,
                             query: str, emit: Callable[[Any], None], timeout: int) -> bool:
        approval = threading.Event()
        with self._lock:
            self._web_approvals[run_id] = (approval, None)
        emit(RunEvent("web_approval_requested", {"run_id": run_id, "query": query}))
        deadline = time.monotonic() + timeout
        try:
            while not cancelled.is_set() and time.monotonic() < deadline:
                approval.wait(min(0.25, max(0, deadline - time.monotonic())))
                with self._lock:
                    decision = self._web_approvals.get(run_id, (approval, None))[1]
                if decision is not None:
                    emit(RunEvent("web_approval_resolved", {"allowed": decision}))
                    return decision
            emit(RunEvent("web_approval_resolved", {"allowed": False, "reason": "stopped_or_timed_out"}))
            return False
        finally:
            with self._lock:
                self._web_approvals.pop(run_id, None)

    def decide_web_approval(self, run_id: str, allowed: bool) -> bool:
        with self._lock:
            pending = self._web_approvals.get(run_id)
            if pending is None:
                return False
            self._web_approvals[run_id] = (pending[0], allowed)
            pending[0].set()
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

    def provider(self, role: ProviderRole) -> RuntimeSelection:
        with self._lock:
            try:
                return self._providers[role]
            except KeyError as exc:
                raise ConfigurationError(
                    f"Configure the {role.value} runtime in Models before using this action"
                ) from exc

    def runtime_status(self, *, fresh: bool = False) -> dict[str, object]:
        now = time.monotonic()
        with self._lock:
            cached = self._runtime_status_cache
            if fresh and now - self._last_fresh_runtime_probe >= 3:
                self._last_fresh_runtime_probe = now
            elif fresh and cached:
                return cached[1]
            elif cached and now - cached[0] < 15:
                return cached[1]
            providers = dict(self._providers)
        result: dict[str, object] = {"checked_at": datetime.now(timezone.utc).isoformat()}
        for role in (ProviderRole.CHAT,):
            selection = providers.get(role)
            if selection is None:
                result[role.value] = {"configured": False, "reachable": False, "latency_ms": None, "model_present": None, "error": None,
                                      "runtime": None, "endpoint": None, "error_kind": None, "loaded": None}
                continue
            parsed_endpoint = urlsplit(selection.base_url)
            endpoint = parsed_endpoint.hostname or ""
            if parsed_endpoint.port:
                endpoint += f":{parsed_endpoint.port}"
            runtime = selection.runtime if selection.runtime in {"ollama", "lm-studio", "llama-cpp", "vllm", "openai"} else None
            try:
                probe = discover_models(replace(selection.provider_config(), timeout_seconds=2.0))
                result[role.value] = {
                    "configured": True, "reachable": True, "latency_ms": probe["latency_ms"],
                    "model_present": probe["configured_model_available"], "error": None,
                    "runtime": runtime, "endpoint": endpoint,
                    "error_kind": None if probe["configured_model_available"] else "model_missing",
                    "loaded": _loaded_model_state(selection),
                }
            except (AgenticRAGError, OSError, ValueError) as exc:
                message = str(exc)[:240]
                kind = "timeout" if "timed out" in message.lower() or "timeout" in message.lower() else "refused" if "refused" in message.lower() or "could not reach" in message.lower() else "invalid" if "invalid" in message.lower() else "http"
                result[role.value] = {"configured": True, "reachable": False, "latency_ms": None, "model_present": None, "error": message,
                                      "runtime": runtime, "endpoint": endpoint, "error_kind": kind, "loaded": None}
        with self._lock:
            self._runtime_status_cache = (time.monotonic(), result)
        return result

    def warm_chat_model(self) -> dict[str, bool]:
        selection = self.provider(ProviderRole.CHAT)
        if selection.provider_kind != "local" or selection.runtime not in {"ollama", "lm-studio"}:
            raise ConfigurationError("Warm-up is available for local Ollama and LM Studio models")
        with self._lock:
            if self._warm_active or self._active_runs:
                return {"started": False}
            if not self._model_slot.acquire(blocking=False):
                return {"started": False}
            self._warm_active = True

        def warm() -> None:
            try:
                parsed = urlsplit(selection.base_url)
                origin = f"{parsed.scheme}://{parsed.netloc}"
                if selection.runtime == "ollama":
                    endpoint = origin + "/api/generate"
                    payload = {"model": selection.model, "keep_alive": "30m", "stream": False,
                               "options": {"num_ctx": 16384}}
                else:
                    endpoint = selection.base_url + "/chat/completions"
                    payload = {"model": selection.model, "messages": [{"role": "user", "content": "Ready"}], "max_tokens": 1, "stream": False}
                request = Request(endpoint, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
                with urlopen(request, timeout=120) as response:  # noqa: S310
                    response.read(1024)
            except (HTTPError, URLError, TimeoutError, OSError, ValueError):
                pass
            finally:
                with self._lock:
                    self._warm_active = False
                    self._runtime_status_cache = None
                self._model_slot.release()

        threading.Thread(target=warm, daemon=True, name="model-warm-up").start()
        return {"started": True}

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
            if previous and previous.runtime == selection.runtime and previous.base_url == selection.base_url and not payload.get("api_key"):
                selection = replace(selection, api_key=previous.api_key)
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

    def prune_web_pages(self) -> int:
        expired = self.conversations.expired_web_sources()
        if not expired:
            return 0
        removed = 0
        with self.store() as store:
            for project_id, source_id in expired:
                try:
                    project = self.conversations.get_project(project_id)
                    store.delete_web_source_version(source_id, scopes=tuple(project["scopes"]))
                except (AuthorizationError, ValueError):
                    # A removed project or source can leave stale registry metadata.
                    pass
                self.conversations.forget_web_source(source_id)
                removed += 1
        return removed

    def bootstrap(self) -> dict[str, object]:
        ingestion = load_ingestion_config()
        return {"version": __version__, "providers": self.public_providers(), "runtimes": RUNTIME_PROFILES,
                "store": load_store_config(self.db_path).public_dict(),
                "local_web_search_available": self._web_search_available(),
                "web_search_provider": configured_search_label(),
                "web": {"available": self._web_search_available(), "max_searches": 1, "max_pages": 4},
                "ingestion": {"limits": asdict(ingestion), "formats": parser_capabilities(ingestion.docling_artifacts_path)}}

    def _web_search_available(self) -> bool:
        return local_web_search_available()


def make_handler(state: WorkbenchState) -> type[BaseHTTPRequestHandler]:
    class WorkbenchHandler(BaseHTTPRequestHandler):
        server_version = "ChatWeb/0.5"

        def do_GET(self) -> None:  # noqa: N802
            try:
                self._require_allowed_host()
                parsed = urlsplit(self.path)
                if parsed.path == "/healthz":
                    self._json(HTTPStatus.OK, {"status": "ok", "version": __version__})
                    return
                if parsed.path == "/api/v1/health":
                    self._json(HTTPStatus.OK, {"ok": True, "version": __version__, "asset_version": "50", "started_at": state.started_at,
                                                "server_time": datetime.now(timezone.utc).isoformat()})
                    return
                if parsed.path in UI_FILES:
                    self._asset(UI_FILES[parsed.path])
                    return
                if parsed.path == "/api/v1/bootstrap":
                    self._json(HTTPStatus.OK, state.bootstrap())
                    return
                if parsed.path == "/api/v1/runtime-status":
                    self._json(HTTPStatus.OK, state.runtime_status(fresh=parse_qs(parsed.query).get("fresh") == ["1"]))
                    return
                run = re.fullmatch(r"/api/v1/runs/([0-9a-f]{32})", parsed.path)
                if run:
                    record = state.runs.get(run[1])
                    if record is None:
                        self._json(HTTPStatus.NOT_FOUND, {"error": "Run not found"})
                    else:
                        self._json(HTTPStatus.OK, record)
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
                    response = asdict(source)
                    if source.collection.startswith("web-"):
                        project_id = source.collection.removeprefix("web-")
                        response["web_page"] = state.conversations.web_page_info(project_id, source.id) or {
                            "project_id": project_id, "final_url": source.logical_path,
                            "source_version_id": source.id, "saved_library_version_id": None,
                        }
                    self._json(HTTPStatus.OK, response)
                    return
                self._json(HTTPStatus.NOT_FOUND, {"error": "Route not found"})
            except (AgenticRAGError, OSError, ValueError) as exc:
                self._error(exc)

        def do_POST(self) -> None:  # noqa: N802
            try:
                self._require_allowed_host()
                self._require_same_origin()
                payload = self._read_json()
                path = urlsplit(self.path).path
                if path == "/api/v1/configure":
                    self._json(HTTPStatus.OK, {"provider": state.configure(payload)})
                    return
                if path == "/api/v1/runtime/warm":
                    if payload.get("role") != "chat":
                        raise ValueError("Only the chat model can be warmed")
                    self._json(HTTPStatus.ACCEPTED, state.warm_chat_model())
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
                save_web = re.fullmatch(r"/api/v1/web-sources/(version_[0-9a-f]+)/save", path)
                if save_web:
                    self._json(HTTPStatus.OK, self._save_web_source(save_web[1], payload))
                    return
                if path == "/api/v1/ask":
                    self._json(HTTPStatus.OK, self._ask(payload))
                    return
                if path == "/api/v1/ask-stream":
                    self._stream_ask(payload)
                    return
                if path == "/api/v1/runs":
                    self._start_durable_run(payload)
                    return
                cancel = re.fullmatch(r"/api/v1/runs/([0-9a-f]{32})/cancel", path)
                if cancel:
                    self._json(HTTPStatus.OK, {"cancelled": state.cancel_run(cancel[1])})
                    return
                approval = re.fullmatch(r"/api/v1/runs/([0-9a-f]{32})/web-approval", path)
                if approval:
                    if set(payload) != {"allow"} or type(payload["allow"]) is not bool:
                        raise ValueError("Web approval requires one boolean allow field")
                    self._json(HTTPStatus.OK, {"accepted": state.decide_web_approval(approval[1], payload["allow"])})
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
                self._require_allowed_host()
                self._require_same_origin()
                path = urlsplit(self.path).path
                chat = re.fullmatch(r"/api/v1/chats/([0-9a-f]{32})", path)
                if chat:
                    payload = self._read_json()
                    action = payload.get("action")
                    if action == "rename":
                        result = state.conversations.rename(chat[1], _bounded_string(payload.get("title"), "title", 100))
                    elif action == "pin":
                        if not isinstance(payload.get("pinned"), bool):
                            raise ValueError("pinned must be a boolean")
                        result = state.conversations.set_pinned(chat[1], payload["pinned"])
                    elif action == "move":
                        project_id = payload.get("project_id")
                        if not isinstance(project_id, str) or not re.fullmatch(r"default|[0-9a-f]{32}", project_id):
                            raise ValueError("Invalid project identifier")
                        result = state.conversations.move(chat[1], project_id)
                    else:
                        raise ValueError("Unknown chat action")
                    self._json(HTTPStatus.OK, result)
                    return
                note = re.fullmatch(r"/api/v1/project-notes/([0-9a-f]{32})", path)
                if note:
                    payload = self._read_json()
                    content = _bounded_string(payload.get("content"), "content", 1_000)
                    self._json(HTTPStatus.OK, state.conversations.update_project_note(note[1], content))
                    return
                project_settings = re.fullmatch(r"/api/v1/projects/(default|[0-9a-f]{32})/settings", path)
                if project_settings:
                    payload = self._read_json()
                    if set(payload) == {"web_mode"}:
                        project = state.conversations.update_project_web_mode(project_settings[1], payload["web_mode"])
                    elif set(payload) == {"web_retention"}:
                        project = state.conversations.update_project_web_retention(
                            project_settings[1], payload["web_retention"]
                        )
                    else:
                        raise ValueError("Project settings need exactly web_mode or web_retention")
                    self._json(HTTPStatus.OK, project)
                    return
                self._json(HTTPStatus.NOT_FOUND, {"error": "Route not found"})
            except (AgenticRAGError, OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
                self._error(exc)

        def do_DELETE(self) -> None:  # noqa: N802
            try:
                self._require_allowed_host()
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
                with state.store() as store:
                    version = Ingestor(store, parser=parser).ingest_source(draft)
                return {"status": "published", "index": "lexical-only", **asdict(version)}
            finally:
                if temporary_path is not None:
                    temporary_path.unlink(missing_ok=True)

        def _save_web_source(self, source_id: str, payload: dict[str, Any]) -> dict[str, object]:
            if set(payload) != {"project_id"}:
                raise ValueError("Save request needs exactly project_id")
            project_id = _bounded_string(payload["project_id"], "project_id", 32)
            project = state.conversations.get_project(project_id)
            scopes = tuple(str(scope) for scope in project["scopes"])
            with state.store() as store:
                source = store.get_source(source_id, scopes=scopes)
                if source.collection != f"web-{project_id}" or source.text is None:
                    raise AuthorizationError("Web source is outside this project")
                record = state.conversations.web_page_info(project_id, source_id)
                if record and record.get("saved_library_version_id"):
                    saved = store.get_source(str(record["saved_library_version_id"]), scopes=scopes)
                    return {"status": "already_saved", "source": asdict(saved)}
                draft = SourceDraft(str(project["collection"]), source.logical_path, "text/plain",
                                    source.text, scopes, original_bytes=source.text.encode("utf-8"),
                                    parser_id="web-saved-v1")
                saved = Ingestor(store).ingest_source(draft)
                if record is None:
                    state.conversations.record_web_page(project_id, source.id, source.logical_path,
                                                        source.logical_path, source.title or source.logical_path,
                                                        source.sha256, "forever")
                state.conversations.mark_web_page_saved(project_id, source.id, saved.id)
            return {"status": "saved", "source": asdict(saved)}

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
                effort = payload.get("effort", "standard")
                limits = {"max_searches": 1, "max_pages": 4}
                emit("started", {"run_id": run_id, "limits": limits})
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

        def _start_durable_run(self, payload: dict[str, Any]) -> None:
            run_id = payload.get("run_id")
            chat_id = payload.get("chat_id")
            if not isinstance(run_id, str) or not re.fullmatch(r"[0-9a-f]{32}", run_id):
                raise ValueError("Invalid run identifier")
            if not isinstance(chat_id, str) or not re.fullmatch(r"[0-9a-f]{32}", chat_id):
                raise ValueError("A saved conversation is required for a durable run")
            question = _bounded_string(payload.get("question"), "question", MAX_QUESTION_CHARS)
            workflow = payload.get("workflow", "chat")
            if workflow != "chat":
                raise ValueError("Only normal chat is supported. Reload the app to update its controls.")
            if state.runs.get(run_id) is not None:
                raise ValueError("Run identifier already exists")
            # Validate conversation access before creating an observable run.
            collection = _bounded_string(payload.get("collection"), "collection", 128)
            scopes = _string_list(payload.get("scopes"), "scopes", max_items=16, max_chars=128)
            state.conversations.history(chat_id, collection, list(scopes))
            chat_config = state.provider(ProviderRole.CHAT).provider_config()
            cancelled = state.start_run(run_id)
            try:
                state.runs.create(run_id, chat_id, question, workflow)
            except Exception:
                state.finish_run(run_id)
                raise

            def worker() -> None:
                streamed = ""
                last_flush = time.monotonic()
                recorded_events = []
                try:
                    if cancelled.is_set():
                        raise WorkflowError("Run stopped")
                    state.runs.update(run_id, status="running")
                    def token(text):
                        nonlocal streamed, last_flush
                        streamed += text
                        if time.monotonic() - last_flush >= 0.25:
                            state.runs.update(run_id, streamed_text=streamed)
                            last_flush = time.monotonic()
                    def event(item):
                        recorded_events.append(asdict(item))
                        state.runs.update(run_id, event={"type": "event", "event": asdict(item)})
                    def evidence(items):
                        state.runs.update(run_id, event={"type": "evidence", "items": items})
                    result = self._ask(payload, cancelled=cancelled, on_token=token, on_event=event,
                                       on_evidence=evidence, chat_config=chat_config)
                    state.runs.update(run_id, status="completed", streamed_text=streamed, result=result)
                except Exception as exc:
                    error = "Run stopped" if cancelled.is_set() else str(exc)[:1000]
                    status = "stopped" if cancelled.is_set() else "failed"
                    # A stopped or interrupted answer remains visible in saved history.
                    partial = {"workflow": "chat", "provider": chat_config.label,
                               "question": question, "answer": (streamed.rstrip()+"\n\n" if streamed else "")+error,
                               "abstained": True, "incomplete": True, "elapsed_ms": 0,
                               "citations": [], "evidence": [], "events": recorded_events}
                    try:
                        state.conversations.record(chat_id, question, partial, "chat")
                    except ValueError:
                        pass  # The conversation may have been deleted in another window.
                    state.runs.update(run_id, status=status, streamed_text=streamed, result=partial, error=error)
                finally:
                    state.finish_run(run_id)

            threading.Thread(target=worker, name=f"workbench-run-{run_id[:8]}", daemon=True).start()
            self._json(HTTPStatus.ACCEPTED, {"run_id": run_id, "status": "queued"})

        def _ask(self, payload: dict[str, Any], *, cancelled=None, on_token=None, on_event=None,
                 on_evidence=None, chat_config=None) -> dict[str, object]:
            if payload.get("workflow", "chat") != "chat":
                raise ValueError("Only normal chat is supported. Reload the app.")
            if any(key in payload for key in ("skills", "effort", "deep_sources", "auto_route", "max_steps")):
                raise ValueError("Unsupported chat settings. Reload the app.")
            state.prune_web_pages()
            question = _bounded_string(payload.get("question"), "question", MAX_QUESTION_CHARS)
            collection = _bounded_string(payload.get("collection"), "collection", 128)
            scopes = _string_list(payload.get("scopes"), "scopes", max_items=16, max_chars=128)
            chat_id = payload.get("chat_id")
            if chat_id is not None and (not isinstance(chat_id, str) or not re.fullmatch(r"[0-9a-f]{32}", chat_id)):
                raise ValueError("Invalid conversation identifier")
            history = state.conversations.history(chat_id, collection, list(scopes)) if chat_id else []
            project = state.conversations.project_for_context(collection, list(scopes))
            web_mode = str(project.get("web_mode", "ask")) if project else "off"
            requested_web = payload.get("allow_web", False)
            if type(requested_web) is not bool:
                raise ValueError("allow_web must be boolean")
            if web_mode == "off" and requested_web:
                raise ValueError("Web is Off for this project")
            search_enabled = web_mode == "on" or web_mode == "ask"
            if search_enabled and not state._web_search_available():
                raise ConfigurationError("Web search is unavailable. Configure DuckDuckGo, SearXNG or Brave Search, or set Web Off.")
            image, image_name = _validated_chat_image(payload.get("image"))
            config = chat_config or state.provider(ProviderRole.CHAT).provider_config()
            if image and not ollama_supports_vision(config):
                raise ValueError("The selected model cannot read images. Select a vision model.")
            chat = build_chat_provider(config)
            chat = _CancellableChat(chat, cancelled if cancelled is not None else threading.Event(),
                                    state._model_slot if config.kind == "local" else None)
            notes = state.conversations.list_project_notes(str(project["id"])) if project and not search_enabled else []
            if notes:
                chat = _ProjectMemoryChat(chat, notes)
            decision = None
            def permission(query):
                nonlocal decision
                if requested_web:
                    decision = True
                    return True
                run_id = payload.get("run_id")
                if not isinstance(run_id, str) or cancelled is None or on_event is None:
                    raise WorkflowError("Web Ask requires a saved chat request for approval")
                decision = state.request_web_approval(run_id, cancelled, query, on_event, 180)
                return decision
            # Only user-authored questions enter the public search query.
            query = build_retrieval_query(question, [{"role": m.role, "content": m.content} for m in history])
            with state.store() as store:
                result = WebChat(chat, store, search=configured_search_provider() if search_enabled else None,
                                 registry=state.conversations, project=project).run(
                    question, scopes=scopes, collection=collection, history=history, query=query, image=image,
                    cancelled=cancelled, permission=permission if web_mode == "ask" else None,
                    on_token=on_token, on_event=on_event, on_evidence=on_evidence)
            response = result.to_dict()
            if decision is False:
                response["answer"] += "\n\nWeb access was declined. This answer uses no new web sources."
            response["memory_notes_used"] = len(notes)
            if chat_id:
                state.conversations.record(chat_id, question + (f"\n[Attached image: {image_name}]" if image_name else ""), response, "chat")
                response["chat_id"] = chat_id
            return response

        def _check_model(self) -> dict[str, object]:
            with state._model_slot:
                chat = build_chat_provider(state.provider(ProviderRole.CHAT).provider_config())
                started = time.perf_counter()
                text = chat.complete([ChatMessage("user", "Reply with the word Ready.")], max_tokens=32)
            return {"compatible": bool(text.strip()), "model": chat.config.model,
                    "answer": text, "latency_ms": round((time.perf_counter()-started)*1000)}

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

        def _require_allowed_host(self) -> None:
            host = self.headers.get("Host", "")
            if not host or any(character in host for character in ("/", "@", ",", " ", "\t")):
                raise AuthorizationError("Unrecognized request host")
            try:
                parsed = urlsplit("//" + host)
                _ = parsed.port
            except ValueError as exc:
                raise AuthorizationError("Unrecognized request host") from exc
            allowed = {"localhost", "127.0.0.1", "::1"}
            allowed.update(
                value.strip().lower().rstrip(".")
                for value in os.environ.get("AGENTICRAG_ALLOWED_HOSTS", "").split(",") if value.strip()
            )
            if parsed.hostname is None or parsed.hostname.lower().rstrip(".") not in allowed:
                raise AuthorizationError("Unrecognized request host")

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
            versioned_asset = bool(urlsplit(self.path).query) and name not in {"index.html"}
            self.send_header(
                "Cache-Control",
                "public, max-age=31536000, immutable"
                if name.endswith(".woff2") or (versioned_asset and name not in {"boot.js", "sw.js"}) else "no-cache",
            )
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
    open_browser: bool = True,
    allow_remote: bool = False,
) -> None:
    if not 1 <= port <= 65_535:
        raise ConfigurationError("Port must be between 1 and 65535")
    if host not in {"127.0.0.1", "localhost", "::1"} and not allow_remote:
        raise ConfigurationError(
            "Non-loopback UI binding requires --allow-remote and a trusted reverse proxy"
        )
    state = WorkbenchState(db_path)
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
        state.runs.close()
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
