from fastapi import APIRouter, Request

from ..schemas import BackupStatus

router = APIRouter(prefix="/api/backup")


@router.get("")
async def status(request: Request) -> BackupStatus:
    return request.app.state.backups.status()  # type: ignore[no-any-return]


@router.post("")
async def make(request: Request) -> BackupStatus:
    return await request.app.state.backups.make()  # type: ignore[no-any-return]
