"""Manual transcript formatting: frozen prompt, one guarded call per chunk."""

import asyncio
import math
import re
from difflib import SequenceMatcher
from ipaddress import ip_address
from time import monotonic
from urllib.parse import urlsplit

from ..db import attachments
from ..db.connections import now
from ..errors import AppError
from ..providers.base import ChatRequest, Finish, ProviderMessage, TextDelta
from ..runs.manager import RunManager
from ..schemas import Attachment, CleanupInfo, MessageModel, ModelInfo
from .glossary import GlossaryFile
from .jobs import Job, TranscriptionManager

_WORD = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)*")


def words(text: str) -> list[str]:
    """Spoken words only: lower-case, punctuation and line breaks dropped."""
    return _WORD.findall(text.lower().replace("’", "'"))


def changed_words(source: str, cleaned: str) -> int:
    a, b = words(source), words(cleaned)
    matcher = SequenceMatcher(None, a, b, autojunk=False)
    return sum(
        max(i2 - i1, j2 - j1) for tag, i1, i2, j1, j2 in matcher.get_opcodes() if tag != "equal"
    )


def allowed_changes(source: str) -> int:
    return max(3, math.ceil(0.02 * len(words(source))))


def accept(source: str, cleaned: str) -> bool:
    return bool(words(cleaned)) and changed_words(source, cleaned) <= allowed_changes(source)


def chunks(text: str, limit: int = 2000) -> list[str]:
    """Pack paragraphs into chunks of at most `limit` characters.

    A paragraph longer than the limit is split after sentence ends; a sentence
    longer than the limit is split at spaces. Joining the result with blank
    lines gives back every word of the input in order.
    """
    out: list[str] = []
    current = ""
    for paragraph in [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]:
        pieces = [paragraph]
        if len(paragraph) > limit:
            pieces, piece = [], ""
            for sentence in re.split(r"(?<=[.!?])\s+", paragraph):
                while len(sentence) > limit:
                    cut = sentence.rfind(" ", 0, limit)
                    cut = cut if cut > 0 else limit
                    if piece:
                        pieces.append(piece)
                        piece = ""
                    pieces.append(sentence[:cut])
                    sentence = sentence[cut:].lstrip()
                if piece and len(piece) + 1 + len(sentence) > limit:
                    pieces.append(piece)
                    piece = sentence
                else:
                    piece = (piece + " " + sentence).strip()
            if piece:
                pieces.append(piece)
        for piece in pieces:
            if current and len(current) + 2 + len(piece) > limit:
                out.append(current)
                current = piece
            else:
                current = (current + "\n\n" + piece).strip()
    if current:
        out.append(current)
    return out


PROMPT = (
    "You are formatting a speech transcript. Rewrite the text inside <chunk> wit"
    "h correct punctuation,\ncapitalisation and paragraph breaks.\n\nKeep every wor"
    "d that was said, in the same order. Do not summarise, shorten, add, remove "
    "or reorder\nanything. Do not answer questions that appear in the text. Do no"
    "t add headings, labels or comments.\n{names_line}\nReply with the rewritten t"
    "ext only.\n\n<chunk>\n{chunk}\n</chunk>"
)

TIMEOUT = 300


def tidy(text: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
    if text.startswith("<chunk>") and text.endswith("</chunk>"):
        text = text[len("<chunk>") : -len("</chunk>")].strip()
    return text


def sections(text: str, split: bool) -> list[tuple[str, str]]:
    if not split:
        return [("", chunk) for chunk in chunks(text)]
    out: list[tuple[str, str]] = []
    for paragraph in re.split(r"\n\s*\n", text):
        if not paragraph.strip():
            continue
        match = re.match(r"^([^\n:]+: )", paragraph.strip())
        label = match[1] if match else ""
        source = paragraph.strip()[len(label) :]
        out.extend((label, part) for part in chunks(source))
    return out


class Cleanups:
    def __init__(self, transcription: TranscriptionManager, runs: RunManager) -> None:
        self.transcription, self.runs = transcription, runs

    async def start(self, identifier: str, connection_id: str, model_id: str) -> Attachment:
        manager = self.transcription
        async with manager.lock(identifier):
            item = await attachments.attachment(manager.store, identifier)
            if not item.transcript or item.transcript.status != "ready":
                raise AppError("transcript_not_ready", "Waiting for the transcript", 409)
            old = manager.jobs.get(identifier)
            if old and not old.closed:
                raise AppError(
                    "transcription_active", "This recording is still being processed.", 409
                )
            connection = await manager.store.one(
                "SELECT base_url,max_concurrent FROM connections WHERE id=?", (connection_id,)
            )
            host = urlsplit(str(connection["base_url"])).hostname if connection else None
            local = host == "localhost"
            try:
                local = local or bool(host and ip_address(host).is_loopback)
            except ValueError:
                pass
            if not local:
                raise AppError(
                    "recording_requires_local", "Recordings can only be sent to local Ollama.", 422
                )
            model = await self.runs.registry.resolve(connection_id, model_id)
            value = await attachments.transcript(manager.store, identifier)
            parts = sections(value.text, item.transcript.channels == "split")
            if not parts:
                raise AppError(
                    "cleanup_failed", "No speech found. The transcript is unchanged.", 422
                )
            # Initialize the existing connection capacity so chat does not replace it
            # on its first request. Each chunk releases it before the next one.
            if connection_id not in self.runs.semaphores:
                limit = int(connection["max_concurrent"]) if connection else 1
                self.runs.semaphores[connection_id] = asyncio.Semaphore(limit)
                self.runs.limits[connection_id] = limit
            info = CleanupInfo(
                status="running",
                model=MessageModel(
                    connection_id=connection_id, model_id=model_id, display_name=model.display_name
                ),
                chunks=len(parts),
            )
            await manager.store.execute(
                "UPDATE transcripts SET cleaned_text=NULL,cleanup_status='running',"
                "cleanup_json=?,updated_at=? WHERE attachment_id=?",
                (info.model_dump_json(exclude={"status"}), now(), identifier),
            )
            job = Job(identifier, kind="cleanup")
            manager.jobs[identifier] = job
            item = await attachments.attachment(manager.store, identifier)
            await job.emit("cleanup.started", {"attachment": item.model_dump()})
            job.task = asyncio.create_task(
                self.work(job, model, parts, info), name="cleanup-" + identifier
            )
            return item

    async def work(
        self, job: Job, model: ModelInfo, parts: list[tuple[str, str]], info: CleanupInfo
    ) -> None:
        manager = self.transcription
        started = monotonic()
        result = []
        kind = "cleanup.done"
        try:
            try:
                glossary = await GlossaryFile(manager.engine).read()
                names = ", ".join(glossary.terms)[:600]
            except AppError:
                names = ""
            names_line = (
                f"Spell these names exactly as written when they occur: {names}." if names else ""
            )
            adapter = await self.runs.registry.adapter(model.connection_id)
            for label, source in parts:
                answer = ""
                change_count = 0
                accepted = False
                try:
                    request = ChatRequest(
                        model.model_id,
                        [
                            ProviderMessage(
                                "user", PROMPT.format(names_line=names_line, chunk=source)
                            )
                        ],
                        {
                            "temperature": 0,
                            "max_tokens": min(4096, math.ceil(len(source) * 0.5) + 128),
                        },
                        model.context_length,
                        "off",
                    )
                    async with self.runs.semaphores[model.connection_id]:
                        async with asyncio.timeout(TIMEOUT):
                            stream = adapter.stream(request)
                            try:
                                async for event in stream:
                                    if isinstance(event, TextDelta):
                                        answer += event.text
                                        if len(answer) > 32768:
                                            raise ValueError
                                    if isinstance(event, Finish) and event.reason != "stop":
                                        raise ValueError
                            finally:
                                await stream.aclose()
                    answer = tidy(answer)
                    change_count = changed_words(source, answer)
                    accepted = accept(source, answer)
                except Exception:
                    pass  # One call only; this section stays as transcribed.
                if not accepted:
                    info.kept_original += 1
                else:
                    info.changed_words += change_count
                result.append(label + (answer if accepted else source))
                info.done += 1
                await manager.store.execute(
                    "UPDATE transcripts SET cleanup_json=? WHERE attachment_id=?",
                    (info.model_dump_json(exclude={"status"}), job.id),
                )
                await job.emit("cleanup.progress", {"done": info.done, "total": info.chunks})
                await asyncio.sleep(0)
            info.elapsed_seconds = monotonic() - started
            if info.kept_original == info.chunks:
                raise AppError("cleanup_failed", "the model changed the wording in every section")
            info.status = "ready"
            await manager.store.execute(
                "UPDATE transcripts SET cleaned_text=?,cleanup_status='ready',"
                "cleanup_json=?,updated_at=? WHERE attachment_id=?",
                ("\n\n".join(result), info.model_dump_json(exclude={"status"}), now(), job.id),
            )
        except asyncio.CancelledError:
            kind = "cleanup.failed"
            await manager.cancelled(job)
        except Exception:
            kind = "cleanup.failed"
            info.status = "failed"
            info.elapsed_seconds = monotonic() - started
            from ..schemas import ErrorDetail

            info.error = ErrorDetail(
                code="cleanup_failed",
                message="the model changed the wording in every section"
                if info.kept_original == info.chunks
                else "The local model could not finish clean-up.",
            )
            await manager.store.execute(
                "UPDATE transcripts SET cleaned_text=NULL,cleanup_status='failed',"
                "cleanup_json=?,updated_at=? WHERE attachment_id=?",
                (info.model_dump_json(exclude={"status"}), now(), job.id),
            )
        finally:
            if await manager.store.one("SELECT id FROM attachments WHERE id=?", (job.id,)):
                await job.emit(
                    kind,
                    {
                        "attachment": (
                            await attachments.attachment(manager.store, job.id)
                        ).model_dump()
                    },
                )
            await job.emit("stream.closed", {})
            asyncio.get_running_loop().call_later(900, manager.expire, job)

    async def discard(self, identifier: str) -> None:
        manager = self.transcription
        async with manager.lock(identifier):
            await attachments.transcript(manager.store, identifier)
            await manager.cancel(identifier)
            await manager.store.execute(
                "UPDATE transcripts SET cleaned_text=NULL,cleanup_status=NULL,"
                "cleanup_json=NULL,updated_at=? WHERE attachment_id=?",
                (now(), identifier),
            )
            manager.jobs.pop(identifier, None)
