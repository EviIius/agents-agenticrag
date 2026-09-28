"""Build an isolated, frozen local corpus for the model comparison."""

from __future__ import annotations

import argparse
import json
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
    parser.add_argument("--chat-model", default="gemma4:12b-mlx")
    args = parser.parse_args()
    if args.db.exists():
        parser.error(f"{args.db} already exists; choose a new path to keep this corpus frozen")
    provider = OpenAICompatibleEmbedding(ProviderConfig(
        kind="local", role=ProviderRole.EMBEDDING,
        base_url=args.embedding_url, model=args.embedding_model,
        api_key=None, timeout_seconds=90, runtime="ollama",
    ))
    root = Path(__file__).resolve().parents[1] / "examples"
    paths = sorted((root / "sample-corpus").glob("*.md")) + sorted((root / "evaluation-corpus").glob("*.md"))
    with SQLiteCorpusStore(args.db) as store:
        store.initialize()
        ingestor = Ingestor(store, provider)
        for path in paths:
            version = ingestor.ingest_file(path, "evaluation", ("private",))
            print(f"{path.name}: {version.id}")
    profile = {
        "version": 1,
        "providers": {
            "chat": {"runtime": "ollama", "base_url": "http://127.0.0.1:11434/v1", "model": args.chat_model, "structured_output_mode": "json_object", "timeout_seconds": 180},
            "embedding": {"runtime": "ollama", "base_url": args.embedding_url, "model": args.embedding_model, "structured_output_mode": "json_schema", "timeout_seconds": 90},
        },
    }
    args.db.with_suffix(".providers.json").write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")
    print(f"Frozen corpus: {args.db}")


if __name__ == "__main__":
    main()
