from fastapi import APIRouter, Request

from ..db import folders
from ..schemas import Folder, FolderCreate, FolderPatch

router = APIRouter(prefix="/api/folders")


@router.get("")
async def listing(request: Request) -> list[Folder]:
    return await folders.listing(request.app.state.store)


@router.post("", status_code=201)
async def create(body: FolderCreate, request: Request) -> Folder:
    return await folders.create(request.app.state.store, body)


@router.patch("/{identifier}")
async def patch(identifier: str, body: FolderPatch, request: Request) -> Folder:
    return await folders.patch(request.app.state.store, identifier, body)


@router.delete("/{identifier}", status_code=204)
async def delete(identifier: str, request: Request) -> None:
    await folders.delete(request.app.state.store, identifier)
