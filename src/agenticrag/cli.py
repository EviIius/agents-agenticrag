from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Sequence

from .config import (
    ProviderRole,
    StoreConfig,
    load_ingestion_config,
    load_provider_config,
    load_store_config,
)
from .agent import AgentConfig, BoundedAgenticRAGWorkflow
from .errors import AgenticRAGError, ConfigurationError
from .experiments import (
    ExperimentCase,
    ExperimentRunner,
    JsonlRunJournal,
    summarize_experiments,
)
from .ingestion import FileParser, IngestionLimits, Ingestor, parser_capabilities
from .providers.openai_compatible import build_chat_provider, build_embedding_provider
from .providers.openai_responses import OpenAIResponsesWebSearch
from .providers.base import ChatMessage
from .postgres_store import PostgresCorpusStore
from .retrieval import HybridRetriever
from .runtimes import discover_models
from .skills import SkillRegistry
from .store import SQLiteCorpusStore
from .supervisor import SupervisorAgentWorkflow
from .workflows import DirectWorkflow, FixedRAGWorkflow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agenticrag")
    parser.add_argument(
        "--db", default=".data/corpus.db", help="SQLite corpus path; ignored by PostgreSQL"
    )
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("init-db", help="Initialize the development corpus")
    commands.add_parser("doctor", help="Validate provider configuration without network access")
    openai_check = commands.add_parser(
        "openai-check",
        help="Run an explicit live, billable OpenAI model contract check using environment credentials",
    )
    openai_check.add_argument(
        "--web-query",
        help="Also run one bounded hosted web-search request and report its source URLs",
    )

    serve = commands.add_parser("serve", help="Launch the local AgenticRAG workbench")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8787)
    serve.add_argument("--no-open", action="store_true", help="Do not open a browser window")
    serve.add_argument(
        "--allow-remote",
        action="store_true",
        help="Allow an explicit non-loopback bind; place it behind a trusted reverse proxy",
    )
    serve.add_argument(
        "--skills-root",
        type=Path,
        default=Path(os.environ.get("AGENTICRAG_SKILLS_PATH", ".agenticrag/skills")),
    )

    ingest = commands.add_parser("ingest", help="Ingest a local PDF, DOCX, Markdown, or TXT source")
    ingest.add_argument("path", type=Path)
    ingest.add_argument("--collection", required=True)
    ingest.add_argument("--scope", action="append", required=True)
    ingest.add_argument(
        "--ocr",
        choices=("auto", "never", "always"),
        default="auto",
        help="Use local OCR for low-text PDFs when available (default: auto)",
    )

    ask = commands.add_parser("ask", help="Run the fixed hybrid-RAG workflow")
    ask.add_argument("question")
    ask.add_argument("--collection", required=True)
    ask.add_argument("--scope", action="append", required=True)

    agent = commands.add_parser("agent", help="Run bounded agentic RAG with local skills and tools")
    agent.add_argument("question")
    agent.add_argument("--collection", required=True)
    agent.add_argument("--scope", action="append", required=True)
    agent.add_argument("--skill", action="append", default=[])
    agent.add_argument(
        "--skills-root",
        type=Path,
        default=Path(os.environ.get("AGENTICRAG_SKILLS_PATH", ".agenticrag/skills")),
    )
    agent.add_argument("--max-steps", type=int, default=8)
    agent.add_argument("--max-seconds", type=float, default=180.0)

    supervisor = commands.add_parser(
        "supervisor", help="Run the manager agent with bounded, non-recursive specialists"
    )
    supervisor.add_argument("question")
    supervisor.add_argument("--collection", required=True)
    supervisor.add_argument("--scope", action="append", required=True)
    supervisor.add_argument("--skill", action="append", default=[])
    supervisor.add_argument(
        "--skills-root",
        type=Path,
        default=Path(os.environ.get("AGENTICRAG_SKILLS_PATH", ".agenticrag/skills")),
    )
    supervisor.add_argument(
        "--allow-web",
        action="store_true",
        help="Permit the supervisor to send delegated web queries to hosted OpenAI",
    )

    source = commands.add_parser("show-source", help="Resolve an authorized immutable source version")
    source.add_argument("source_version_id")
    source.add_argument("--scope", action="append", required=True)

    compare = commands.add_parser(
        "compare", help="Run direct/fixed baselines and optionally bounded agentic RAG"
    )
    compare.add_argument("dataset", type=Path)
    compare.add_argument("--runs", type=Path, default=Path(".data/runs.jsonl"))
    compare.add_argument("--include-agent", action="store_true")
    compare.add_argument("--skill", action="append", default=[])
    compare.add_argument(
        "--skills-root",
        type=Path,
        default=Path(os.environ.get("AGENTICRAG_SKILLS_PATH", ".agenticrag/skills")),
    )
    compare.add_argument("--agent-max-steps", type=int, default=8)
    compare.add_argument("--agent-max-seconds", type=float, default=180.0)

    summarize = commands.add_parser("summarize", help="Score terminal records in a run journal")
    summarize.add_argument("dataset", type=Path)
    summarize.add_argument("--runs", type=Path, default=Path(".data/runs.jsonl"))

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "doctor":
            return _doctor()
        if args.command == "openai-check":
            return _openai_check(args.web_query)
        if args.command == "serve":
            from .server import serve

            serve(
                host=args.host,
                port=args.port,
                db_path=args.db,
                skills_root=args.skills_root,
                open_browser=not args.no_open,
                allow_remote=args.allow_remote,
            )
            return 0
        if args.command == "summarize":
            cases = _load_cases(args.dataset)
            summaries = summarize_experiments(JsonlRunJournal(args.runs).latest_records(), cases)
            _emit({"type": "summary", "groups": summaries})
            return 0
        store_config = load_store_config(args.db)
        with _build_store(store_config) as store:
            store.initialize()
            if args.command == "init-db":
                _emit({"status": "initialized", "store": store_config.public_dict()})
                return 0
            if args.command == "show-source":
                source = store.get_source(args.source_version_id, scopes=args.scope)
                _emit(asdict(source))
                return 0

            embedding = build_embedding_provider(load_provider_config(ProviderRole.EMBEDDING))
            if args.command == "ingest":
                ingestion = load_ingestion_config()
                file_parser = FileParser(
                    limits=IngestionLimits(
                        max_file_bytes=ingestion.max_file_bytes,
                        max_pages=ingestion.max_pages,
                        max_segments=ingestion.max_segments,
                    ),
                    ocr=args.ocr,
                    docling_artifacts_path=ingestion.docling_artifacts_path,
                )
                version = Ingestor(store, embedding, parser=file_parser).ingest_file(
                    args.path,
                    collection=args.collection,
                    scopes=args.scope,
                )
                _emit({"status": "published", "embedding_provider": embedding.label, **asdict(version)})
                return 0

            chat = build_chat_provider(load_provider_config(ProviderRole.CHAT))
            retriever = HybridRetriever(store, embedding)
            fixed = FixedRAGWorkflow(retriever, chat)
            if args.command == "ask":
                _emit(fixed.run(args.question, scopes=args.scope, collection=args.collection).to_dict())
                return 0
            if args.command == "agent":
                workflow = BoundedAgenticRAGWorkflow(
                    retriever,
                    chat,
                    store,
                    skill_registry=_skill_registry(args.skills_root),
                    selected_skills=args.skill,
                    config=AgentConfig(max_steps=args.max_steps, max_seconds=args.max_seconds),
                )
                _emit(
                    workflow.run(
                        args.question, scopes=args.scope, collection=args.collection
                    ).to_dict()
                )
                return 0
            if args.command == "supervisor":
                web_search = None
                if args.allow_web:
                    chat_config = load_provider_config(ProviderRole.CHAT)
                    if chat_config.kind != "openai":
                        raise ConfigurationError(
                            "--allow-web requires AGENTICRAG_CHAT_PROVIDER=openai"
                        )
                    web_search = OpenAIResponsesWebSearch(chat_config)
                workflow = SupervisorAgentWorkflow(
                    retriever,
                    chat,
                    store,
                    skill_registry=_skill_registry(args.skills_root),
                    selected_skills=args.skill,
                    web_search=web_search,
                )
                _emit(
                    workflow.run(
                        args.question, scopes=args.scope, collection=args.collection
                    ).to_dict()
                )
                return 0
            if args.command == "compare":
                cases = _load_cases(args.dataset)
                journal = JsonlRunJournal(args.runs)
                workflows = [DirectWorkflow(chat), fixed]
                if args.include_agent:
                    workflows.append(
                        BoundedAgenticRAGWorkflow(
                            retriever,
                            chat,
                            store,
                            skill_registry=_skill_registry(args.skills_root),
                            selected_skills=args.skill,
                            config=AgentConfig(
                                max_steps=args.agent_max_steps,
                                max_seconds=args.agent_max_seconds,
                            ),
                        )
                    )
                records = ExperimentRunner(journal).run(cases, workflows)
                for record in records:
                    _emit(record.to_dict())
                _emit({"type": "summary", "groups": summarize_experiments(records, cases)})
                return 0
    except (AgenticRAGError, OSError, ValueError, json.JSONDecodeError) as exc:
        _emit(
            {"status": "failed", "error_type": type(exc).__name__, "error": str(exc)},
            stream=sys.stderr,
        )
        return 2
    return 2


def _doctor() -> int:
    result: dict[str, Any] = {"status": "ready", "providers": {}}
    try:
        store_config = load_store_config()
        if store_config.backend == "postgres" and importlib.util.find_spec("psycopg") is None:
            raise ConfigurationError(
                "PostgreSQL is configured but psycopg is unavailable; install the 'postgres' extra"
            )
        result["store"] = {"status": "configured", **store_config.public_dict()}
    except ConfigurationError as exc:
        result["store"] = {"status": "invalid", "error": str(exc)}
        result["status"] = "invalid"
    try:
        skills_root = Path(os.environ.get("AGENTICRAG_SKILLS_PATH", ".agenticrag/skills"))
        skill_metadata = _skill_registry(skills_root).metadata()
        result["skills"] = {
            "status": "configured",
            "root": str(skills_root.expanduser().resolve()),
            "count": len(skill_metadata),
            "skills": list(skill_metadata),
        }
    except ConfigurationError as exc:
        result["skills"] = {"status": "invalid", "error": str(exc)}
        result["status"] = "invalid"
    for role in ProviderRole:
        try:
            config = load_provider_config(role)
            result["providers"][role.value] = {"status": "configured", **config.public_dict()}
        except ConfigurationError as exc:
            result["providers"][role.value] = {"status": "invalid", "error": str(exc)}
            result["status"] = "invalid"
    try:
        ingestion = load_ingestion_config()
        result["ingestion"] = {
            "status": "configured",
            "limits": {
                "max_file_bytes": ingestion.max_file_bytes,
                "max_pages": ingestion.max_pages,
                "max_segments": ingestion.max_segments,
            },
            "formats": parser_capabilities(ingestion.docling_artifacts_path),
        }
    except ConfigurationError as exc:
        result["ingestion"] = {"status": "invalid", "error": str(exc)}
        result["status"] = "invalid"
    _emit(result)
    return 0 if result["status"] == "ready" else 2


def _build_store(config: StoreConfig) -> SQLiteCorpusStore | PostgresCorpusStore:
    if config.backend == "sqlite":
        return SQLiteCorpusStore(config.sqlite_path)
    assert config.postgres_dsn is not None
    return PostgresCorpusStore.connect(config.postgres_dsn, config.objects_root)


def _skill_registry(root: Path) -> SkillRegistry:
    resolved = root.expanduser().resolve()
    standard = Path(".agents/skills").resolve()
    additional = (standard,) if resolved == Path(".agenticrag/skills").resolve() else ()
    return SkillRegistry(resolved, additional_roots=additional)


def _openai_check(web_query: str | None) -> int:
    config = load_provider_config(ProviderRole.CHAT)
    if config.kind != "openai":
        raise ConfigurationError(
            "openai-check requires AGENTICRAG_CHAT_PROVIDER=openai"
        )
    discovery = discover_models(config)
    chat = build_chat_provider(config)
    schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "answer": {"type": "integer"},
            "action": {"type": "string", "enum": ["calculate"]},
        },
        "required": ["answer", "action"],
        "additionalProperties": False,
    }
    raw = chat.complete(
        [
            ChatMessage("system", "Return the requested structured check only."),
            ChatMessage("user", "Compute 3 * 6 and choose the calculate action."),
        ],
        response_schema=schema,
        max_tokens=128,
        temperature=0.0,
    )
    try:
        contract = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ConfigurationError("OpenAI model returned invalid JSON for the contract check") from exc
    if contract != {"answer": 18, "action": "calculate"}:
        raise ConfigurationError("OpenAI model did not pass the bounded contract check")
    output: dict[str, Any] = {
        "status": "passed",
        "provider": config.public_dict(),
        "model_discovery": discovery,
        "checks": {"authentication": True, "model_access": True, "structured_output": True},
    }
    if web_query:
        result = OpenAIResponsesWebSearch(config, max_tool_calls=1).search(web_query)
        output["web_search"] = {
            "status": "passed",
            "source_count": len(result.sources),
            "sources": [asdict(source) for source in result.sources],
            "elapsed_ms": result.elapsed_ms,
        }
    _emit(output)
    return 0


def _load_cases(path: Path) -> list[ExperimentCase]:
    cases: list[ExperimentCase] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"Dataset line {line_number} must be a JSON object")
        try:
            raw_scopes = value["scopes"]
            if not isinstance(raw_scopes, list) or not raw_scopes or not all(
                isinstance(item, str) and item.strip() for item in raw_scopes
            ):
                raise TypeError("scopes must be a non-empty string array")
            case_id = value["id"]
            question = value["question"]
            collection = value["collection"]
            if not all(isinstance(item, str) and item.strip() for item in (case_id, question, collection)):
                raise TypeError("id, question, and collection must be non-empty strings")
            cases.append(
                ExperimentCase(
                    id=case_id,
                    question=question,
                    collection=collection,
                    scopes=tuple(raw_scopes),
                    answerable=_optional_bool(value, "answerable", line_number),
                    required_chunk_ids=_optional_string_array(
                        value, "required_chunk_ids", line_number
                    ),
                    expected_answer_contains=_optional_string_array(
                        value, "expected_answer_contains", line_number
                    ),
                )
            )
        except (KeyError, TypeError) as exc:
            raise ValueError(f"Dataset line {line_number} has an invalid case schema") from exc
    if not cases:
        raise ValueError("Experiment dataset contains no cases")
    return cases


def _optional_bool(value: dict[str, Any], key: str, line_number: int) -> bool | None:
    item = value.get(key)
    if item is None:
        return None
    if not isinstance(item, bool):
        raise ValueError(f"Dataset line {line_number} field {key} must be boolean or null")
    return item


def _optional_string_array(
    value: dict[str, Any], key: str, line_number: int
) -> tuple[str, ...]:
    items = value.get(key, [])
    if not isinstance(items, list) or not all(
        isinstance(item, str) and item.strip() for item in items
    ):
        raise ValueError(f"Dataset line {line_number} field {key} must be a string array")
    return tuple(items)


def _emit(value: Any, *, stream: Any = sys.stdout) -> None:
    print(json.dumps(value, ensure_ascii=False, sort_keys=True), file=stream)
