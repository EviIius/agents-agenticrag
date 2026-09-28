from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Protocol, Sequence

from .domain import Chunk, RankedChunk
from .providers.base import EmbeddingProvider
from .store import CorpusStore


class Reranker(Protocol):
    def score(self, query: str, chunks: Sequence[Chunk]) -> Sequence[float]: ...


@dataclass(frozen=True)
class RetrievalConfig:
    candidate_limit: int = 30
    result_limit: int = 8
    rrf_k: int = 60
    max_chunks_per_document: int = 3
    evidence_token_budget: int = 8_000

    def __post_init__(self) -> None:
        for name in (
            "candidate_limit",
            "result_limit",
            "rrf_k",
            "max_chunks_per_document",
            "evidence_token_budget",
        ):
            if getattr(self, name) <= 0:
                raise ValueError(f"{name} must be positive")


class HybridRetriever:
    def __init__(
        self,
        store: CorpusStore,
        embedding_provider: EmbeddingProvider,
        *,
        reranker: Reranker | None = None,
        config: RetrievalConfig | None = None,
    ) -> None:
        self.store = store
        self.embedding_provider = embedding_provider
        self.reranker = reranker
        self.config = config or RetrievalConfig()

    def retrieve(
        self,
        query: str,
        *,
        scopes: Sequence[str],
        collection: str,
    ) -> list[RankedChunk]:
        if not query.strip():
            raise ValueError("query cannot be empty")
        query_vectors = self.embedding_provider.embed([query])
        if len(query_vectors) != 1:
            raise ValueError("Embedding provider must return exactly one query vector")

        lexical = self.store.lexical_search(
            query,
            embedding_label=self.embedding_provider.label,
            scopes=scopes,
            collection=collection,
            limit=self.config.candidate_limit,
        )
        vector = self.store.vector_search(
            query_vectors[0],
            embedding_label=self.embedding_provider.label,
            scopes=scopes,
            collection=collection,
            limit=self.config.candidate_limit,
        )
        fused = self._fuse(lexical, vector)
        if self.reranker and fused:
            scores = self.reranker.score(query, [item.chunk for item in fused])
            if len(scores) != len(fused):
                raise ValueError("Reranker must return one score per candidate")
            fused = [
                RankedChunk(
                    chunk=item.chunk,
                    score=float(score),
                    lexical_rank=item.lexical_rank,
                    vector_rank=item.vector_rank,
                )
                for item, score in zip(fused, scores, strict=True)
            ]
            fused.sort(key=lambda item: (-item.score, item.chunk.id))
        return self._pack(fused)

    def _fuse(
        self,
        lexical: Sequence[RankedChunk],
        vector: Sequence[RankedChunk],
    ) -> list[RankedChunk]:
        chunks: dict[str, Chunk] = {}
        scores: dict[str, float] = defaultdict(float)
        lexical_ranks: dict[str, int] = {}
        vector_ranks: dict[str, int] = {}
        for rank, item in enumerate(lexical, start=1):
            chunks[item.chunk.id] = item.chunk
            lexical_rank = item.lexical_rank or rank
            lexical_ranks[item.chunk.id] = lexical_rank
            scores[item.chunk.id] += 1.0 / (self.config.rrf_k + lexical_rank)
        for rank, item in enumerate(vector, start=1):
            chunks[item.chunk.id] = item.chunk
            vector_rank = item.vector_rank or rank
            vector_ranks[item.chunk.id] = vector_rank
            scores[item.chunk.id] += 1.0 / (self.config.rrf_k + vector_rank)
        results = [
            RankedChunk(
                chunk=chunk,
                score=scores[chunk_id],
                lexical_rank=lexical_ranks.get(chunk_id),
                vector_rank=vector_ranks.get(chunk_id),
            )
            for chunk_id, chunk in chunks.items()
        ]
        results.sort(key=lambda item: (-item.score, item.chunk.id))
        return results

    def _pack(self, candidates: Sequence[RankedChunk]) -> list[RankedChunk]:
        selected: list[RankedChunk] = []
        per_document: dict[str, int] = defaultdict(int)
        used_tokens = 0
        lexical = [item for item in candidates if item.lexical_rank is not None]
        best_lexical = min(lexical, key=lambda item: item.lexical_rank or 0) if lexical else None
        ordered = (
            [best_lexical, *(item for item in candidates if item.chunk.id != best_lexical.chunk.id)]
            if best_lexical else candidates
        )
        for item in ordered:
            if len(selected) >= self.config.result_limit:
                break
            if per_document[item.chunk.document_id] >= self.config.max_chunks_per_document:
                continue
            estimated_tokens = max(1, (len(item.chunk.text) + 3) // 4)
            if used_tokens + estimated_tokens > self.config.evidence_token_budget:
                continue
            selected.append(item)
            per_document[item.chunk.document_id] += 1
            used_tokens += estimated_tokens
        return selected
