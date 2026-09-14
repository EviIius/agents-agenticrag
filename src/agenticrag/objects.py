from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path, PurePosixPath

from .errors import IngestionError


class LocalObjectStore:
    """Content-addressed immutable byte storage for original source objects."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def put_text(self, text: str) -> tuple[str, str]:
        return self.put_bytes(text.encode("utf-8"), suffix=".txt")

    def put_bytes(self, data: bytes, *, suffix: str = ".bin") -> tuple[str, str]:
        sha256 = hashlib.sha256(data).hexdigest()
        if not suffix.startswith(".") or not suffix[1:].isalnum():
            raise IngestionError("Object suffix must contain only an extension")
        relative = PurePosixPath(sha256[:2], sha256[2:4], f"{sha256}{suffix.lower()}")
        target = self._resolve(relative.as_posix())
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            self._verify(target, sha256)
            return relative.as_posix(), sha256

        temporary: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                dir=target.parent,
                prefix=f".{sha256}.",
                suffix=".tmp",
                delete=False,
            ) as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
                temporary = stream.name
            os.replace(temporary, target)
            temporary = None
        finally:
            if temporary is not None:
                Path(temporary).unlink(missing_ok=True)
        self._verify(target, sha256)
        return relative.as_posix(), sha256

    def get_text(self, relative_path: str, expected_sha256: str) -> str:
        try:
            return self.get_bytes(relative_path, expected_sha256).decode("utf-8")
        except UnicodeDecodeError as exc:
            raise IngestionError("Stored source object is not valid UTF-8") from exc

    def get_bytes(self, relative_path: str, expected_sha256: str) -> bytes:
        target = self._resolve(relative_path)
        self._verify(target, expected_sha256)
        return target.read_bytes()

    def _resolve(self, relative_path: str) -> Path:
        path = PurePosixPath(relative_path)
        if path.is_absolute() or ".." in path.parts:
            raise IngestionError("Object path must be a safe relative path")
        target = self.root.joinpath(*path.parts).resolve()
        if not target.is_relative_to(self.root):
            raise IngestionError("Object path escapes the configured object root")
        return target

    @staticmethod
    def _verify(path: Path, expected_sha256: str) -> None:
        if not path.is_file():
            raise IngestionError("Stored source object is missing")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected_sha256:
            raise IngestionError("Stored source object failed its SHA-256 integrity check")
