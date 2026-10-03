"""The external engine boundary. Never log filenames, output or stderr."""

import asyncio
import json
import os
import re
import signal
from pathlib import Path
from time import monotonic
from typing import Any

from ..errors import AppError
from ..schemas import EngineCheck, TranscriptionStatus

AUDIO = {
    ".aac",
    ".aif",
    ".aiff",
    ".amr",
    ".caf",
    ".flac",
    ".m4a",
    ".mka",
    ".mov",
    ".mp3",
    ".mp4",
    ".oga",
    ".ogg",
    ".opus",
    ".wav",
    ".webm",
    ".wma",
}


class Engine:
    def __init__(self, home: Path | None) -> None:
        self.home = home.expanduser().resolve() if home else None
        self.cached: TranscriptionStatus | None = None
        self.checked = 0.0
        self.paths: dict[str, str] = {}

    async def status(self, refresh: bool = False) -> TranscriptionStatus:
        if self.cached is not None and not refresh and monotonic() - self.checked < 30:
            return self.cached
        reason = "Set WORKBENCH_TRANSCRIBE_HOME to the transcription engine folder."
        configured = bool(self.home and os.access(self.home / "bin/transcribe", os.X_OK))
        try:
            if not configured:
                raise ValueError(reason)
            assert self.home is not None
            child = await asyncio.create_subprocess_exec(
                str(self.home / "bin/transcribe"),
                "doctor",
                "--json",
                cwd=self.home,
                stdin=asyncio.subprocess.DEVNULL,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
                start_new_session=True,
            )
            try:
                stdout, _ = await asyncio.wait_for(child.communicate(), 20)
            except (TimeoutError, asyncio.CancelledError):
                await self.stop(child)
                raise
            data = json.loads(stdout)
            self.paths = data.get("paths", {})
            # Expose checks, never glossary content or a writable program path.
            glossary: dict[str, Any] = next(
                (c for c in data["checks"] if c["name"] == "glossary"), {}
            )
            count = re.search(r"\((\d+) terms?\)", glossary.get("detail", ""))
            status = TranscriptionStatus(
                configured=True,
                ready=bool(data["ok"] and child.returncode == 0),
                version=data["version"],
                checks=data["checks"],
                glossary_terms=int(count[1]) if count else 0,
                audio_extensions=sorted(set(data["audio_extensions"]) & AUDIO),
            )
        except asyncio.CancelledError:
            raise
        except Exception:
            status = TranscriptionStatus(
                configured=False,
                ready=False,
                checks=[
                    EngineCheck(
                        name="engine",
                        ok=False,
                        blocking=True,
                        detail=reason
                        if not configured
                        else "The engine setup check failed or timed out.",
                    )
                ],
                audio_extensions=sorted(AUDIO),
            )
        self.cached, self.checked = status, monotonic()
        return status

    @staticmethod
    async def stop(child: asyncio.subprocess.Process) -> None:
        if child.returncode is not None:
            return
        try:
            child.send_signal(signal.SIGTERM)
            await asyncio.wait_for(child.wait(), 10)
        except ProcessLookupError:
            pass
        except TimeoutError:
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            await child.wait()

    async def run(self, audio: Path, out_dir: Path, channels: str) -> dict[str, Any]:
        if not (await self.status()).ready:
            raise AppError(
                "transcription_unavailable", "Recordings need the transcription engine", 422
            )
        assert self.home is not None
        args = [
            str(self.home / "bin/transcribe"),
            "run",
            str(audio),
            "--out-dir",
            str(out_dir),
            "--quiet",
        ]
        if channels == "split":
            args += ["--channels", "split"]
        child = await asyncio.create_subprocess_exec(
            *args,
            cwd=self.home,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE,
            start_new_session=True,
        )
        tail = bytearray()

        async def drain() -> None:
            assert child.stderr is not None
            while chunk := await child.stderr.read(4096):
                tail.extend(chunk)
                del tail[:-8192]

        reader = asyncio.create_task(drain())
        try:
            try:
                await asyncio.wait_for(child.wait(), 4 * 3600)
                await reader
            except TimeoutError:
                await self.stop(child)
                raise AppError(
                    "transcription_failed", "The recording exceeded the four-hour processing limit."
                ) from None
            if child.returncode == 130:
                raise asyncio.CancelledError
            if child.returncode != 0:
                lines = tail.decode("utf-8", errors="replace").splitlines()
                detail = next(
                    (line.strip() for line in reversed(lines) if line.strip()), "The engine failed."
                )
                detail = detail.removeprefix("Transcription failed: ")[:300]
                raise AppError("transcription_failed", detail)
            try:
                result = json.loads((out_dir / (audio.stem + ".json")).read_text())
                if not isinstance(result["text"], str) or not isinstance(result["raw_text"], str):
                    raise ValueError
                from ..schemas import TranscriptSegment

                for segment in result["segments"]:
                    TranscriptSegment.model_validate(segment)
                return dict(result)
            except (OSError, ValueError, KeyError, TypeError):
                raise AppError(
                    "transcription_failed", "The engine did not produce a valid transcript."
                ) from None
        except asyncio.CancelledError:
            await self.stop(child)
            raise
        finally:
            reader.cancel()
            await asyncio.gather(reader, return_exceptions=True)
