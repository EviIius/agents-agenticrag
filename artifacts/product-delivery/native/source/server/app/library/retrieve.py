"""Scoped keyword/vector candidates, deterministic RRF and bounded source selection."""

import asyncio
import math
import re
from array import array
from time import monotonic
from typing import Any

from ..db.connections import now
from ..db.core import Store
from ..providers.base import Adapter
from ..schemas import LibraryInfo, LibraryScope, Passage, Source
from ..search.rank import rrf, select
from .prompt import sanitize


async def retrieve(
    store: Store,
    adapter: Adapter,
    settings: dict[str, Any],
    query: str,
    scope: LibraryScope | None,
    budget_tokens: int,
    ratio: float,
) -> tuple[list[Source], LibraryInfo]:
    choice = settings["library.embedding"]
    start = monotonic()
    vectors = await asyncio.wait_for(
        adapter.embed(choice["model_id"], [settings["library.query_prefix"] + query]), 60
    )
    if (
        len(vectors) != 1
        or len(vectors[0]) != choice["dim"]
        or any(not math.isfinite(v) for v in vectors[0])
        or not any(vectors[0])
    ):
        raise ValueError("Invalid query embedding")
    packed = array("f", vectors[0])
    if any(not math.isfinite(v) for v in packed):
        raise ValueError("Invalid query embedding")
    info = LibraryInfo(
        status="used", queries=[query], timings={"embed": (monotonic() - start) * 1000}
    )
    sources = await candidates(
        store, packed.tobytes(), query, scope, budget_tokens, settings["library.max_sources"], ratio
    )
    info.timings["retrieve"] = (monotonic() - start) * 1000 - info.timings["embed"]
    info.source_count = len(sources)
    info.passage_count = sum(len(s.passages) for s in sources)
    return sources, info


async def candidates(
    store: Store,
    vector: bytes,
    query: str,
    scope: LibraryScope | None,
    budget: int,
    maximum: int,
    ratio: float,
) -> list[Source]:
    where = "d.status='ready'"
    params: tuple[object, ...] = ()
    if scope is not None:
        ids = list(dict.fromkeys(scope.collection_ids))
        if not ids:
            return []
        where += " AND d.collection_id IN (" + ",".join("?" for _ in ids) + ")"
        params = tuple(ids)
    eligible = (
        "SELECT c.id FROM library_chunks c JOIN library_documents d ON d.id=c.document_id WHERE "
        + where
    )
    lexical: list[dict[str, Any]] = []
    terms = list(dict.fromkeys(re.findall(r"\w+", query)))
    if terms:
        match = " OR ".join('"' + term + '"' for term in terms)
        lexical = await store.rows(
            "SELECT library_chunks_fts.rowid AS id,bm25(library_chunks_fts) AS score "
            "FROM library_chunks_fts CROSS JOIN library_chunks c "
            "ON c.id=library_chunks_fts.rowid CROSS JOIN library_documents d "
            "ON d.id=c.document_id WHERE library_chunks_fts MATCH ? AND "
            + where
            + " ORDER BY score,library_chunks_fts.rowid LIMIT 40",
            (match, *params),
        )
    semantic = await nearest(store, vector, eligible, params)
    rankings = [
        [str(row["id"]) for row in lexical],
        [str(row["id"]) for row in sorted(semantic, key=lambda r: (r["distance"], r["id"]))],
    ]
    fused = rrf(rankings)
    if not fused:
        return []
    keys = sorted(fused, key=lambda k: (-fused[k], int(k)))
    rows = await store.rows(
        "SELECT c.*,d.filename FROM library_chunks c JOIN library_documents d "
        "ON d.id=c.document_id "
        "WHERE c.id IN (" + ",".join("?" for _ in keys) + ")",
        tuple(int(k) for k in keys),
    )
    metadata = {str(row["id"]): row for row in rows}
    passages = [
        (
            Passage(
                source_url=metadata[k]["document_id"],
                ord=metadata[k]["ord"],
                heading=metadata[k]["heading"],
                page_start=metadata[k]["page_start"],
                page_end=metadata[k]["page_end"],
                text=sanitize(metadata[k]["text"]),
            ),
            fused[k],
        )
        for k in keys
        if k in metadata
    ]
    groups = select(passages, budget, maximum, ratio)
    sources = []
    for n, group in enumerate(groups, 1):
        doc = group[0].source_url
        chosen = [r for r in rows if r["document_id"] == doc and r["ord"] in {p.ord for p in group}]
        pages = [r["page_start"] for r in chosen if r["page_start"] is not None]
        ends = [r["page_end"] for r in chosen if r["page_end"] is not None]
        first = min(pages) if pages else None
        sources.append(
            Source(
                n=n,
                url=f"/api/library/documents/{doc}/file"
                + (f"#page={first}" if first is not None else ""),
                title=chosen[0]["filename"],
                site_name=chosen[0]["filename"],
                domain="",
                fetched_at=now(),
                kind="document",
                document_id=doc,
                page_start=first,
                page_end=max(ends) if ends else None,
                passages=group,
            )
        )
    return sources


async def nearest(
    store: Store, vector: bytes, eligible: str, params: tuple[object, ...]
) -> list[dict[str, Any]]:
    count = await store.one("SELECT count(*) AS n FROM (" + eligible + ")", params)
    if not count or not count["n"]:
        return []
    if count["n"] <= 256:
        # Small collections use vec0's supported rowid pre-filter. This reaches
        # matches below any global cutoff without expanding unrelated candidates.
        return await store.rows(
            "SELECT chunk_id AS id,distance FROM library_vectors WHERE embedding MATCH ? "
            "AND k=40 AND chunk_id IN (" + eligible + ") ORDER BY distance",
            (vector, *params),
        )
    total = await store.one("SELECT count(*) AS n FROM library_vectors")
    n = int(total["n"]) if total else 0
    k = min(40, n)
    while k:
        global_rows = await store.rows(
            "SELECT chunk_id AS id,distance FROM library_vectors WHERE embedding MATCH ? "
            "AND k=? ORDER BY distance",
            (vector, k),
        )
        keys = tuple(r["id"] for r in global_rows)
        filtered = (
            await store.rows(
                "SELECT id FROM ("
                + eligible
                + ") WHERE id IN ("
                + ",".join("?" for _ in keys)
                + ")",
                (*params, *keys),
            )
            if keys
            else []
        )
        allowed = {r["id"] for r in filtered}
        selected = sorted(
            (r for r in global_rows if r["id"] in allowed), key=lambda r: (r["distance"], r["id"])
        )
        # Complete ties at the frontier before returning. Nothing beyond the
        # frontier can displace a nearer scoped candidate; no fixed cutoff.
        if k >= n or (
            len(selected) >= 40 and selected[39]["distance"] < global_rows[-1]["distance"]
        ):
            return selected[:40]
        if k >= 4096:
            # vec0 limits K. The exact scoped scalar search exhausts eligible
            # rows; it never silently discards a deeply ranked collection.
            return await store.rows(
                "SELECT v.chunk_id AS id,vec_distance_cosine(v.embedding,?) AS distance "
                "FROM library_vectors v WHERE v.chunk_id IN (" + eligible + ") "
                "ORDER BY distance,id LIMIT 40",
                (vector, *params),
            )
        k = min(n, k * 2, 4096)
    return []
