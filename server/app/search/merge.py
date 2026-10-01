import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from ..schemas import SearchResult


def canonical(url: str) -> str:
    p = urlsplit(url)
    if (
        p.scheme.lower() not in ("http", "https")
        or not p.hostname
        or p.username
        or p.password
        or p.port not in (None, 443)
    ):
        return ""
    host = p.hostname.lower().removeprefix("www.").encode("idna").decode("ascii")
    if ":" in host:
        host = "[" + host + "]"
    query = urlencode(
        [
            (k, v)
            for k, v in parse_qsl(p.query, keep_blank_values=True)
            if not k.lower().startswith("utm_")
            and k.lower() not in {"gclid", "fbclid", "ref", "ref_src"}
        ]
    )
    return urlunsplit(("https", host, p.path.rstrip("/") or "/", query, ""))


def merge(results: list[list[SearchResult]], blocked: list[str]) -> list[SearchResult]:
    scores: dict[str, float] = {}
    rows: dict[str, SearchResult] = {}
    for batch in results:
        seen: set[str] = set()
        for rank, result in enumerate(batch, 1):
            try:
                url = canonical(result.url)
            except (ValueError, UnicodeError):
                continue
            host = urlsplit(url).hostname or ""
            if (
                not url
                or url in seen
                or re.search(r"\.(zip|exe|dmg|mp4|mp3|jpg|png|gif)$", urlsplit(url).path, re.I)
                or any(
                    host == d.lower().strip() or host.endswith("." + d.lower().strip())
                    for d in blocked
                    if d.strip()
                )
            ):
                continue
            seen.add(url)
            scores[url] = scores.get(url, 0) + 1 / (60 + rank)
            rows.setdefault(url, result.model_copy(update={"url": url}))
    counts: dict[str, int] = {}
    out: list[SearchResult] = []
    for url in sorted(scores, key=lambda u: (-scores[u], u)):
        host = urlsplit(url).hostname or ""
        if counts.get(host, 0) >= 2:
            continue
        counts[host] = counts.get(host, 0) + 1
        out.append(rows[url])
        if len(out) == 10:
            break
    return out
