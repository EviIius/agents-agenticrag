import asyncio
import re
from time import monotonic
from urllib.parse import urlsplit

from fastapi import APIRouter, Request
from fastapi.responses import Response

from ..db import settings
from ..db.connections import now
from ..errors import AppError
from ..schemas import SearchStatus, SearchTest, SearchTestResult
from ..search.fetch import read_network
from ..search.providers import Providers

router = APIRouter(prefix="/api")


def providers(request: Request) -> Providers:
    return Providers(request.app.state.store, {}, request.app.state.search.fixtures)


@router.get("/search/status")
async def status(request: Request) -> list[SearchStatus]:
    service = providers(request)
    service.values = await settings.get(service.store)
    return await service.status()


@router.post("/search/test")
async def test(body: SearchTest, request: Request) -> SearchTestResult:
    service = providers(request)
    service.values = await settings.get(service.store)
    clock = monotonic()
    try:
        results = await service.request(body.provider, "test", "any")
        return SearchTestResult(
            ok=bool(results), results=results[:3], ms=(monotonic() - clock) * 1000
        )
    except Exception as exc:
        return SearchTestResult(
            ok=False, results=[], ms=(monotonic() - clock) * 1000, error=str(exc)[:200]
        )


@router.get("/favicon/{domain}")
async def favicon(domain: str, request: Request) -> Response:
    try:
        host = domain.encode("idna").decode("ascii").lower()
    except UnicodeError as exc:
        raise AppError("not_found", "Favicon unavailable.", 404) from exc
    if not re.fullmatch(r"[a-z0-9.-]{1,253}", host) or urlsplit("https://" + host).hostname != host:
        raise AppError("not_found", "Favicon unavailable.", 404)
    store = request.app.state.store
    if request.app.state.search.fixtures.directory:
        raise AppError("not_found", "Favicon unavailable in fixtures.", 404)
    cached = await store.one("SELECT * FROM favicons WHERE domain=?", (host,))
    if cached:
        if not cached["data"]:
            raise AppError("not_found", "Favicon unavailable.", 404)
        return Response(
            bytes(cached["data"]),
            media_type=str(cached["mime_type"]),
            headers={"Cache-Control": "private, max-age=86400"},
        )
    try:
        async with asyncio.timeout(8):
            raw = await read_network("https://" + host + "/favicon.ico", 65536)
        mime = raw.content_type.split(";", 1)[0].lower()
        if mime not in (
            "image/png",
            "image/x-icon",
            "image/vnd.microsoft.icon",
            "image/jpeg",
            "image/gif",
            "image/webp",
        ):
            raise ValueError("unsupported type")
        await store.execute(
            "INSERT OR REPLACE INTO favicons VALUES (?,?,?,?)", (host, mime, raw.data, now())
        )
        return Response(
            raw.data, media_type=mime, headers={"Cache-Control": "private, max-age=86400"}
        )
    except Exception as exc:
        await store.execute("INSERT OR REPLACE INTO favicons VALUES (?,NULL,NULL,?)", (host, now()))
        raise AppError("not_found", "Favicon unavailable.", 404) from exc
