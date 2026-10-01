"""All outbound page reads use public-address validation and pinned TLS."""

import asyncio
import http.client
import ipaddress
import socket
import ssl
import threading
import zlib
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote, urljoin, urlsplit


class _PinnedHTTPS(http.client.HTTPSConnection):
    _context: ssl.SSLContext

    def __init__(self, host: str, ip: str, timeout: float) -> None:
        mac_ca_bundle = Path("/etc/ssl/cert.pem")
        context = ssl.create_default_context(
            cafile=str(mac_ca_bundle) if mac_ca_bundle.is_file() else None
        )
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
    return host, sorted(ips)[0], path  # type: ignore[return-value]


@dataclass
class RawPage:
    url: str
    data: bytes
    content_type: str


def fetch_public(
    url: str,
    limit: int = 3_000_000,
    cancelled: threading.Event | None = None,
    connections: list[_PinnedHTTPS] | None = None,
) -> RawPage:
    current = url
    for hop in range(6):
        if cancelled and cancelled.is_set():
            raise ValueError("cancelled")
        try:
            host, ip, path = _public_address(current)
        except ValueError as exc:
            raise ValueError("not a public address") from exc
        connection = _PinnedHTTPS(host, ip, 4.0)
        if connections is not None:
            connections.append(connection)
        try:
            if cancelled and cancelled.is_set():
                raise ValueError("cancelled")
            connection.connect()
            if connection.sock:
                connection.sock.settimeout(6.0)
            connection.request(
                "GET",
                path,
                headers={
                    "Host": host,
                    "Accept": (
                        "text/html,application/xhtml+xml,text/plain;q=0.9,application/pdf;q=0.8"
                    ),
                    "Accept-Encoding": "gzip",
                    "Accept-Language": "en-US,en;q=0.8",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Workbench/1.0",
                },
            )
            response = connection.getresponse()
            if response.status in {301, 302, 303, 307, 308}:
                location = response.getheader("Location")
                if not location:
                    raise ValueError("redirect has no destination")
                if hop == 5:
                    raise ValueError("too many redirects")
                current = urljoin(current, location)
                continue
            if response.status != 200:
                raise ValueError(f"HTTP {response.status}")
            raw = response.read(limit + 1)
            if len(raw) > limit:
                raise ValueError("too large")
            if response.getheader("Content-Encoding", "").lower() == "gzip":
                decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
                raw = decoder.decompress(raw, 10_000_001)
                if len(raw) > 10_000_000 or decoder.unconsumed_tail:
                    raise ValueError("too large")
                if not decoder.eof:
                    raise ValueError("invalid compressed page")
            return RawPage(current, raw, response.getheader("Content-Type", ""))
        finally:
            connection.close()
    raise ValueError("too many redirects")


async def read_network(url: str, limit: int = 3_000_000) -> RawPage:
    cancelled = threading.Event()
    connections: list[_PinnedHTTPS] = []
    try:
        return await asyncio.to_thread(fetch_public, url, limit, cancelled, connections)
    except asyncio.CancelledError:
        cancelled.set()
        for connection in connections:
            if connection.sock:
                try:
                    connection.sock.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
            connection.close()
        raise
