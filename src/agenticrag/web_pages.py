"""Bounded public HTTPS page extraction for consented web research."""

from __future__ import annotations

import http.client
import ipaddress
import socket
import ssl
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit


MAX_PAGE_BYTES = 2_000_000
MAX_PAGE_CHARS = 5_000


class _Text(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.hidden = 0
        self.parts: list[str] = []
        self.main_depth = 0
        self.main_parts: list[str] = []
        self.content_depth = 0
        self.content_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_map = dict(attrs)
        classes = set((attrs_map.get("class") or "").split())
        if tag == "div" and {"AppleTopic", "apd-topic"} <= classes:
            self.content_parts.clear()
        if tag == "article" or {"AppleTopic", "apd-topic"} <= classes or attrs_map.get("itemprop") == "articleBody":
            self.content_depth += 1
        if tag == "main":
            self.main_depth += 1
        if tag in {"script", "style", "nav", "footer", "header", "noscript", "svg"}:
            self.hidden += 1
        if tag in {"p", "h1", "h2", "h3", "li", "section", "article", "br"}:
            self.parts.append("\n")
            if self.main_depth:
                self.main_parts.append("\n")
            if self.content_depth:
                self.content_parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag == "article" and self.content_depth:
            self.content_depth -= 1
        if tag == "main":
            self.main_depth = max(0, self.main_depth - 1)
        if tag in {"script", "style", "nav", "footer", "header", "noscript", "svg"}:
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, data: str) -> None:
        if not self.hidden and data.strip():
            self.parts.append(data.strip() + " ")
            if self.main_depth:
                self.main_parts.append(data.strip() + " ")
            if self.content_depth:
                self.content_parts.append(data.strip() + " ")


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
    host = parsed.hostname.rstrip(".")
    if len(host) > 253 or host.endswith((".local", ".localhost", ".internal")):
        raise ValueError("Private hosts are not allowed")
    addresses = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    ips = {row[4][0] for row in addresses}
    if not ips or not all(ipaddress.ip_address(ip).is_global for ip in ips):
        raise ValueError("Private or unroutable addresses are not allowed")
    path = parsed.path or "/"
    if parsed.query:
        path += "?" + parsed.query
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
                "Accept-Encoding": "identity", "User-Agent": "AgenticRAG/0.4 (+private research)",
            })
            response = connection.getresponse()
            if response.status in {301, 302, 303, 307, 308}:
                location = response.getheader("Location")
                if not location:
                    raise ValueError("Redirect had no destination")
                current = urljoin(current, location)
                continue
            if response.status != 200:
                raise ValueError("Page could not be read")
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
            chosen = parser.content_parts if len("".join(parser.content_parts)) >= 80 else (
                parser.main_parts if len("".join(parser.main_parts)) >= 80 else parser.parts
            )
            text = " ".join(" ".join(chosen).split())
        if len(text) < 80:
            raise ValueError("Page has too little readable text")
        return current, text[:MAX_PAGE_CHARS]
    raise ValueError("Too many redirects")
