import asyncio
import io
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import urlsplit

import trafilatura
from pypdf import PdfReader

from .fetch import RawPage

_WORKER = ThreadPoolExecutor(max_workers=1, thread_name_prefix="web-extract")


async def extract_async(raw: RawPage, max_chars: int = 80000) -> "Page":
    # trafilatura shares native lxml parsers. Keep their trees on one worker:
    # concurrent parsing crashed CPython on this Mac (Phase 2 crash report).
    return await asyncio.get_running_loop().run_in_executor(_WORKER, extract, raw, max_chars)


class _Text(HTMLParser):
    """Keep meaningful table and emphasis structure, excluding navigation chrome."""

    VOID = {
        "br",
        "hr",
        "img",
        "input",
        "meta",
        "link",
        "source",
        "wbr",
        "area",
        "embed",
        "param",
        "col",
        "track",
        "base",
    }
    BLOCK = {"p", "h1", "h2", "h3", "h4", "li", "section", "article", "br", "tr", "table", "div"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, bool, bool]] = []
        self.parts: list[str] = []
        self.main_parts: list[str] = []
        self.content_parts: list[str] = []

    def _append(self, text: str) -> None:
        if any(item[1] for item in self.stack):
            return
        self.parts.append(text)
        if any(item[2] for item in self.stack):
            self.main_parts.append(text)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        tokens = set(
            re.split(
                r"[\s_-]+", (attributes.get("id") or "") + " " + (attributes.get("class") or "")
            )
        )
        skip = tag in {
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "noscript",
            "svg",
            "aside",
        } or (
            tag not in {"html", "body", "main", "article"}
            and bool(
                tokens
                & {
                    "footer",
                    "navigation",
                    "sidebar",
                    "comments",
                    "cookie",
                    "advertisement",
                    "ads",
                    "toc",
                    "navbox",
                }
            )
        )
        primary = (
            tag in {"main", "article"}
            or attributes.get("role") == "main"
            or attributes.get("itemprop") == "articleBody"
            or bool(tokens & {"apd", "AppleTopic", "mw-content-text"})
        )
        if tag not in self.VOID:
            self.stack.append((tag, skip, primary))
        if tag in self.BLOCK:
            self._append("\n")
        if tag in {"b", "strong"}:
            self._append("**")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"}:
            self._append(" | ")
        if tag in {"b", "strong"}:
            for parts in (self.parts, self.main_parts):
                if parts:
                    parts[-1] = parts[-1].rstrip()
            self._append("** ")
        if tag in self.BLOCK:
            self._append("\n")
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data: str) -> None:
        if data.strip():
            self._append(data.strip() + " ")


@dataclass
class Page:
    url: str
    title: str
    site_name: str
    published_at: str | None
    text: str


def extract(raw: RawPage, max_chars: int = 80000) -> Page:
    if not 1 <= max_chars <= 500000:
        raise ValueError("Invalid extraction limit")
    mime = raw.content_type.split(";", 1)[0].strip().lower()
    domain = urlsplit(raw.url).hostname or ""
    title, site, date = domain, domain, None
    if mime == "application/pdf":
        reader = PdfReader(io.BytesIO(raw.data))
        text = "\n\n".join(p.extract_text() or "" for p in reader.pages[:30])
        if reader.metadata and reader.metadata.title:
            title = str(reader.metadata.title)
    elif mime in ("text/html", "application/xhtml+xml", "text/plain"):
        charset = re.search(r"charset\s*=\s*[\"']?([^;\s\"']+)", raw.content_type, re.I)
        if not charset:
            charset = re.search(
                r"charset\s*=\s*[\"']?([^;\s\"'/>]+)",
                raw.data[:4096].decode("ascii", errors="ignore"),
                re.I,
            )
        try:
            decoded = raw.data.decode(charset[1] if charset else "utf-8", errors="replace")
        except LookupError:
            decoded = raw.data.decode("utf-8", errors="replace")
        if mime == "text/plain":
            text = decoded
        else:
            text = (
                trafilatura.extract(
                    decoded,
                    url=raw.url,
                    output_format="markdown",
                    include_tables=True,
                    include_comments=False,
                    include_links=False,
                    include_images=False,
                    favor_recall=True,
                )
                or ""
            )
            metadata = trafilatura.extract_metadata(decoded, default_url=raw.url)
            if metadata:
                title = metadata.title or title
                site = metadata.sitename or site
                date = metadata.date
            if not text:
                parser = _Text()
                parser.feed(decoded)
                chosen = (
                    parser.main_parts if len("".join(parser.main_parts)) >= 80 else parser.parts
                )
                text = "\n".join(
                    re.sub(r"[ \t]+", " ", line).strip()
                    for line in "".join(chosen).splitlines()
                    if line.strip()
                )
    else:
        raise ValueError("unsupported type")
    text = text.strip()
    if len(text) < 1200 and re.search(
        r"enable javascript|are you a robot|captcha|access denied|"
        r"subscribe to (continue|read)|cookies? (policy|settings)",
        text,
        re.I,
    ):
        raise ValueError("blocked or needs JavaScript")
    if len(text) < 300:
        raise ValueError("too little readable text")
    return Page(raw.url, title, site, date, text[:max_chars])
