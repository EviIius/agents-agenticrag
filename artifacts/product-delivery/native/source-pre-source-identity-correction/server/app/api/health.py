from fastapi import APIRouter

from ..schemas import ErrorResponse, Health

router = APIRouter(prefix="/api")


@router.get("/health", response_model=Health, responses={403: {"model": ErrorResponse}})
async def health() -> Health:
    return Health()
