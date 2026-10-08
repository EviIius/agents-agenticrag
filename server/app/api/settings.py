from typing import Any

from fastapi import APIRouter, Request

from ..config import APP_NAME, VERSION
from ..db import settings
from ..errors import AppError
from ..schemas import AttachmentExtensions, Bootstrap
from ..search.providers import Providers
from .attachments import DOCUMENT, TEXT
from .connections import listing

router = APIRouter(prefix="/api")


@router.get("/bootstrap")
async def bootstrap(request: Request) -> Bootstrap:
    values = await settings.get(request.app.state.store)
    service = Providers(request.app.state.store, values, request.app.state.search.fixtures)
    return Bootstrap(
        attachment_extensions=AttachmentExtensions(text=sorted(TEXT), document=sorted(DOCUMENT)),
        app_name=APP_NAME,
        version=VERSION,
        data_dir=str(request.app.state.config.data_dir.expanduser().resolve()),
        settings=await settings.get(request.app.state.store, True),
        connections=await listing(request),
        features={
            "library": bool(request.app.state.library.available),
            "web_search": any(service.configured(p) for p in values["web.provider_order"]),
            "transcription": (await request.app.state.transcription.engine.status()).ready,
        },
    )


@router.get("/settings")
async def get(request: Request) -> dict[str, Any]:
    return await settings.get(request.app.state.store, True)


@router.patch("/settings")
async def patch(body: dict[str, Any], request: Request) -> dict[str, Any]:
    try:
        if any(k.startswith("library.") for k in body):
            await request.app.state.library.preferences(body)
        else:
            await settings.patch(request.app.state.store, body)
    except (ValueError, TypeError) as exc:
        raise AppError("validation_error", str(exc), 422) from exc
    return await get(request)
