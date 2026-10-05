"""Text only: PDFs with page markers and Word paragraphs/tables in document order."""

from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from pypdf import PdfReader

from ..errors import AppError

UPLOAD_LIMIT = 50 * 1024**2
PAGE_LIMIT = 1500
TEXT_LIMIT = 2_000_000
XML_LIMIT = 16 * 1024**2
EXPANDED_LIMIT = 64 * 1024**2
ENTRY_LIMIT = 2048
ERRORS = {
    "document_no_text": "This PDF has no selectable text. Scanned documents aren't supported yet.",
    "document_encrypted": "This PDF is password-protected. Remove the password and try again.",
    "document_unreadable": "Couldn't read this file. It may be damaged.",
    "document_too_large": "Documents can be up to 50 MB and 1,500 pages.",
    "document_timeout": "This document took too long to read.",
}
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


@dataclass
class Extracted:
    text: str
    pages: int | None
    chars: int


def error(code: str) -> AppError:
    return AppError(code, ERRORS[code], 413 if code == "document_too_large" else 422)


def bounded(parts: list[str], value: str, count: int) -> int:
    count += len(value)
    if count > TEXT_LIMIT:
        raise error("document_too_large")
    parts.append(value)
    return count


def paragraph(node: ET.Element) -> str:
    parts: list[str] = []

    def visit(element: ET.Element) -> None:
        if element.tag in (W + "del", W + "moveFrom"):
            return
        if element.tag == W + "t":
            parts.append(element.text or "")
        elif element.tag == W + "tab":
            parts.append("\t")
        elif element.tag in (W + "br", W + "cr"):
            parts.append("\n")
        else:
            for child in element:
                visit(child)

    visit(node)
    return "".join(parts)


def cell_paragraphs(node: ET.Element) -> list[str]:
    if node.tag in (W + "del", W + "moveFrom"):
        return []
    if node.tag == W + "p":
        return [paragraph(node)]
    return [text for child in node for text in cell_paragraphs(child)]


def word(path: Path) -> Extracted:
    with ZipFile(path) as archive:
        entries = archive.infolist()
        if len(entries) > ENTRY_LIMIT or sum(e.file_size for e in entries) > EXPANDED_LIMIT:
            raise error("document_too_large")
        info = archive.getinfo("word/document.xml")
        if info.file_size > XML_LIMIT:
            raise error("document_too_large")
        with archive.open(info) as source:
            xml = source.read(XML_LIMIT + 1)
        if len(xml) > XML_LIMIT:
            raise error("document_too_large")
        # Word document XML never needs a DTD or custom entities.
        if b"<!DOCTYPE" in xml.replace(b"\x00", b"") or b"<!ENTITY" in xml.replace(b"\x00", b""):
            raise error("document_unreadable")
        root = ET.fromstring(xml)
    body = root.find(W + "body")
    if body is None:
        raise error("document_unreadable")
    parts: list[str] = []
    count = 0

    def blocks(node: ET.Element) -> None:
        nonlocal count
        for child in node:
            if child.tag == W + "p":
                count = bounded(parts, paragraph(child) + "\n", count)
            elif child.tag == W + "tbl":
                for row in child.findall(W + "tr"):
                    cells = ["\n".join(cell_paragraphs(cell)) for cell in row.findall(W + "tc")]
                    count = bounded(parts, "\t".join(cells) + "\n", count)
            elif child.tag not in (W + "del", W + "moveFrom", W + "sectPr"):
                blocks(child)

    blocks(body)
    text = "".join(parts).strip()
    if not text:
        raise error("document_unreadable")
    return Extracted(text, None, len(text))


def pdf(path: Path) -> Extracted:
    reader = PdfReader(path)
    if reader.is_encrypted:
        raise error("document_encrypted")
    pages = len(reader.pages)
    if pages > PAGE_LIMIT:
        raise error("document_too_large")
    parts: list[str] = []
    count = selectable = 0
    for number, page in enumerate(reader.pages, 1):
        stream = page.get_contents()
        if stream is not None and len(stream.get_data()) > XML_LIMIT:
            raise error("document_too_large")
        text = page.extract_text() or ""
        selectable += sum(not c.isspace() for c in text)
        count = bounded(parts, f"\n\n[Page {number}]\n" + text, count)
    if not pages or selectable / pages < 20:
        raise error("document_no_text")
    text = "".join(parts)
    return Extracted(text, pages, len(text))


def extract(path: Path, suffix: str) -> Extracted:
    try:
        if path.stat().st_size > UPLOAD_LIMIT:
            raise error("document_too_large")
        if suffix == ".pdf":
            return pdf(path)
        if suffix == ".docx":
            return word(path)
        raise error("document_unreadable")
    except AppError:
        raise
    except Exception:
        # Parser exceptions can contain private filenames or document contents.
        raise error("document_unreadable") from None
