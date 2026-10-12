"""Explicit fixture/recording boundary. Production never consults eval content."""

import gzip
import hashlib
import json
from pathlib import Path

from ..schemas import SearchResult
from .fetch import RawPage


class Fixtures:
    def __init__(self, directory: Path | None = None, recording: Path | None = None) -> None:
        self.directory, self.recording = directory, recording
        if recording:
            recording.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def key(provider: str, query: str, freshness: str) -> str:
        return hashlib.sha256((provider + "\0" + query + "\0" + freshness).encode()).hexdigest()

    def search(self, provider: str, query: str, freshness: str) -> list[SearchResult] | None:
        if not self.directory:
            return None
        key = self.key(provider, query, freshness)
        file = self.directory / (key + ".search.json")
        if not file.exists():
            # Synthetic browser/attack fixtures declare wildcards; real web recordings do not.
            file = self.directory / (provider + ".search.json")
        if not file.exists():
            raise ValueError("Search fixture missing for this query")
        raw = json.loads(file.read_text())
        if isinstance(raw, dict) and raw.get("error"):
            raise ValueError(raw["error"])
        return [SearchResult.model_validate(r) for r in raw]

    def save_search(
        self, provider: str, query: str, freshness: str, results: list[SearchResult]
    ) -> None:
        if self.recording:
            (self.recording / (self.key(provider, query, freshness) + ".search.json")).write_text(
                json.dumps([r.model_dump() for r in results], indent=2)
            )

    def save_error(self, provider: str, query: str, freshness: str, reason: str) -> None:
        if self.recording:
            (self.recording / (self.key(provider, query, freshness) + ".search.json")).write_text(
                json.dumps({"error": reason})
            )

    def save_page_error(self, url: str, reason: str) -> None:
        if self.recording:
            key = hashlib.sha256(url.encode()).hexdigest()
            (self.recording / (key + ".page.json")).write_text(
                json.dumps({"url": url, "error": reason})
            )

    def page(self, url: str) -> RawPage | None:
        if not self.directory:
            return None
        key = hashlib.sha256(url.encode()).hexdigest()
        meta = json.loads((self.directory / (key + ".page.json")).read_text())
        if meta.get("error"):
            raise ValueError(meta["error"])
        raw = self.directory / (key + ".page.bin")
        data = (
            raw.read_bytes()
            if raw.exists()
            else gzip.decompress(raw.with_suffix(".bin.gz").read_bytes())
        )
        return RawPage(meta["url"], data, meta["content_type"])

    def save_page(self, url: str, raw: RawPage) -> None:
        if self.recording:
            key = hashlib.sha256(url.encode()).hexdigest()
            (self.recording / (key + ".page.bin")).write_bytes(raw.data)
            (self.recording / (key + ".page.json")).write_text(
                json.dumps({"url": raw.url, "content_type": raw.content_type})
            )
