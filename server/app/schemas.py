from pydantic import BaseModel

from .config import VERSION


class Health(BaseModel):
    ok: bool = True
    version: str = VERSION


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
