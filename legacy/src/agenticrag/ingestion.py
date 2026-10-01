from __future__ import annotations

import hashlib
import importlib.util
import io
import os
import re
import threading
import zipfile
from contextlib import contextmanager
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Iterable, Literal, Sequence
from xml.etree import ElementTree

from .domain import ChunkDraft, ProvenanceSpan, SourceDraft, SourceVersion
from .errors import IngestionError
from .providers.base import EmbeddingProvider
from .store import CorpusStore


OcrMode = Literal["auto", "never", "always"]
_WORD_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
_OFFLINE_ENV_LOCK = threading.Lock()


@dataclass(frozen=True)
class IngestionLimits:
    max_file_bytes: int = 50 * 1024 * 1024
    max_pages: int = 500
    max_segments: int = 100_000
    max_docx_members: int = 2_000
    max_docx_expanded_bytes: int = 250 * 1024 * 1024
    max_docx_compression_ratio: int = 200

    def __post_init__(self) -> None:
        if min(
            self.max_file_bytes,
            self.max_pages,
            self.max_segments,
            self.max_docx_members,
            self.max_docx_expanded_bytes,
            self.max_docx_compression_ratio,
        ) <= 0:
            raise ValueError("All ingestion limits must be positive")


class TextChunker:
    """Character-bounded chunker retaining source provenance intersecting each chunk."""

    def __init__(self, max_chars: int = 1_200, overlap_chars: int = 200) -> None:
        if max_chars < 200:
            raise ValueError("max_chars must be at least 200")
        if overlap_chars < 0 or overlap_chars >= max_chars:
            raise ValueError("overlap_chars must be non-negative and smaller than max_chars")
        self.max_chars = max_chars
        self.overlap_chars = overlap_chars

    def split(
        self, text: str, provenance: Sequence[ProvenanceSpan] = ()
    ) -> list[ChunkDraft]:
        if not text.strip():
            raise IngestionError("Cannot ingest an empty document")
        chunks: list[ChunkDraft] = []
        cursor = 0
        ordinal = 0
        while cursor < len(text):
            end = min(len(text), cursor + self.max_chars)
            if end < len(text):
                floor = cursor + self.max_chars // 2
                candidates = [text.rfind("\n\n", floor, end), text.rfind("\n", floor, end)]
                boundary = max(candidates)
                if boundary < floor:
                    boundary = text.rfind(" ", floor, end)
                if boundary >= floor:
                    end = boundary

            raw = text[cursor:end]
            left_trim = len(raw) - len(raw.lstrip())
            right_trimmed = raw.rstrip()
            start_char = cursor + left_trim
            end_char = cursor + len(right_trimmed)
            chunk_text = text[start_char:end_char]
            if chunk_text:
                spans = tuple(
                    span
                    for span in provenance
                    if span.end_char > start_char and span.start_char < end_char
                )
                pages = [span.page_no for span in spans if span.page_no is not None]
                section_path = _nearest_section(spans, start_char)
                chunks.append(
                    ChunkDraft(
                        ordinal=ordinal,
                        text=chunk_text,
                        heading=section_path[-1] if section_path else self._heading_before(text, start_char),
                        start_char=start_char,
                        end_char=end_char,
                        page_start=min(pages) if pages else None,
                        page_end=max(pages) if pages else None,
                        section_path=section_path,
                        provenance=spans,
                    )
                )
                ordinal += 1

            if end >= len(text):
                break
            cursor = max(end - self.overlap_chars, cursor + 1)
        return chunks

    @staticmethod
    def _heading_before(text: str, offset: int) -> str | None:
        heading: str | None = None
        for match in re.finditer(r"(?m)^#{1,6}\s+(.+?)\s*$", text[:offset]):
            heading = match.group(1).strip()
        return heading


class FileParser:
    """Local-only parser registry with strict type sniffing and bounded inputs."""

    SUPPORTED_SUFFIXES = {".txt", ".md", ".markdown", ".docx", ".pdf"}

    def __init__(
        self,
        *,
        limits: IngestionLimits | None = None,
        ocr: OcrMode = "auto",
        docling_artifacts_path: str | Path | None = None,
    ) -> None:
        if ocr not in {"auto", "never", "always"}:
            raise ValueError("ocr must be 'auto', 'never', or 'always'")
        self.limits = limits or IngestionLimits()
        self.ocr = ocr
        self.docling_artifacts_path = (
            None if docling_artifacts_path is None else Path(docling_artifacts_path).expanduser().resolve()
        )

    def parse(self, path: Path, collection: str, scopes: Sequence[str]) -> SourceDraft:
        resolved = path.expanduser().resolve(strict=True)
        if not resolved.is_file():
            raise IngestionError(f"Source is not a file: {resolved}")
        size = resolved.stat().st_size
        if size > self.limits.max_file_bytes:
            raise IngestionError(
                f"Source is {size} bytes; limit is {self.limits.max_file_bytes} bytes"
            )
        data = resolved.read_bytes()
        suffix = resolved.suffix.lower()
        if suffix not in self.SUPPORTED_SUFFIXES:
            raise IngestionError(
                f"Unsupported source type {suffix!r}; supported types are PDF, DOCX, Markdown, and TXT"
            )
        source_sha = hashlib.sha256(data).hexdigest()
        if suffix == ".pdf":
            self._require_magic(data, b"%PDF-", "PDF")
            return self._parse_pdf(resolved, data, collection, scopes, source_sha)
        if suffix == ".docx":
            return self._parse_docx(resolved, data, collection, scopes, source_sha)
        if data.startswith(b"%PDF-") or data.startswith(b"PK\x03\x04"):
            raise IngestionError("Source content does not match its text/Markdown extension")
        return self._parse_text(resolved, data, collection, scopes, source_sha)

    @staticmethod
    def _require_magic(data: bytes, magic: bytes, label: str) -> None:
        if not data.startswith(magic):
            raise IngestionError(f"Source extension says {label}, but its file signature does not")

    def _parse_text(
        self, path: Path, data: bytes, collection: str, scopes: Sequence[str], source_sha: str
    ) -> SourceDraft:
        try:
            text = data.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise IngestionError(f"Source is not valid UTF-8: {path}") from exc
        if "\x00" in text:
            raise IngestionError("Text sources cannot contain NUL bytes")
        if not text.strip():
            raise IngestionError("Cannot ingest an empty document")
        kind = "markdown" if path.suffix.lower() in {".md", ".markdown"} else "text"
        provenance = _text_provenance(text, markdown=kind == "markdown")
        if len(provenance) > self.limits.max_segments:
            raise IngestionError("Text source contains too many document segments")
        return SourceDraft(
            collection=collection,
            logical_path=path.as_posix(),
            media_type="text/markdown" if kind == "markdown" else "text/plain",
            text=text,
            scopes=tuple(scopes),
            original_bytes=data,
            original_sha256=source_sha,
            parser_id=f"builtin-{kind}-v2",
            provenance=provenance,
        )

    def _parse_docx(
        self, path: Path, data: bytes, collection: str, scopes: Sequence[str], source_sha: str
    ) -> SourceDraft:
        try:
            archive = zipfile.ZipFile(io.BytesIO(data))
        except (zipfile.BadZipFile, OSError) as exc:
            raise IngestionError("DOCX is not a valid ZIP/OOXML package") from exc
        with archive:
            infos = archive.infolist()
            if len(infos) > self.limits.max_docx_members:
                raise IngestionError("DOCX contains too many archive members")
            expanded = sum(info.file_size for info in infos)
            compressed = max(1, sum(info.compress_size for info in infos))
            if expanded > self.limits.max_docx_expanded_bytes:
                raise IngestionError("DOCX expanded content exceeds the configured limit")
            if expanded / compressed > self.limits.max_docx_compression_ratio:
                raise IngestionError("DOCX compression ratio exceeds the configured safety limit")
            names = {info.filename for info in infos}
            required = {"[Content_Types].xml", "word/document.xml"}
            if not required.issubset(names):
                raise IngestionError("DOCX package is missing required OOXML parts")
            if any(name.lower().endswith(("vbaproject.bin", ".exe", ".dll")) for name in names):
                raise IngestionError("Macro-enabled or executable DOCX package content is not supported")
            xml = archive.read("word/document.xml")
        try:
            root = ElementTree.fromstring(xml)
        except ElementTree.ParseError as exc:
            raise IngestionError("DOCX document.xml is malformed") from exc

        elements: list[tuple[str, str, int | None, tuple[str, ...], str | None, bool]] = []
        section: list[str] = []
        body = root.find(f"{_WORD_NS}body")
        if body is None:
            raise IngestionError("DOCX contains no document body")
        table_no = 0
        for child in body:
            if child.tag == f"{_WORD_NS}p":
                value = _word_text(child).strip()
                if not value:
                    continue
                style = child.find(f"{_WORD_NS}pPr/{_WORD_NS}pStyle")
                style_name = "" if style is None else style.attrib.get(f"{_WORD_NS}val", "")
                match = re.fullmatch(r"Heading\s*([1-6])", style_name, flags=re.IGNORECASE)
                if match:
                    level = int(match.group(1))
                    section[level - 1 :] = [value]
                    kind = "heading"
                else:
                    kind = "list_item" if child.find(f"{_WORD_NS}pPr/{_WORD_NS}numPr") is not None else "paragraph"
                elements.append((value, kind, None, tuple(section), None, False))
            elif child.tag == f"{_WORD_NS}tbl":
                table_no += 1
                rows: list[str] = []
                for row in child.findall(f"{_WORD_NS}tr"):
                    cells = [
                        " ".join(_word_text(cell).split())
                        for cell in row.findall(f"{_WORD_NS}tc")
                    ]
                    rows.append(" | ".join(cells))
                value = "\n".join(row for row in rows if row.strip())
                if value:
                    elements.append(
                        (value, "table", None, tuple(section), f"table-{table_no}", False)
                    )
            if len(elements) > self.limits.max_segments:
                raise IngestionError("DOCX contains too many document elements")
        text, provenance = _assemble(elements)
        return SourceDraft(
            collection=collection,
            logical_path=path.as_posix(),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            text=text,
            scopes=tuple(scopes),
            original_bytes=data,
            original_sha256=source_sha,
            parser_id="builtin-docx-ooxml-v1",
            provenance=provenance,
        )

    def _parse_pdf(
        self, path: Path, data: bytes, collection: str, scopes: Sequence[str], source_sha: str
    ) -> SourceDraft:
        if self.ocr == "always":
            return self._parse_pdf_docling(path, data, collection, scopes, source_sha, force_ocr=True)
        if importlib.util.find_spec("pypdf") is None:
            if self.ocr == "auto" and self._docling_ready():
                return self._parse_pdf_docling(path, data, collection, scopes, source_sha, force_ocr=True)
            raise IngestionError(
                "PDF parsing requires the local 'documents' extra: pip install -e '.[documents]'. "
                "Scanned PDFs additionally require the 'docling' extra and a local "
                "AGENTICRAG_DOCLING_ARTIFACTS_PATH."
            )
        try:
            from pypdf import PdfReader

            reader = PdfReader(io.BytesIO(data), strict=False)
            if reader.is_encrypted:
                raise IngestionError("Encrypted PDFs are not supported")
            if len(reader.pages) > self.limits.max_pages:
                raise IngestionError(
                    f"PDF has {len(reader.pages)} pages; limit is {self.limits.max_pages}"
                )
            elements = []
            low_text_pages = 0
            for page_no, page in enumerate(reader.pages, start=1):
                value = (page.extract_text() or "").strip()
                if len(value) < 24:
                    low_text_pages += 1
                if value:
                    elements.append((value, "page_text", page_no, (), None, False))
        except IngestionError:
            raise
        except Exception as exc:
            raise IngestionError("PDF could not be parsed safely") from exc
        needs_ocr = not elements or low_text_pages > len(reader.pages) // 2
        if needs_ocr and self.ocr == "auto":
            if self._docling_ready():
                return self._parse_pdf_docling(path, data, collection, scopes, source_sha, force_ocr=True)
            raise IngestionError(
                "PDF contains pages with little or no extractable text. Local OCR is unavailable; "
                "install the 'docling' extra and set AGENTICRAG_DOCLING_ARTIFACTS_PATH to "
                "prefetched model artifacts, or use --ocr never to accept text-only extraction."
            )
        if not elements:
            raise IngestionError(
                "PDF has no extractable text. Rerun with --ocr auto or --ocr always after "
                "installing the local Docling capability and prefetched artifacts."
            )
        text, provenance = _assemble(elements)
        return SourceDraft(
            collection=collection,
            logical_path=path.as_posix(),
            media_type="application/pdf",
            text=text,
            scopes=tuple(scopes),
            original_bytes=data,
            original_sha256=source_sha,
            parser_id=f"pypdf-{_package_version('pypdf')}-text-v1",
            provenance=provenance,
        )

    def _docling_ready(self) -> bool:
        return (
            importlib.util.find_spec("docling") is not None
            and self.docling_artifacts_path is not None
            and self.docling_artifacts_path.is_dir()
        )

    def _parse_pdf_docling(
        self,
        path: Path,
        data: bytes,
        collection: str,
        scopes: Sequence[str],
        source_sha: str,
        *,
        force_ocr: bool,
    ) -> SourceDraft:
        if importlib.util.find_spec("docling") is None:
            raise IngestionError(
                "Local OCR requires Docling: pip install -e '.[docling]'"
            )
        if self.docling_artifacts_path is None or not self.docling_artifacts_path.is_dir():
            raise IngestionError(
                "Local Docling PDF parsing requires AGENTICRAG_DOCLING_ARTIFACTS_PATH to point "
                "to prefetched model artifacts; runtime downloads are intentionally disabled"
            )
        try:
            from docling.datamodel.base_models import InputFormat
            from docling.datamodel.pipeline_options import PdfPipelineOptions
            from docling.document_converter import DocumentConverter, PdfFormatOption

            options = PdfPipelineOptions(
                artifacts_path=self.docling_artifacts_path,
                do_ocr=force_ocr,
                do_table_structure=True,
                enable_remote_services=False,
                allow_external_plugins=False,
            )
            with _offline_model_environment():
                converter = DocumentConverter(
                    allowed_formats=[InputFormat.PDF],
                    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)},
                )
                result = converter.convert(path, max_num_pages=self.limits.max_pages)
            elements = _docling_elements(result.document, force_ocr, self.limits.max_segments)
        except IngestionError:
            raise
        except Exception as exc:
            raise IngestionError(
                "Local Docling conversion failed. Verify the artifact directory and installed OCR "
                "engine; remote services and external plugins are disabled."
            ) from exc
        text, provenance = _assemble(elements)
        return SourceDraft(
            collection=collection,
            logical_path=path.as_posix(),
            media_type="application/pdf",
            text=text,
            scopes=tuple(scopes),
            original_bytes=data,
            original_sha256=source_sha,
            parser_id=(
                f"docling-{_package_version('docling')}-pdf-v1:ocr={str(force_ocr).lower()}"
            ),
            provenance=provenance,
        )


class Ingestor:
    def __init__(
        self,
        store: CorpusStore,
        embedding_provider: EmbeddingProvider | None = None,
        chunker: TextChunker | None = None,
        batch_size: int = 32,
        parser: FileParser | None = None,
    ) -> None:
        if batch_size <= 0:
            raise ValueError("batch_size must be positive")
        self.store = store
        self.embedding_provider = embedding_provider
        self.chunker = chunker or TextChunker()
        self.batch_size = batch_size
        self.parser = parser or FileParser()

    def ingest_file(self, path: Path, collection: str, scopes: Sequence[str]) -> SourceVersion:
        return self.ingest_source(self.parser.parse(path, collection, scopes))

    def ingest_source(self, source: SourceDraft) -> SourceVersion:
        chunks = self.chunker.split(source.text, source.provenance)
        if self.embedding_provider is None:
            return self.store.publish(source, chunks, [], embedding_label="lexical-only",
                                      index_signature="lexical-only-v1")
        vectors = self.embedding_provider.embed([chunk.text for chunk in chunks])
        if len(vectors) != len(chunks):
            raise IngestionError("Embedding provider returned the wrong number of vectors")
        return self.store.publish(source, chunks, vectors, embedding_label=self.embedding_provider.label,
                                 index_signature=f"{self.embedding_provider.label}|text-chunker-v1:{self.chunker.max_chars}:{self.chunker.overlap_chars}")



def parser_capabilities(docling_artifacts_path: str | Path | None = None) -> dict[str, object]:
    artifacts = None if docling_artifacts_path is None else Path(docling_artifacts_path).expanduser()
    return {
        "txt_markdown": {"available": True, "parser": "builtin"},
        "docx": {"available": True, "parser": "builtin-ooxml", "page_numbers": False},
        "pdf_text": {
            "available": importlib.util.find_spec("pypdf") is not None,
            "install": "pip install -e '.[documents]'",
        },
        "pdf_ocr": {
            "available": importlib.util.find_spec("docling") is not None
            and artifacts is not None
            and artifacts.is_dir(),
            "docling_installed": importlib.util.find_spec("docling") is not None,
            "artifacts_configured": artifacts is not None and artifacts.is_dir(),
            "network_services": False,
            "install": "pip install -e '.[docling]' and set AGENTICRAG_DOCLING_ARTIFACTS_PATH",
        },
    }


def _text_provenance(text: str, *, markdown: bool) -> tuple[ProvenanceSpan, ...]:
    spans: list[ProvenanceSpan] = []
    section: list[str] = []
    paragraph_pattern = r"\S(?:.*?\S)?(?=\r?\n[ \t]*\r?\n|\Z)"
    for ordinal, match in enumerate(re.finditer(paragraph_pattern, text, re.DOTALL)):
        value = match.group(0)
        kind = "paragraph"
        if markdown:
            heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", value, flags=re.MULTILINE)
            if heading:
                level = len(heading.group(1))
                title = heading.group(2).strip()
                section[level - 1 :] = [title]
                kind = "heading"
            elif all(
                line.strip().startswith("|") and line.strip().endswith("|")
                for line in value.splitlines()
                if line.strip()
            ):
                kind = "table"
            elif re.match(r"^\s*(?:[-*+] |\d+[.)] )", value):
                kind = "list_item"
        spans.append(
            ProvenanceSpan(
                segment_id=_segment_id(ordinal, kind, value),
                kind=kind,
                start_char=match.start(),
                end_char=match.end(),
                source_start=match.start(),
                source_end=match.end(),
                section_path=tuple(section),
                table_id=f"table-{ordinal + 1}" if kind == "table" else None,
            )
        )
    return tuple(spans)


def _assemble(elements: Iterable[tuple[object, ...]]) -> tuple[str, tuple[ProvenanceSpan, ...]]:
    parts: list[str] = []
    spans: list[ProvenanceSpan] = []
    cursor = 0
    for ordinal, element in enumerate(elements):
        raw, kind, page, section, table_id, ocr = element[:6]
        bbox = element[6] if len(element) > 6 else None
        value = str(raw).strip()
        if not value:
            continue
        if parts:
            parts.append("\n\n")
            cursor += 2
        start = cursor
        parts.append(value)
        cursor += len(value)
        spans.append(
            ProvenanceSpan(
                segment_id=_segment_id(ordinal, kind, value),
                kind=str(kind),
                start_char=start,
                end_char=cursor,
                page_no=None if page is None else int(page),
                bbox=None if bbox is None else tuple(bbox),  # type: ignore[arg-type]
                section_path=tuple(section),  # type: ignore[arg-type]
                table_id=None if table_id is None else str(table_id),
                ocr=bool(ocr),
            )
        )
    text = "".join(parts)
    if not text.strip():
        raise IngestionError("Parser produced no usable text")
    return text, tuple(spans)


def _word_text(element: ElementTree.Element) -> str:
    return "".join(node.text or "" for node in element.iter(f"{_WORD_NS}t"))


def _segment_id(ordinal: int, kind: str, value: str) -> str:
    digest = hashlib.sha256(f"{ordinal}\0{kind}\0{value}".encode("utf-8")).hexdigest()[:16]
    return f"seg-{ordinal:06d}-{digest}"


def _package_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "unknown"


def _nearest_section(spans: Sequence[ProvenanceSpan], offset: int) -> tuple[str, ...]:
    before = [span for span in spans if span.start_char <= offset and span.section_path]
    if before:
        return before[-1].section_path
    with_section = [span for span in spans if span.section_path]
    return with_section[0].section_path if with_section else ()


def _docling_elements(
    document: object, force_ocr: bool, max_segments: int
) -> list[tuple[object, ...]]:
    elements: list[tuple[object, ...]] = []
    section: list[str] = []
    iterator = getattr(document, "iterate_items", None)
    if iterator is None:
        raise IngestionError("Installed Docling version does not expose document provenance")
    for item, level in iterator():
        label = str(getattr(item, "label", item.__class__.__name__)).lower()
        text = str(getattr(item, "text", "") or "").strip()
        if not text and "table" in label:
            exporter = getattr(item, "export_to_markdown", None)
            text = str(exporter(document) if callable(exporter) else "").strip()
        if not text:
            continue
        kind = "table" if "table" in label else "heading" if "title" in label or "heading" in label else "paragraph"
        if kind == "heading":
            depth = max(1, min(6, int(level or 1)))
            section[depth - 1 :] = [text]
        prov = tuple(getattr(item, "prov", ()) or ())
        page = None
        if prov:
            page_value = getattr(prov[0], "page_no", None)
            page = None if page_value is None else int(page_value)
        bbox = _docling_bbox(prov[0]) if prov else None
        table_id = f"table-{len(elements) + 1}" if kind == "table" else None
        elements.append((text, kind, page, tuple(section), table_id, force_ocr, bbox))
        if len(elements) > max_segments:
            raise IngestionError("Docling produced too many document elements")
    return elements


def _docling_bbox(provenance: object) -> tuple[float, float, float, float] | None:
    bbox = getattr(provenance, "bbox", None)
    if bbox is None:
        return None
    values = tuple(getattr(bbox, name, None) for name in ("l", "t", "r", "b"))
    if any(value is None for value in values):
        return None
    return tuple(float(value) for value in values)  # type: ignore[return-value]


@contextmanager
def _offline_model_environment() -> Iterable[None]:
    """Prevent model hubs from making artifact-fetch requests during Docling conversion."""

    names = ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE")
    with _OFFLINE_ENV_LOCK:
        previous = {name: os.environ.get(name) for name in names}
        os.environ.update({name: "1" for name in names})
        try:
            yield
        finally:
            for name, value in previous.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value
