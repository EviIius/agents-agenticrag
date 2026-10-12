"""Bounded extraction in a supervised process; no private parser output reaches logs."""

import json
import logging
import sys
from dataclasses import asdict
from pathlib import Path

import trafilatura

from ..documents.extract import TEXT_LIMIT, Extracted, error, pdf, word
from ..errors import AppError


def extract(path: Path, suffix: str) -> Extracted:
    try:
        if suffix == ".pdf":
            return pdf(path)
        if suffix == ".docx":
            return word(path)
        with path.open("rb") as source:
            data = source.read(TEXT_LIMIT * 4 + 1)
        if len(data) > TEXT_LIMIT * 4:
            raise error("document_too_large")
        text = data.decode("utf-8-sig")
        if suffix == ".html":
            text = trafilatura.extract(text, output_format="markdown", include_tables=True) or ""
        if len(text) > TEXT_LIMIT:
            raise error("document_too_large")
        if not text.strip():
            raise error("document_unreadable")
        return Extracted(text, None, len(text))
    except AppError:
        raise
    except Exception:
        raise error("document_unreadable") from None


def main() -> None:
    logging.disable(logging.CRITICAL)
    source, suffix, output = sys.argv[1:]
    try:
        result = asdict(extract(Path(source), suffix))
    except AppError as exc:
        result = {"error": exc.code}
    with Path(output).open("x", encoding="utf-8") as destination:
        Path(output).chmod(0o600)
        json.dump(result, destination, ensure_ascii=False)


if __name__ == "__main__":
    main()
