from __future__ import annotations

import hashlib
import json
import math
import re
import sqlite3
from dataclasses import asdict
from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

from .domain import Chunk, ChunkDraft, ProvenanceSpan, RankedChunk, SourceDraft, SourceVersion
from .errors import AuthorizationError, IngestionError


class CorpusStore(Protocol):
    def publish(
        self,
        source: SourceDraft,
        chunks: Sequence[ChunkDraft],
        vectors: Sequence[Sequence[float]],
        *,
        embedding_label: str,
        index_signature: str,
    ) -> SourceVersion: ...

    def lexical_search(
        self,
        query: str,
        *,
        embedding_label: str,
        scopes: Sequence[str],
        collection: str,
        limit: int,
    ) -> list[RankedChunk]: ...

    def vector_search(
        self,
        query_vector: Sequence[float],
        *,
        embedding_label: str,
        scopes: Sequence[str],
        collection: str,
        limit: int,
    ) -> list[RankedChunk]: ...

    def get_source(self, source_version_id: str, *, scopes: Sequence[str]) -> SourceVersion: ...

    def list_sources(
        self,
        *,
        scopes: Sequence[str],
        collection: str | None = None,
        limit: int = 200,
    ) -> list[SourceVersion]: ...


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    collection_id TEXT NOT NULL,
    logical_path TEXT NOT NULL,
    current_version_id TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(collection_id, logical_path)
);

CREATE TABLE IF NOT EXISTS source_versions (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(id),
    content_sha256 TEXT NOT NULL,
    parsed_sha256 TEXT NOT NULL,
    provenance_sha256 TEXT NOT NULL,
    scope_sha256 TEXT NOT NULL,
    media_type TEXT NOT NULL,
    parser_id TEXT NOT NULL,
    byte_size INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(document_id, content_sha256, parsed_sha256, provenance_sha256, parser_id, scope_sha256)
);

CREATE TABLE IF NOT EXISTS source_objects (
    sha256 TEXT PRIMARY KEY,
    content BLOB NOT NULL,
    byte_size INTEGER NOT NULL CHECK(byte_size >= 0)
);

CREATE TABLE IF NOT EXISTS source_scopes (
    source_version_id TEXT NOT NULL REFERENCES source_versions(id) ON DELETE CASCADE,
    scope TEXT NOT NULL,
    PRIMARY KEY(source_version_id, scope)
);

CREATE TABLE IF NOT EXISTS chunks (
    id TEXT PRIMARY KEY,
    source_version_id TEXT NOT NULL REFERENCES source_versions(id) ON DELETE CASCADE,
    ordinal INTEGER NOT NULL,
    heading TEXT,
    text TEXT NOT NULL,
    start_char INTEGER NOT NULL,
    end_char INTEGER NOT NULL,
    vector_json TEXT NOT NULL,
    page_start INTEGER,
    page_end INTEGER,
    section_path_json TEXT NOT NULL DEFAULT '[]',
    provenance_json TEXT NOT NULL DEFAULT '[]',
    UNIQUE(source_version_id, ordinal),
    CHECK(start_char >= 0 AND end_char > start_char)
);

CREATE VIRTUAL TABLE IF NOT EXISTS chunk_fts USING fts5(
    chunk_id UNINDEXED,
    heading,
    text,
    tokenize = 'unicode61'
);

CREATE INDEX IF NOT EXISTS idx_documents_collection ON documents(collection_id);
CREATE INDEX IF NOT EXISTS idx_source_versions_document ON source_versions(document_id);
CREATE INDEX IF NOT EXISTS idx_source_scopes_scope ON source_scopes(scope, source_version_id);
CREATE INDEX IF NOT EXISTS idx_chunks_source ON chunks(source_version_id, ordinal);
"""


class SQLiteCorpusStore:
    """Zero-service development store; PostgreSQL remains the production target."""

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")

    def initialize(self) -> None:
        self.connection.executescript(SCHEMA)
        self._ensure_column("source_versions", "parsed_sha256", "TEXT")
        self._ensure_column("source_versions", "provenance_sha256", "TEXT")
        self._ensure_column("source_versions", "parser_id", "TEXT NOT NULL DEFAULT 'text-v1'")
        self._ensure_column("source_versions", "byte_size", "INTEGER")
        self._ensure_column("chunks", "page_start", "INTEGER")
        self._ensure_column("chunks", "page_end", "INTEGER")
        self._ensure_column("chunks", "section_path_json", "TEXT NOT NULL DEFAULT '[]'")
        self._ensure_column("chunks", "provenance_json", "TEXT NOT NULL DEFAULT '[]'")
        self.connection.execute(
            "UPDATE source_versions SET parsed_sha256 = content_sha256 WHERE parsed_sha256 IS NULL"
        )
        self.connection.execute(
            "UPDATE source_versions SET provenance_sha256 = ? WHERE provenance_sha256 IS NULL",
            (hashlib.sha256(b"[]").hexdigest(),),
        )
        self.connection.execute(
            "UPDATE source_versions SET byte_size = length(CAST(content AS BLOB)) WHERE byte_size IS NULL"
        )
        self.connection.commit()

    def _ensure_column(self, table: str, column: str, declaration: str) -> None:
        columns = {row[1] for row in self.connection.execute(f"PRAGMA table_info({table})")}
        if column not in columns:
            self.connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {declaration}")

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> SQLiteCorpusStore:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def publish(
        self,
        source: SourceDraft,
        chunks: Sequence[ChunkDraft],
        vectors: Sequence[Sequence[float]],
        *,
        embedding_label: str,
        index_signature: str,
    ) -> SourceVersion:
        collection = _identifier(source.collection, "collection")
        scopes = _scopes(source.scopes)
        if not chunks or len(chunks) != len(vectors):
            raise IngestionError("Publishing requires one embedding vector per non-empty chunk")
        dimension = self._validate_vectors(vectors)
        original = source.original_bytes if source.original_bytes is not None else source.text.encode("utf-8")
        content_sha = hashlib.sha256(original).hexdigest()
        if source.original_sha256 is not None and source.original_sha256 != content_sha:
            raise IngestionError("Original source bytes do not match declared SHA-256")
        parsed_sha = hashlib.sha256(source.text.encode("utf-8")).hexdigest()
        provenance_sha = hashlib.sha256(
            json.dumps(
                [asdict(span) for span in source.provenance],
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        scope_sha = hashlib.sha256("\0".join(scopes).encode("utf-8")).hexdigest()
        document_id = _digest_id("doc", collection, source.logical_path)
        version_id = _digest_id(
            "version", document_id, content_sha, parsed_sha, provenance_sha, source.parser_id, scope_sha
        )

        with self.connection:
            self._require_index(dimension, embedding_label, index_signature)
            self.connection.execute(
                """INSERT INTO documents(id, collection_id, logical_path)
                   VALUES (?, ?, ?)
                   ON CONFLICT(collection_id, logical_path) DO NOTHING""",
                (document_id, collection, source.logical_path),
            )
            self.connection.execute(
                """INSERT INTO source_objects(sha256, content, byte_size)
                   VALUES (?, ?, ?) ON CONFLICT(sha256) DO NOTHING""",
                (content_sha, original, len(original)),
            )
            existing = self.connection.execute(
                "SELECT id FROM source_versions WHERE id = ?", (version_id,)
            ).fetchone()
            if existing is None:
                self.connection.execute(
                    """INSERT INTO source_versions(
                           id, document_id, content_sha256, parsed_sha256, provenance_sha256, scope_sha256,
                           media_type, parser_id, byte_size, content
                       ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        version_id, document_id, content_sha, parsed_sha, provenance_sha, scope_sha,
                        source.media_type, source.parser_id, len(original), source.text,
                    ),
                )
                self.connection.executemany(
                    "INSERT INTO source_scopes(source_version_id, scope) VALUES (?, ?)",
                    [(version_id, scope) for scope in scopes],
                )
                for draft, vector in zip(chunks, vectors, strict=True):
                    chunk_id = _digest_id("chunk", version_id, str(draft.ordinal))
                    self.connection.execute(
                        """INSERT INTO chunks(
                               id, source_version_id, ordinal, heading, text,
                               start_char, end_char, vector_json, page_start, page_end,
                               section_path_json, provenance_json
                           ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            chunk_id,
                            version_id,
                            draft.ordinal,
                            draft.heading,
                            draft.text,
                            draft.start_char,
                            draft.end_char,
                            json.dumps(list(vector), separators=(",", ":")),
                            draft.page_start,
                            draft.page_end,
                            json.dumps(draft.section_path, separators=(",", ":")),
                            json.dumps(
                                [asdict(span) for span in draft.provenance],
                                separators=(",", ":"),
                            ),
                        ),
                    )
                    self.connection.execute(
                        "INSERT INTO chunk_fts(chunk_id, heading, text) VALUES (?, ?, ?)",
                        (chunk_id, draft.heading or "", draft.text),
                    )
            self.connection.execute(
                "UPDATE documents SET current_version_id = ? WHERE id = ?",
                (version_id, document_id),
            )
        return self._source_by_id(version_id, include_text=False)

    def lexical_search(
        self,
        query: str,
        *,
        embedding_label: str,
        scopes: Sequence[str],
        collection: str,
        limit: int,
    ) -> list[RankedChunk]:
        allowed = _scopes(scopes)
        stored_label = self._metadata("embedding_provider_label")
        if stored_label is not None and stored_label != embedding_label:
            raise IngestionError(
                "Lexical retrieval index does not match the selected embedding provider; use a "
                "separately built corpus for provider comparisons"
            )
        tokens = re.findall(r"[\w-]+", query, flags=re.UNICODE)
        if not tokens or limit <= 0:
            return []
        fts_query = " OR ".join(f'"{token.replace(chr(34), chr(34) * 2)}"' for token in tokens[:32])
        scope_marks = ",".join("?" for _ in allowed)
        rows = self.connection.execute(
            f"""SELECT {self._chunk_columns()}, bm25(chunk_fts) AS raw_score
                FROM chunk_fts
                JOIN chunks c ON c.id = chunk_fts.chunk_id
                JOIN source_versions sv ON sv.id = c.source_version_id
                JOIN documents d ON d.id = sv.document_id
                WHERE chunk_fts MATCH ?
                  AND d.collection_id = ?
                  AND d.current_version_id = sv.id
                  AND EXISTS (
                      SELECT 1 FROM source_scopes ss
                      WHERE ss.source_version_id = sv.id AND ss.scope IN ({scope_marks})
                  )
                ORDER BY raw_score ASC, c.id ASC
                LIMIT ?""",
            (fts_query, collection, *allowed, limit),
        ).fetchall()
        return [
            RankedChunk(chunk=self._row_to_chunk(row), score=-float(row["raw_score"]), lexical_rank=i)
            for i, row in enumerate(rows, start=1)
        ]

    def vector_search(
        self,
        query_vector: Sequence[float],
        *,
        embedding_label: str,
        scopes: Sequence[str],
        collection: str,
        limit: int,
    ) -> list[RankedChunk]:
        allowed = _scopes(scopes)
        if limit <= 0:
            return []
        dimension = self._stored_dimension()
        if dimension is None:
            return []
        stored_label = self._metadata("embedding_provider_label")
        if stored_label != embedding_label:
            raise IngestionError(
                "Query embedding provider does not match this index generation; use a separately "
                "built corpus for provider comparisons"
            )
        if len(query_vector) != dimension:
            raise IngestionError(
                f"Query embedding dimension {len(query_vector)} does not match index dimension {dimension}"
            )
        try:
            query_is_finite = all(math.isfinite(float(value)) for value in query_vector)
        except (TypeError, ValueError) as exc:
            raise IngestionError("Query embedding must contain numeric values") from exc
        if not query_is_finite:
            raise IngestionError("Query embedding must contain finite values")
        scope_marks = ",".join("?" for _ in allowed)
        rows = self.connection.execute(
            f"""SELECT {self._chunk_columns()}, c.vector_json
                FROM chunks c
                JOIN source_versions sv ON sv.id = c.source_version_id
                JOIN documents d ON d.id = sv.document_id
                WHERE d.collection_id = ?
                  AND d.current_version_id = sv.id
                  AND EXISTS (
                      SELECT 1 FROM source_scopes ss
                      WHERE ss.source_version_id = sv.id AND ss.scope IN ({scope_marks})
                  )""",
            (collection, *allowed),
        ).fetchall()
        scored = [
            (self._row_to_chunk(row), _cosine(query_vector, json.loads(row["vector_json"])))
            for row in rows
        ]
        scored.sort(key=lambda item: (-item[1], item[0].id))
        return [
            RankedChunk(chunk=chunk, score=score, vector_rank=i)
            for i, (chunk, score) in enumerate(scored[:limit], start=1)
        ]

    def get_source(self, source_version_id: str, *, scopes: Sequence[str]) -> SourceVersion:
        allowed = _scopes(scopes)
        scope_marks = ",".join("?" for _ in allowed)
        row = self.connection.execute(
            f"""SELECT sv.*, d.collection_id, d.logical_path
                FROM source_versions sv
                JOIN documents d ON d.id = sv.document_id
                WHERE sv.id = ? AND EXISTS (
                    SELECT 1 FROM source_scopes ss
                    WHERE ss.source_version_id = sv.id AND ss.scope IN ({scope_marks})
                )""",
            (source_version_id, *allowed),
        ).fetchone()
        if row is None:
            raise AuthorizationError("Source version does not exist or is not authorized")
        return self._row_to_source(row, include_text=True)

    def list_sources(
        self,
        *,
        scopes: Sequence[str],
        collection: str | None = None,
        limit: int = 200,
    ) -> list[SourceVersion]:
        allowed = _scopes(scopes)
        if collection is not None:
            collection = _identifier(collection, "collection")
        if not 1 <= limit <= 1_000:
            raise IngestionError("Source list limit must be between 1 and 1000")
        scope_marks = ",".join("?" for _ in allowed)
        collection_clause = "" if collection is None else "AND d.collection_id = ?"
        parameters: tuple[object, ...] = (*allowed,)
        if collection is not None:
            parameters += (collection,)
        rows = self.connection.execute(
            f"""SELECT sv.*, d.collection_id, d.logical_path
                FROM source_versions sv
                JOIN documents d ON d.id = sv.document_id
                WHERE d.current_version_id = sv.id
                  AND EXISTS (
                      SELECT 1 FROM source_scopes ss
                      WHERE ss.source_version_id = sv.id AND ss.scope IN ({scope_marks})
                  )
                  {collection_clause}
                ORDER BY sv.created_at DESC, sv.id ASC
                LIMIT ?""",
            (*parameters, limit),
        ).fetchall()
        return [self._row_to_source(row, include_text=False) for row in rows]

    def _source_by_id(self, source_version_id: str, *, include_text: bool) -> SourceVersion:
        row = self.connection.execute(
            """SELECT sv.*, d.collection_id, d.logical_path
               FROM source_versions sv JOIN documents d ON d.id = sv.document_id
               WHERE sv.id = ?""",
            (source_version_id,),
        ).fetchone()
        if row is None:
            raise IngestionError("Published source version could not be reloaded")
        return self._row_to_source(row, include_text=include_text)

    def _row_to_source(self, row: sqlite3.Row, *, include_text: bool) -> SourceVersion:
        scopes = tuple(
            value[0]
            for value in self.connection.execute(
                "SELECT scope FROM source_scopes WHERE source_version_id = ? ORDER BY scope",
                (row["id"],),
            ).fetchall()
        )
        return SourceVersion(
            id=row["id"],
            document_id=row["document_id"],
            collection=row["collection_id"],
            logical_path=row["logical_path"],
            media_type=row["media_type"],
            sha256=row["content_sha256"],
            created_at=row["created_at"],
            scopes=scopes,
            text=row["content"] if include_text else None,
            parsed_sha256=row["parsed_sha256"],
            provenance_sha256=row["provenance_sha256"],
            parser_id=row["parser_id"],
            byte_size=row["byte_size"],
        )

    @staticmethod
    def _chunk_columns() -> str:
        return (
            "c.id, c.source_version_id, sv.document_id, d.collection_id, d.logical_path, "
            "c.ordinal, c.heading, c.text, c.start_char, c.end_char, c.page_start, "
            "c.page_end, c.section_path_json, c.provenance_json"
        )

    @staticmethod
    def _row_to_chunk(row: sqlite3.Row) -> Chunk:
        return Chunk(
            id=row["id"],
            source_version_id=row["source_version_id"],
            document_id=row["document_id"],
            collection=row["collection_id"],
            logical_path=row["logical_path"],
            ordinal=row["ordinal"],
            text=row["text"],
            heading=row["heading"],
            start_char=row["start_char"],
            end_char=row["end_char"],
            page_start=row["page_start"],
            page_end=row["page_end"],
            section_path=tuple(json.loads(row["section_path_json"])),
            provenance=tuple(
                ProvenanceSpan(**_restore_span(value))
                for value in json.loads(row["provenance_json"])
            ),
        )

    def _validate_vectors(self, vectors: Sequence[Sequence[float]]) -> int:
        dimension = len(vectors[0])
        if dimension <= 0:
            raise IngestionError("Embedding vectors cannot be empty")
        for vector in vectors:
            if len(vector) != dimension:
                raise IngestionError("All embedding vectors must use the same dimension")
            try:
                is_finite = all(math.isfinite(float(value)) for value in vector)
            except (TypeError, ValueError) as exc:
                raise IngestionError("Embedding vectors must contain numeric values") from exc
            if not is_finite:
                raise IngestionError("Embedding vectors must contain finite numbers")
        return dimension

    def _metadata(self, key: str) -> str | None:
        row = self.connection.execute("SELECT value FROM metadata WHERE key = ?", (key,)).fetchone()
        return None if row is None else str(row["value"])

    def _stored_dimension(self) -> int | None:
        value = self._metadata("embedding_dimension")
        return None if value is None else int(value)

    def _require_index(self, dimension: int, embedding_label: str, index_signature: str) -> None:
        if not embedding_label.strip():
            raise IngestionError("Embedding provider label cannot be empty")
        if not index_signature.strip():
            raise IngestionError("Index signature cannot be empty")
        current = self._stored_dimension()
        if current is None:
            self.connection.executemany(
                "INSERT INTO metadata(key, value) VALUES (?, ?)",
                (
                    ("embedding_dimension", str(dimension)),
                    ("embedding_provider_label", embedding_label),
                    ("index_signature", index_signature),
                ),
            )
        elif current != dimension:
            raise IngestionError(
                f"Embedding dimension changed from {current} to {dimension}; create a new index generation"
            )
        elif self._metadata("index_signature") != index_signature:
            raise IngestionError(
                "Embedding provider or chunking configuration changed; create a new index generation"
            )


def _identifier(value: str, name: str) -> str:
    normalized = value.strip()
    if not normalized or len(normalized) > 128:
        raise IngestionError(f"{name} must contain 1 to 128 characters")
    return normalized


def _scopes(values: Sequence[str]) -> tuple[str, ...]:
    scopes = tuple(sorted({_identifier(value, "scope") for value in values}))
    if not scopes:
        raise AuthorizationError("At least one authorization scope is required")
    return scopes


def _digest_id(kind: str, *parts: str) -> str:
    digest = hashlib.sha256("\0".join((kind, *parts)).encode("utf-8")).hexdigest()
    return f"{kind}_{digest[:32]}"


def _cosine(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise IngestionError("Stored embedding has an inconsistent dimension")
    dot = sum(float(a) * float(b) for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(float(value) ** 2 for value in left))
    right_norm = math.sqrt(sum(float(value) ** 2 for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def _restore_span(value: dict[str, object]) -> dict[str, object]:
    restored = dict(value)
    restored["section_path"] = tuple(restored.get("section_path", ()))
    bbox = restored.get("bbox")
    restored["bbox"] = None if bbox is None else tuple(bbox)  # type: ignore[arg-type]
    return restored
