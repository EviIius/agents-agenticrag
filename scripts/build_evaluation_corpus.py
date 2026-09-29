"""Build an isolated, frozen local corpus for the model comparison."""

from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path

from agenticrag.config import ProviderConfig, ProviderRole
from agenticrag.ingestion import Ingestor
from agenticrag.providers.openai_compatible import OpenAICompatibleEmbedding
from agenticrag.store import SQLiteCorpusStore


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=Path(".data/evaluation-corpus.db"))
    parser.add_argument("--embedding-model", default="qwen3-embedding:0.6b")
    parser.add_argument("--embedding-url", default="http://127.0.0.1:11434/v1")
    parser.add_argument("--embedding-runtime", default="ollama", choices=("ollama", "lm-studio"))
    parser.add_argument("--chat-model", default="gemma4:12b-mlx")
    parser.add_argument("--chat-url", default="http://127.0.0.1:11434/v1")
    parser.add_argument("--chat-runtime", default="ollama", choices=("ollama", "lm-studio"))
    parser.add_argument("--structured-output-mode", default="json_schema",
                        choices=("json_schema", "json_object", "prompt"))
    parser.add_argument("--source-dir", action="append", type=Path, default=[],
                        help="Recursively ingest documents from this directory; repeat for more roots")
    parser.add_argument("--manifest", type=Path,
                        help="JSONL with path and logical_path; repeat logical_path for document versions")
    parser.add_argument("--collection", default="evaluation")
    parser.add_argument("--scope", default="private")
    args = parser.parse_args()
    if args.db.exists():
        parser.error(f"{args.db} already exists; choose a new path to keep this corpus frozen")
    provider = OpenAICompatibleEmbedding(ProviderConfig(
        kind="local", role=ProviderRole.EMBEDDING,
        base_url=args.embedding_url, model=args.embedding_model,
        api_key=None, timeout_seconds=90, runtime=args.embedding_runtime,
    ))
    entries: list[tuple[Path, str]] = []
    if args.manifest:
        base = args.manifest.resolve().parent
        for line_number, line in enumerate(args.manifest.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            item = json.loads(line)
            if not isinstance(item, dict) or set(item) != {"path", "logical_path"}:
                parser.error(f"Manifest line {line_number} needs path and logical_path")
            if not all(isinstance(item[key], str) and item[key].strip() for key in item):
                parser.error(f"Manifest line {line_number} has an empty value")
            entries.append(((base / item["path"]).resolve(), item["logical_path"]))
    for root in args.source_dir:
        root = root.resolve()
        if not root.is_dir():
            parser.error(f"Source directory does not exist: {root}")
        entries.extend((path, path.relative_to(root).as_posix()) for path in sorted(root.rglob("*"))
                       if path.is_file() and path.suffix.lower() in {".txt", ".md", ".markdown", ".pdf", ".docx"})
    if not entries:
        root = Path(__file__).resolve().parents[1] / "examples"
        paths = sorted((root / "sample-corpus").glob("*.md")) + sorted((root / "evaluation-corpus").glob("*.md"))
        entries = [(path, path.as_posix()) for path in paths]
    if not entries:
        parser.error("No supported source files were found")
    with SQLiteCorpusStore(args.db) as store:
        store.initialize()
        ingestor = Ingestor(store, provider)
        for path, logical_path in entries:
            draft = ingestor.parser.parse(path, args.collection, (args.scope,))
            version = ingestor.ingest_source(replace(draft, logical_path=logical_path))
            print(f"{logical_path}: {version.id}")
    profile = {
        "version": 1,
        "providers": {
            "chat": {"runtime": args.chat_runtime, "base_url": args.chat_url, "model": args.chat_model,
                     "structured_output_mode": args.structured_output_mode, "timeout_seconds": 180},
            "embedding": {"runtime": args.embedding_runtime, "base_url": args.embedding_url,
                          "model": args.embedding_model, "structured_output_mode": "json_schema", "timeout_seconds": 90},
        },
    }
    args.db.with_suffix(".providers.json").write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")
    print(f"Frozen corpus: {args.db}")


if __name__ == "__main__":
    main()
