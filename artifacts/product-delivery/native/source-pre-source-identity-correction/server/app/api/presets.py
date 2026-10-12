from fastapi import APIRouter, Request

from ..db import presets
from ..schemas import Preset, PresetCreate, PresetPatch

router = APIRouter(prefix="/api/presets")


@router.get("")
async def listing(request: Request) -> list[Preset]:
    return await presets.listing(request.app.state.store)


@router.post("", status_code=201)
async def create(body: PresetCreate, request: Request) -> Preset:
    return await presets.create(request.app.state.store, body)


@router.patch("/{identifier}")
async def patch(identifier: str, body: PresetPatch, request: Request) -> Preset:
    return await presets.patch(request.app.state.store, identifier, body)


@router.delete("/{identifier}", status_code=204)
async def delete(identifier: str, request: Request) -> None:
    await presets.delete(request.app.state.store, identifier)
