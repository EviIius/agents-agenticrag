from __future__ import annotations

import hashlib
import os
import tempfile
import unittest
import uuid
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from _bootstrap import SRC  # noqa: F401
from agenticrag.domain import ChunkDraft, SourceDraft
from agenticrag.errors import AuthorizationError
from agenticrag.objects import LocalObjectStore
from agenticrag.postgres_store import PostgresCorpusStore


class FakeResult:
    def __init__(self, rows: Any = None) -> None:
        if rows is None:
            self.rows: list[dict[str, Any]] = []
        elif isinstance(rows, list):
            self.rows = rows
        else:
            self.rows = [rows]

    def fetchone(self):  # type: ignore[no-untyped-def]
        return self.rows[0] if self.rows else None

    def fetchall(self):  # type: ignore[no-untyped-def]
        return self.rows


class FakeTransaction:
    def __enter__(self):  # type: ignore[no-untyped-def]
        return self

    def __exit__(self, *_):  # type: ignore[no-untyped-def]
        return False


class FakeBatchCursor(FakeTransaction):
    def __init__(self, connection: FakeConnection) -> None:
        self.connection = connection

    def executemany(self, query: str, rows: Sequence[Sequence[object]]) -> None:
        self.connection.batches.append((query, list(rows)))


class FakeConnection:
    def __init__(self, responses: Sequence[Any]) -> None:
        self.responses = list(responses)
        self.executions: list[tuple[str, object | None]] = []
        self.batches: list[tuple[str, list[Sequence[object]]]] = []
        self.closed = False

    def execute(self, query: str, params: object | None = None) -> FakeResult:
        self.executions.append((query, params))
        rows = self.responses.pop(0) if self.responses else None
        return FakeResult(rows)

    def cursor(self) -> FakeBatchCursor:
        return FakeBatchCursor(self)

    def transaction(self) -> FakeTransaction:
        return FakeTransaction()

    def close(self) -> None:
        self.closed = True


class PostgresContractTests(unittest.TestCase):
    def test_packaged_and_repository_migrations_match(self) -> None:
        root = Path(__file__).resolve().parents[1]
        packaged = (root / "src/agenticrag/sql/001_initial.sql").read_bytes()
        repository = (root / "migrations/postgres/001_initial.sql").read_bytes()
        self.assertEqual(packaged, repository)
        schema = packaged.decode("utf-8")
        self.assertIn("parsed_sha256", schema)
        self.assertIn("parsed_content", schema)
        self.assertIn("provenance jsonb", schema)

    def test_publish_writes_version_scopes_chunks_and_object_provenance(self) -> None:
        text = "Atlas has 64 GB of memory."
        sha256 = hashlib.sha256(text.encode()).hexdigest()
        object_path = f"{sha256[:2]}/{sha256[2:4]}/{sha256}.txt"
        source_row = {
            "id": "version-result",
            "document_id": "doc-result",
            "collection_id": "private",
            "logical_path": "/corpus/atlas.md",
            "media_type": "text/markdown",
            "content_sha256": sha256,
            "object_path": object_path,
            "ingested_at": "2026-09-12T12:00:00+00:00",
        }
        responses = [
            None,
            None,
            None,
            None,
            None,
            {"count": 0},
            None,
            source_row,
            [{"scope": "owner"}],
        ]
        with tempfile.TemporaryDirectory() as directory:
            connection = FakeConnection(responses)
            store = PostgresCorpusStore(connection, LocalObjectStore(directory))
            version = store.publish(
                SourceDraft("private", "/corpus/atlas.md", "text/markdown", text, ("owner",)),
                [ChunkDraft(0, text, "Atlas", 0, len(text))],
                [[1.0, 2.0, 3.0]],
                embedding_label="local:embed@127.0.0.1:8081/v1",
                index_signature="local:embed@127.0.0.1:8081/v1|text-chunker-v1:1200:200",
            )
            self.assertEqual(version.sha256, sha256)
            self.assertTrue(Path(directory).joinpath(*object_path.split("/")).is_file())
            self.assertEqual(len(connection.batches), 2)
            self.assertIn("%s::vector", connection.batches[1][0])
            self.assertIn("%s::jsonb", connection.batches[1][0])

    def test_lexical_query_contains_all_authorization_and_generation_predicates(self) -> None:
        chunk = _chunk_row(raw_score=0.5)
        connection = FakeConnection(
            [{"id": "index-1", "signature": "sig", "dimensions": 3}, [chunk]]
        )
        with tempfile.TemporaryDirectory() as directory:
            store = PostgresCorpusStore(connection, LocalObjectStore(directory))
            hits = store.lexical_search(
                "Atlas memory",
                embedding_label="local:embed",
                scopes=("owner",),
                collection="private",
                limit=20,
            )
        query = connection.executions[1][0]
        self.assertEqual(len(hits), 1)
        self.assertIn("source_scopes", query)
        self.assertIn("d.current_version_id = sv.id", query)
        self.assertIn("c.index_generation_id = %s", query)
        self.assertIn("d.collection_id = %s", query)

    def test_vector_query_uses_exact_cosine_under_authorization_predicates(self) -> None:
        chunk = _chunk_row(similarity=0.9)
        connection = FakeConnection(
            [{"id": "index-1", "signature": "sig", "dimensions": 3}, [chunk]]
        )
        with tempfile.TemporaryDirectory() as directory:
            store = PostgresCorpusStore(connection, LocalObjectStore(directory))
            hits = store.vector_search(
                [1.0, 2.0, 3.0],
                embedding_label="local:embed",
                scopes=("owner",),
                collection="private",
                limit=20,
            )
        query = connection.executions[1][0]
        self.assertEqual(hits[0].score, 0.9)
        self.assertIn("<=> %s::vector", query)
        self.assertIn("source_scopes", query)
        self.assertNotIn("hnsw", query.lower())

    def test_empty_database_search_returns_no_evidence(self) -> None:
        connection = FakeConnection([None, {"count": 0}])
        with tempfile.TemporaryDirectory() as directory:
            store = PostgresCorpusStore(connection, LocalObjectStore(directory))
            self.assertEqual(
                store.lexical_search(
                    "Atlas",
                    embedding_label="local:embed",
                    scopes=("owner",),
                    collection="private",
                    limit=20,
                ),
                [],
            )

    def test_unauthorized_source_never_reaches_object_store(self) -> None:
        connection = FakeConnection([None])

        class FailingObjects:
            def get_text(self, *args):  # type: ignore[no-untyped-def]
                raise AssertionError("object store must not be read")

        store = PostgresCorpusStore(connection, FailingObjects())  # type: ignore[arg-type]
        with self.assertRaises(AuthorizationError):
            store.get_source("version-secret", scopes=("guest",))


def _chunk_row(**scores: float) -> dict[str, Any]:
    return {
        "id": "chunk-1",
        "source_version_id": "version-1",
        "document_id": "doc-1",
        "collection_id": "private",
        "logical_path": "/corpus/atlas.md",
        "ordinal": 0,
        "heading": "Atlas",
        "text": "Atlas has 64 GB of memory.",
        "start_char": 0,
        "end_char": 27,
        **scores,
    }


@unittest.skipUnless(
    os.environ.get("AGENTICRAG_TEST_POSTGRES_DSN"),
    "set AGENTICRAG_TEST_POSTGRES_DSN for live pgvector integration",
)
class PostgresLiveIntegrationTests(unittest.TestCase):
    def test_publish_search_and_authorized_source_round_trip(self) -> None:
        import psycopg
        from psycopg import sql
        from psycopg.rows import dict_row

        dsn = os.environ["AGENTICRAG_TEST_POSTGRES_DSN"]
        schema = f"agenticrag_test_{uuid.uuid4().hex}"
        with tempfile.TemporaryDirectory() as directory:
            connection = psycopg.connect(dsn, row_factory=dict_row)
            try:
                connection.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
                connection.execute(
                    sql.SQL("SET search_path TO {}, public").format(sql.Identifier(schema))
                )
                store = PostgresCorpusStore(connection, LocalObjectStore(directory))
                store.initialize()
                text = "Atlas has 64 GB of memory."
                version = store.publish(
                    SourceDraft("private", "/corpus/atlas.md", "text/markdown", text, ("owner",)),
                    [ChunkDraft(0, text, "Atlas", 0, len(text))],
                    [[1.0, 2.0, 3.0]],
                    embedding_label="test:embed",
                    index_signature="test:embed|chunker-v1",
                )
                lexical = store.lexical_search(
                    "Atlas memory",
                    embedding_label="test:embed",
                    scopes=("owner",),
                    collection="private",
                    limit=10,
                )
                vector = store.vector_search(
                    [1.0, 2.0, 3.0],
                    embedding_label="test:embed",
                    scopes=("owner",),
                    collection="private",
                    limit=10,
                )
                self.assertTrue(lexical)
                self.assertTrue(vector)
                self.assertEqual(store.get_source(version.id, scopes=("owner",)).text, text)
            finally:
                connection.rollback()
                connection.close()


if __name__ == "__main__":
    unittest.main()
