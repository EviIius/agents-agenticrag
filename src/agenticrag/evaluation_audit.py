"""Preflight checks for a document-grounded evaluation set.

Gold evidence is tied to a logical document and exact text rather than a
generated chunk ID, so it survives a change to the chunker.
"""

from __future__ import annotations

import re
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any, Sequence

from .experiments import ExperimentCase


def _normalized(text: str) -> str:
    return " ".join(text.casefold().split())


def audit_evaluation_corpus(
    database: str | Path, cases: Sequence[ExperimentCase], *,
    min_documents: int = 100, min_chunks: int = 2_000, min_questions: int = 150,
) -> dict[str, Any]:
    """Return explicit readiness findings; never silently certify a toy set."""
    path = Path(database)
    if not path.is_file():
        raise FileNotFoundError(path)
    connection = sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        sources = connection.execute(
            "SELECT d.collection_id, d.logical_path, s.content, s.media_type, "
            "(SELECT COUNT(*) FROM source_versions v WHERE v.document_id=d.id) AS versions "
            "FROM documents d JOIN source_versions s ON s.id=d.current_version_id"
        ).fetchall()
        chunk_count = connection.execute(
            "SELECT COUNT(*) FROM chunks c JOIN documents d ON d.current_version_id=c.source_version_id"
        ).fetchone()[0]
    finally:
        connection.close()
    source_by_path = {(row["collection_id"], row["logical_path"]): row for row in sources}
    splits = Counter(case.split for case in cases)
    categories = Counter(case.category for case in cases)
    answerability = Counter(case.answerable for case in cases)
    media_types = Counter(row["media_type"] for row in sources)
    issues: list[str] = []
    if len(sources) < min_documents:
        issues.append(f"Only {len(sources)} documents; target is {min_documents}")
    if chunk_count < min_chunks:
        issues.append(f"Only {chunk_count} chunks; target is {min_chunks}")
    if len(cases) < min_questions:
        issues.append(f"Only {len(cases)} questions; target is {min_questions}")
    if not splits["dev"] or not splits["locked"]:
        issues.append("Both dev and locked question splits are required")
    if not answerability[True] or not answerability[False]:
        issues.append("The question set needs both answerable and unanswerable cases")
    if not any("multi" in category for category in categories):
        issues.append("The question set needs multi-hop or multi-source cases")
    if not any(row["versions"] > 1 for row in sources):
        issues.append("No document has two indexed versions")
    if not any("pdf" in media_type for media_type in media_types):
        issues.append("No PDF has been indexed")
    seen_questions: dict[str, str] = {}
    gold_count = 0
    for case in cases:
        key = re.sub(r"\W+", " ", case.question.casefold()).strip()
        prior_split = seen_questions.get(key)
        if prior_split is not None:
            issues.append(f"Duplicate question across cases: {case.id} ({prior_split}/{case.split})")
        seen_questions[key] = case.split
        if case.answerable is True and not case.required_quotes:
            issues.append(f"Answerable case {case.id} has no gold quote")
        for annotation in case.required_quotes:
            gold_count += 1
            source = source_by_path.get((case.collection, annotation["logical_path"]))
            if source is None:
                issues.append(f"Case {case.id} names a missing document: {annotation['logical_path']}")
            elif _normalized(annotation["quote"]) not in _normalized(source["content"]):
                issues.append(f"Case {case.id} has a quote absent from {annotation['logical_path']}")
    return {
        "ready": not issues,
        "documents": len(sources),
        "chunks": chunk_count,
        "questions": len(cases),
        "gold_quotes": gold_count,
        "splits": dict(splits),
        "categories": dict(categories),
        "answerability": {"answerable": answerability[True], "unanswerable": answerability[False],
                          "unlabelled": answerability[None]},
        "media_types": dict(media_types),
        "issues": issues,
    }
