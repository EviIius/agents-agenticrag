"""Bounded public HTTPS page extraction for consented web research."""

from __future__ import annotations

import http.client
import ipaddress
import socket
import ssl
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, quote


MAX_PAGE_BYTES = 2_000_000
MAX_PAGE_CHARS = 100_000


class _Text(HTMLParser):
    """Keep meaningful table and emphasis structure, excluding navigation chrome."""
    VOID = {"br", "hr", "img", "input", "meta", "link", "source", "wbr", "area", "embed", "param", "col", "track", "base"}
    BLOCK = {"p", "h1", "h2", "h3", "h4", "li", "section", "article", "br", "tr", "table", "div"}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.parts = []
        self.main_parts = []
        self.content_parts = []

    def _append(self, text):
        if any(item[1] for item in self.stack):
            return
        self.parts.append(text)
        if any(item[2] for item in self.stack):
            self.main_parts.append(text)

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        tokens = set(re.split(r"[\s_-]+", (attributes.get("id") or "")+" "+(attributes.get("class") or "")))
        skip = tag in {"script", "style", "nav", "footer", "header", "noscript", "svg", "aside"} or (tag not in {"html", "body", "main", "article"} and bool(tokens & {
            "footer", "navigation", "sidebar", "comments", "cookie", "advertisement", "ads", "toc", "navbox"}))
        primary = tag in {"main", "article"} or attributes.get("role") == "main" or attributes.get("itemprop") == "articleBody" or bool(tokens & {"apd", "AppleTopic", "mw-content-text"})
        if tag not in self.VOID:
            self.stack.append((tag, skip, primary))
        if tag in self.BLOCK:
            self._append("\n")
        if tag in {"b", "strong"}:
            self._append("**")

    def handle_endtag(self, tag):
        if tag in {"td", "th"}:
            self._append(" | ")
        if tag in {"b", "strong"}:
            for parts in (self.parts, self.main_parts):
                if parts:
                    parts[-1] = parts[-1].rstrip()
            self._append("** ")
        if tag in self.BLOCK:
            self._append("\n")
        for index in range(len(self.stack)-1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        if data.strip():
            self._append(data.strip()+" ")


class _PinnedHTTPS(http.client.HTTPSConnection):
    def __init__(self, host: str, ip: str, timeout: float) -> None:
        mac_ca_bundle = Path("/etc/ssl/cert.pem")
        context = ssl.create_default_context(cafile=str(mac_ca_bundle) if mac_ca_bundle.is_file() else None)
        super().__init__(host, port=443, timeout=timeout, context=context)
        self._pinned_ip = ip

    def connect(self) -> None:
        raw = socket.create_connection((self._pinned_ip, 443), self.timeout)
        try:
            self.sock = self._context.wrap_socket(raw, server_hostname=self.host)
        except BaseException:
            raw.close()
            raise


def _public_address(url: str) -> tuple[str, str, str]:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Only public HTTPS pages can be read")
    if parsed.port not in (None, 443):
        raise ValueError("Nonstandard web ports are not allowed")
    host = parsed.hostname.rstrip(".").encode("idna").decode("ascii")
    if len(host) > 253 or host.endswith((".local", ".localhost", ".internal")):
        raise ValueError("Private hosts are not allowed")
    addresses = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    ips = {row[4][0] for row in addresses}
    if not ips or not all(ipaddress.ip_address(ip).is_global for ip in ips):
        raise ValueError("Private or unroutable addresses are not allowed")
    path = quote(parsed.path or "/", safe="/%:@!$&'()*+,;=-._~")
    if parsed.query:
        path += "?" + quote(parsed.query, safe="%=&?/:;+,@!$'()*-._~")
    return host, sorted(ips)[0], path


def fetch_public_page(url: str) -> tuple[str, str]:
    """Return the final URL and short text; DNS is validated and pinned per redirect."""
    current = url
    for _ in range(3):
        host, ip, path = _public_address(current)
        connection = _PinnedHTTPS(host, ip, 6.0)
        try:
            connection.request("GET", path, headers={
                "Host": host, "Accept": "text/html,text/plain;q=0.8",
                "Accept-Encoding": "identity", "User-Agent": "ChatWeb/0.5",
            })
            response = connection.getresponse()
            if response.status in {301, 302, 303, 307, 308}:
                location = response.getheader("Location")
                if not location:
                    raise ValueError("Redirect had no destination")
                current = urljoin(current, location)
                continue
            if response.status != 200:
                raise ValueError(f"HTTP {response.status}: page unavailable or access blocked")
            content_type = response.getheader("Content-Type", "").lower()
            if not (content_type.startswith("text/html") or content_type.startswith("text/plain")):
                raise ValueError("Page is not text")
            raw = response.read(MAX_PAGE_BYTES + 1)
            if len(raw) > MAX_PAGE_BYTES:
                raise ValueError("Page exceeds reading limit")
        finally:
            connection.close()
        decoded = raw.decode("utf-8", errors="replace")
        if content_type.startswith("text/plain"):
            text = decoded
        else:
            parser = _Text()
            parser.feed(decoded)
            chosen = parser.main_parts if len("".join(parser.main_parts)) >= 80 else parser.parts
            text = "\n".join(re.sub(r"[ \t]+", " ", line).strip() for line in "".join(chosen).splitlines() if line.strip())
        if len(text) < 80 or sum(c.isalpha() for c in text) < 60:
            raise ValueError("Page has too little readable text")
        if len(text) < 500 and all(word in text.lower() for word in ("copyright", "privacy", "terms")):
            raise ValueError("Page contains only site navigation and metadata")
        return current, text[:MAX_PAGE_CHARS]
    raise ValueError("Too many redirects")
