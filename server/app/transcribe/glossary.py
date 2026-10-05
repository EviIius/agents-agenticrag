"""Private engine glossary, using only the path reported by doctor."""

import asyncio
import os
import tempfile
from pathlib import Path

from ..errors import AppError
from ..schemas import Glossary
from .engine import Engine

LIMIT = 65536


def validate(text: str) -> str:
    try:
        encoded = text.encode("utf-8")
    except UnicodeError:
        raise AppError("validation_error", "Glossary must be valid UTF-8 text.", 422) from None
    if len(encoded) > LIMIT or "\0" in text:
        raise AppError(
            "validation_error", "Glossary can be up to 64 KB and cannot contain NUL bytes.", 422
        )
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")
    normalized += "\n"
    if len(normalized.encode("utf-8")) > LIMIT:
        raise AppError("validation_error", "Glossary can be up to 64 KB.", 422)
    return normalized


def terms(text: str) -> list[str]:
    result = []
    for raw in text.splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            correct = line.partition("=")[0].strip()
            if correct:
                result.append(correct)
    return result


class GlossaryFile:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.lock = asyncio.Lock()

    async def path(self) -> Path:
        status = await self.engine.status()
        value = self.engine.paths.get("glossary")
        if not status.configured or not value or not self.engine.home:
            raise AppError(
                "transcription_unavailable", "Recordings need the transcription engine", 422
            )
        path = Path(value).expanduser()
        return (path if path.is_absolute() else self.engine.home / path).resolve()

    async def read(self) -> Glossary:
        async with self.lock:
            try:
                path = await self.path()
                if not path.exists():
                    return Glossary(text="", terms=[])
                with path.open("rb") as handle:
                    raw = handle.read(LIMIT + 1)
                if len(raw) > LIMIT:
                    raise ValueError
                text = raw.decode("utf-8")
                if "\0" in text:
                    raise ValueError
                return Glossary(text=text, terms=terms(text))
            except (OSError, UnicodeError, ValueError):
                raise AppError(
                    "glossary_failed", "Couldn't read the glossary. Check setup and try again.", 422
                ) from None

    async def write(self, text: str) -> Glossary:
        normalized = validate(text)
        async with self.lock:
            part: Path | None = None
            try:
                path = await self.path()
                fd, name = tempfile.mkstemp(prefix=".glossary-", suffix=".part", dir=path.parent)
                part = Path(name)
                with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                    handle.write(normalized)
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(part, path)
                self.engine.cached = None
                return Glossary(text=normalized, terms=terms(normalized))
            except OSError:
                raise AppError(
                    "glossary_failed",
                    "Couldn't save the glossary. Your terms are unchanged. Try again.",
                    422,
                ) from None
            finally:
                if part:
                    part.unlink(missing_ok=True)
