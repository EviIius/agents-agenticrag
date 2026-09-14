from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict
from functools import wraps
from collections.abc import Mapping, Sequence
from datetime import datetime
from importlib import resources
from pathlib import Path
from typing import Any

from .domain import Chunk, ChunkDraft, ProvenanceSpan, RankedChunk, SourceDraft, SourceVersion
from .errors import AgenticRAGError, AuthorizationError, ConfigurationError, IngestionError, StorageError
from .objects import LocalObjectStore
from .store import _digest_id, _identifier, _scopes


def _postgres_operation(action: str):  # type: ignore[no-untyped-def]
    def decorate(function):  # type: ignore[no-untyped-def]
        @wraps(function)
        def wrapped(*args, **kwargs):  # type: ignore[no-untyped-def]
            try:
                return function(*args, **kwargs)
            except AgenticRAGError:
                raise
            except Exception as exc:
                raise StorageError(f"PostgreSQL {action} failed") from exc

        return wrapped

    return decorate


class PostgresCorpusStore:
    """PostgreSQL/pgvector implementation of the corpus contract."""

    def __init__(self, connection: Any, object_store: LocalObjectStore) -> None:
        self.connection = connection
        self.objects = object_store

    @classmethod
    def connect(cls, dsn: str, objects_root: str | Path) -> PostgresCorpusStore:
        if not dsn.strip():
            raise ConfigurationError("AGENTICRAG_POSTGRES_DSN is required for the PostgreSQL store")
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError as exc:
            raise ConfigurationError(
                "PostgreSQL support requires the 'postgres' extra: pip install -e '.[postgres]'"
            ) from exc
        try:
            connection = psycopg.connect(dsn, row_factory=dict_row)
        except Exception as exc:
            raise ConfigurationError("Could not connect to the configured PostgreSQL store") from exc
        return cls(connection, LocalObjectStore(objects_root))

    @_postgres_operation("initialization")
    def initialize(self) -> None:
        schema = resources.files("agenticrag.sql").joinpath("001_initial.sql").read_text("utf-8")
        with self.connection.transaction():
            self.connection.execute(schema)

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> PostgresCorpusStore:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    @_postgres_operation("publication")
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
        numeric_vectors, dimension = _validated_vectors(vectors, expected_count=len(chunks))
        original = source.original_bytes if source.original_bytes is not None else source.text.encode("utf-8")
        suffix = ".txt" if source.original_bytes is None else Path(source.logical_path).suffix.lower()
        suffix = suffix if suffix and suffix[1:].isalnum() else ".bin"
        object_path, content_sha = self.objects.put_bytes(original, suffix=suffix)
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

        with self.connection.transaction():
            generation_id = self._ensure_generation(
                embedding_label=embedding_label,
                index_signature=index_signature,
                dimension=dimension,
            )
            self.connection.execute(
                """INSERT INTO documents(id, collection_id, logical_path)
                   VALUES (%s, %s, %s)
                   ON CONFLICT(collection_id, logical_path) DO NOTHING""",
                (document_id, collection, source.logical_path),
            )
            row = self.connection.execute(
                "SELECT id FROM source_versions WHERE id = %s", (version_id,)
            ).fetchone()
            if row is None:
                self.connection.execute(
                    """INSERT INTO source_versions(
                           id, document_id, content_sha256, parsed_sha256, provenance_sha256, scope_sha256,
                           media_type, object_path, parser_id, byte_size, parsed_content
                       ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (
                        version_id,
                        document_id,
                        content_sha,
                        parsed_sha,
                        provenance_sha,
                        scope_sha,
                        source.media_type,
                        object_path,
                        source.parser_id,
                        len(original),
                        source.text,
                    ),
                )
                self._executemany(
                    """INSERT INTO source_scopes(source_version_id, scope)
                       VALUES (%s, %s) ON CONFLICT DO NOTHING""",
                    [(version_id, scope) for scope in scopes],
                )

            existing_chunks = self.connection.execute(
                """SELECT count(*) AS count FROM chunks
                   WHERE source_version_id = %s AND index_generation_id = %s""",
                (version_id, generation_id),
            ).fetchone()
            existing_count = int(existing_chunks["count"])
            if existing_count not in {0, len(chunks)}:
                raise IngestionError("Index generation contains a partial source publication")
            if existing_count == 0:
                rows = []
                for draft, vector in zip(chunks, numeric_vectors, strict=True):
                    chunk_id = _digest_id(
                        "chunk", version_id, generation_id, str(draft.ordinal)
                    )
                    rows.append(
                        (
                            chunk_id,
                            version_id,
                            generation_id,
                            draft.ordinal,
                            draft.heading,
                            draft.text,
                            draft.start_char,
                            draft.end_char,
                            draft.page_start,
                            draft.page_end,
                            json.dumps(draft.section_path, separators=(",", ":")),
                            json.dumps(
                                [asdict(span) for span in draft.provenance],
                                separators=(",", ":"),
                            ),
                            _vector_literal(vector),
                        )
                    )
                self._executemany(
                    """INSERT INTO chunks(
                           id, source_version_id, index_generation_id, ordinal, heading,
                           content, start_char, end_char, page_start, page_end,
                           section_path, provenance, embedding
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                  %s::jsonb, %s::jsonb, %s::vector)""",
                    rows,
                )
            self.connection.execute(
                "UPDATE documents SET current_version_id = %s WHERE id = %s",
                (version_id, document_id),
            )
        return self._source_by_id(version_id, include_text=False)

    def _executemany(self, query: str, rows: Sequence[Sequence[object]]) -> None:
        with self.connection.cursor() as cursor:
            cursor.executemany(query, rows)

    @_postgres_operation("lexical search")
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
        if not query.strip() or limit <= 0:
            return []
        generation = self._generation_for_label(embedding_label)
        if generation is None:
            return []
        rows = self.connection.execute(
            f"""WITH query AS (SELECT plainto_tsquery('simple', %s) AS value)
                SELECT {self._chunk_columns()},
                       ts_rank_cd(c.search_document, query.value) AS raw_score
                FROM chunks c
                JOIN source_versions sv ON sv.id = c.source_version_id
                JOIN documents d ON d.id = sv.document_id
                CROSS JOIN query
                WHERE c.search_document @@ query.value
                  AND c.index_generation_id = %s
                  AND d.collection_id = %s
                  AND d.current_version_id = sv.id
                  AND EXISTS (
                      SELECT 1 FROM source_scopes ss
                      WHERE ss.source_version_id = sv.id AND ss.scope = ANY(%s)
                  )
                ORDER BY raw_score DESC, c.id ASC
                LIMIT %s""",
            (query, generation["id"], collection, list(allowed), limit),
        ).fetchall()
        return [
            RankedChunk(
                chunk=self._row_to_chunk(row),
                score=float(row["raw_score"]),
                lexical_rank=rank,
            )
            for rank, row in enumerate(rows, start=1)
        ]

    @_postgres_operation("vector search")
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
        generation = self._generation_for_label(embedding_label)
        if generation is None:
            return []
        vector, dimension = _validated_vector(query_vector)
        if dimension != int(generation["dimensions"]):
            raise IngestionError(
                f"Query embedding dimension {dimension} does not match index dimension "
                f"{generation['dimensions']}"
            )
        literal = _vector_literal(vector)
        rows = self.connection.execute(
            f"""SELECT {self._chunk_columns()},
                       1 - (c.embedding <=> %s::vector) AS similarity
                FROM chunks c
                JOIN source_versions sv ON sv.id = c.source_version_id
                JOIN documents d ON d.id = sv.document_id
                WHERE c.index_generation_id = %s
                  AND d.collection_id = %s
                  AND d.current_version_id = sv.id
                  AND EXISTS (
                      SELECT 1 FROM source_scopes ss
                      WHERE ss.source_version_id = sv.id AND ss.scope = ANY(%s)
                  )
                ORDER BY c.embedding <=> %s::vector, c.id ASC
                LIMIT %s""",
            (literal, generation["id"], collection, list(allowed), literal, limit),
        ).fetchall()
        return [
            RankedChunk(
                chunk=self._row_to_chunk(row),
                score=float(row["similarity"]),
                vector_rank=rank,
            )
            for rank, row in enumerate(rows, start=1)
        ]

    @_postgres_operation("source fetch")
    def get_source(self, source_version_id: str, *, scopes: Sequence[str]) -> SourceVersion:
        allowed = _scopes(scopes)
        row = self.connection.execute(
            """SELECT sv.*, d.collection_id, d.logical_path
               FROM source_versions sv
               JOIN documents d ON d.id = sv.document_id
               WHERE sv.id = %s AND EXISTS (
                   SELECT 1 FROM source_scopes ss
                   WHERE ss.source_version_id = sv.id AND ss.scope = ANY(%s)
               )""",
            (source_version_id, list(allowed)),
        ).fetchone()
        if row is None:
            raise AuthorizationError("Source version does not exist or is not authorized")
        return self._row_to_source(row, include_text=True)

    @_postgres_operation("source listing")
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
        collection_clause = "" if collection is None else "AND d.collection_id = %s"
        parameters: list[object] = [list(allowed)]
        if collection is not None:
            parameters.append(collection)
        parameters.append(limit)
        rows = self.connection.execute(
            f"""SELECT sv.*, d.collection_id, d.logical_path
                FROM source_versions sv
                JOIN documents d ON d.id = sv.document_id
                WHERE d.current_version_id = sv.id
                  AND EXISTS (
                      SELECT 1 FROM source_scopes ss
                      WHERE ss.source_version_id = sv.id AND ss.scope = ANY(%s)
                  )
                  {collection_clause}
                ORDER BY sv.ingested_at DESC, sv.id ASC
                LIMIT %s""",
            tuple(parameters),
        ).fetchall()
        return [self._row_to_source(row, include_text=False) for row in rows]

    def _ensure_generation(
        self,
        *,
        embedding_label: str,
        index_signature: str,
        dimension: int,
    ) -> str:
        if not embedding_label.strip() or not index_signature.strip():
            raise IngestionError("Embedding label and index signature cannot be empty")
        existing = self.connection.execute(
            """SELECT id, signature, embedding_provider_label, dimensions
               FROM index_generations WHERE embedding_provider_label = %s""",
            (embedding_label,),
        ).fetchone()
        if existing is not None:
            if existing["signature"] != index_signature or int(existing["dimensions"]) != dimension:
                raise IngestionError(
                    "Embedding or chunking configuration changed; create a new database or schema "
                    "for that index generation"
                )
            return str(existing["id"])
        generation_id = _digest_id("index", index_signature)
        self.connection.execute(
            """INSERT INTO index_generations(
                   id, signature, embedding_provider_label, dimensions
               ) VALUES (%s, %s, %s, %s)""",
            (generation_id, index_signature, embedding_label, dimension),
        )
        return generation_id

    def _generation_for_label(self, embedding_label: str) -> Mapping[str, Any] | None:
        row = self.connection.execute(
            """SELECT id, signature, embedding_provider_label, dimensions
               FROM index_generations WHERE embedding_provider_label = %s""",
            (embedding_label,),
        ).fetchone()
        if row is None:
            count = self.connection.execute(
                "SELECT count(*) AS count FROM index_generations"
            ).fetchone()
            if int(count["count"]) == 0:
                return None
            raise IngestionError(
                "No index generation matches the selected embedding provider; ingest the corpus "
                "with that provider first"
            )
        return row

    def _source_by_id(self, source_version_id: str, *, include_text: bool) -> SourceVersion:
        row = self.connection.execute(
            """SELECT sv.*, d.collection_id, d.logical_path
               FROM source_versions sv JOIN documents d ON d.id = sv.document_id
               WHERE sv.id = %s""",
            (source_version_id,),
        ).fetchone()
        if row is None:
            raise IngestionError("Published source version could not be reloaded")
        return self._row_to_source(row, include_text=include_text)

    def _row_to_source(self, row: Mapping[str, Any], *, include_text: bool) -> SourceVersion:
        scopes = tuple(
            str(value["scope"])
            for value in self.connection.execute(
                """SELECT scope FROM source_scopes
                   WHERE source_version_id = %s ORDER BY scope""",
                (row["id"],),
            ).fetchall()
        )
        text = None
        if include_text:
            parsed_content = row.get("parsed_content")
            text = (
                self.objects.get_text(str(row["object_path"]), str(row["content_sha256"]))
                if parsed_content is None
                else str(parsed_content)
            )
        return SourceVersion(
            id=str(row["id"]),
            document_id=str(row["document_id"]),
            collection=str(row["collection_id"]),
            logical_path=str(row["logical_path"]),
            media_type=str(row["media_type"]),
            sha256=str(row["content_sha256"]),
            created_at=_timestamp(row["ingested_at"]),
            scopes=scopes,
            text=text,
            parsed_sha256=str(row.get("parsed_sha256", row["content_sha256"])),
            provenance_sha256=str(
                row.get(
                    "provenance_sha256",
                    "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
                )
            ),
            parser_id=str(row.get("parser_id", "text-v1")),
            byte_size=None if row.get("byte_size") is None else int(row["byte_size"]),
        )

    @staticmethod
    def _chunk_columns() -> str:
        return (
            "c.id, c.source_version_id, sv.document_id, d.collection_id, d.logical_path, "
            "c.ordinal, c.heading, c.content AS text, c.start_char, c.end_char, "
            "c.page_start, c.page_end, c.section_path, c.provenance"
        )

    @staticmethod
    def _row_to_chunk(row: Mapping[str, Any]) -> Chunk:
        return Chunk(
            id=str(row["id"]),
            source_version_id=str(row["source_version_id"]),
            document_id=str(row["document_id"]),
            collection=str(row["collection_id"]),
            logical_path=str(row["logical_path"]),
            ordinal=int(row["ordinal"]),
            text=str(row["text"]),
            heading=None if row["heading"] is None else str(row["heading"]),
            start_char=int(row["start_char"]),
            end_char=int(row["end_char"]),
            page_start=None if row.get("page_start") is None else int(row["page_start"]),
            page_end=None if row.get("page_end") is None else int(row["page_end"]),
            section_path=tuple(row.get("section_path", ())),
            provenance=tuple(
                ProvenanceSpan(**_restore_span(value)) for value in row.get("provenance", ())
            ),
        )


def _validated_vectors(
    vectors: Sequence[Sequence[float]], *, expected_count: int
) -> tuple[list[list[float]], int]:
    if expected_count <= 0 or len(vectors) != expected_count:
        raise IngestionError("Publishing requires one embedding vector per non-empty chunk")
    normalized: list[list[float]] = []
    dimension: int | None = None
    for vector in vectors:
        values, current_dimension = _validated_vector(vector)
        dimension = current_dimension if dimension is None else dimension
        if current_dimension != dimension:
            raise IngestionError("All embedding vectors must use the same dimension")
        normalized.append(values)
    assert dimension is not None
    return normalized, dimension


def _validated_vector(vector: Sequence[float]) -> tuple[list[float], int]:
    if not vector:
        raise IngestionError("Embedding vectors cannot be empty")
    try:
        values = [float(value) for value in vector]
    except (TypeError, ValueError) as exc:
        raise IngestionError("Embedding vectors must contain numeric values") from exc
    if not all(math.isfinite(value) for value in values):
        raise IngestionError("Embedding vectors must contain finite numbers")
    return values, len(values)


def _vector_literal(vector: Sequence[float]) -> str:
    return "[" + ",".join(format(float(value), ".9g") for value in vector) + "]"


def _timestamp(value: object) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _restore_span(value: Mapping[str, Any]) -> dict[str, object]:
    restored = dict(value)
    restored["section_path"] = tuple(restored.get("section_path", ()))
    bbox = restored.get("bbox")
    restored["bbox"] = None if bbox is None else tuple(bbox)  # type: ignore[arg-type]
    return restored
