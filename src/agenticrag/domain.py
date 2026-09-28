from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


@dataclass(frozen=True)
class ProvenanceSpan:
    """A stable anchor from canonical parsed text back to the immutable source."""

    segment_id: str
    kind: str
    start_char: int
    end_char: int
    page_no: int | None = None
    source_start: int | None = None
    source_end: int | None = None
    bbox: tuple[float, float, float, float] | None = None
    section_path: tuple[str, ...] = ()
    table_id: str | None = None
    ocr: bool = False


@dataclass(frozen=True)
class SourceDraft:
    collection: str
    logical_path: str
    media_type: str
    text: str
    scopes: tuple[str, ...]
    original_bytes: bytes | None = None
    original_sha256: str | None = None
    parser_id: str = "text-v1"
    provenance: tuple[ProvenanceSpan, ...] = ()


@dataclass(frozen=True)
class ChunkDraft:
    ordinal: int
    text: str
    heading: str | None
    start_char: int
    end_char: int
    page_start: int | None = None
    page_end: int | None = None
    section_path: tuple[str, ...] = ()
    provenance: tuple[ProvenanceSpan, ...] = ()


@dataclass(frozen=True)
class SourceVersion:
    id: str
    document_id: str
    collection: str
    logical_path: str
    media_type: str
    sha256: str
    created_at: str
    scopes: tuple[str, ...]
    text: str | None = None
    parsed_sha256: str | None = None
    provenance_sha256: str | None = None
    parser_id: str = "text-v1"
    byte_size: int | None = None
    title: str | None = None


@dataclass(frozen=True)
class Chunk:
    id: str
    source_version_id: str
    document_id: str
    collection: str
    logical_path: str
    ordinal: int
    text: str
    heading: str | None
    start_char: int
    end_char: int
    page_start: int | None = None
    page_end: int | None = None
    section_path: tuple[str, ...] = ()
    provenance: tuple[ProvenanceSpan, ...] = ()


@dataclass(frozen=True)
class RankedChunk:
    chunk: Chunk
    score: float
    lexical_rank: int | None = None
    vector_rank: int | None = None


@dataclass(frozen=True)
class Citation:
    chunk_id: str
    source_version_id: str
    logical_path: str
    start_char: int
    end_char: int
    page_start: int | None = None
    page_end: int | None = None
    section_path: tuple[str, ...] = ()
    provenance: tuple[ProvenanceSpan, ...] = ()


EventKind = Literal[
    "retrieval_completed",
    "generation_completed",
    "answer_validated",
    "abstained",
    "failed",
    "plan_created",
    "skill_loaded",
    "tool_called",
    "review_completed",
    "validation_rejected",
    "budget_exhausted",
    "delegation_started",
    "delegation_completed",
    "web_search_completed",
    "synthesis_completed",
]


@dataclass(frozen=True)
class RunEvent:
    kind: EventKind
    detail: dict[str, Any] = field(default_factory=dict)
    at_ms: int | None = None


@dataclass(frozen=True)
class ExternalSource:
    id: str
    title: str
    url: str


@dataclass(frozen=True)
class DelegationTrace:
    id: str
    agent: str
    task: str
    status: str
    summary: str
    elapsed_ms: int
    citation_count: int = 0
    external_source_count: int = 0


@dataclass(frozen=True)
class RAGResult:
    workflow: str
    provider: str
    embedding_provider: str | None
    question: str
    answer: str
    abstained: bool
    citations: tuple[Citation, ...]
    evidence: tuple[RankedChunk, ...]
    events: tuple[RunEvent, ...]
    elapsed_ms: int
    external_sources: tuple[ExternalSource, ...] = ()
    delegations: tuple[DelegationTrace, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
