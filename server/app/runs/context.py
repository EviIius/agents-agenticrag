import re
from dataclasses import dataclass
from datetime import datetime
from html import escape
from ipaddress import ip_address
from pathlib import Path
from typing import Any, cast
from urllib.parse import urlsplit

from ..db.core import Store
from ..errors import AppError
from ..providers.base import ProviderMessage
from ..schemas import Chat, Message, ModelInfo


@dataclass
class Context:
    messages: list[ProviderMessage]
    used_tokens: int
    dropped: int
    reserve: int
    ratio: float
    has_recording: bool = False


def path(messages: list[Message], leaf: str | None) -> list[Message]:
    by_id = {m.id: m for m in messages}
    out: list[Message] = []
    visited: set[str] = set()
    while leaf and leaf in by_id and leaf not in visited:
        visited.add(leaf)
        msg = by_id[leaf]
        out.append(msg)
        leaf = msg.parent_id
    return list(reversed(out))


async def assemble(
    store: Store,
    data_dir: Path,
    chat: Chat,
    messages: list[Message],
    leaf: str | None,
    model: ModelInfo,
    params: dict[str, Any],
    settings: dict[str, Any],
) -> Context:
    pref = await store.one(
        "SELECT tokens_per_char FROM model_prefs WHERE connection_id=? AND model_id=?",
        (model.connection_id, model.model_id),
    )
    ratio = float(str(pref["tokens_per_char"])) if pref and pref["tokens_per_char"] else 0.3
    system = (
        chat.system_prompt if chat.system_prompt is not None else settings["default_system_prompt"]
    )
    if settings["include_current_date"]:
        system += (
            "\n\nCurrent date: " + datetime.now().astimezone().strftime("%A, %B %-d, %Y") + "."
        )
    selected = path(messages, leaf)
    has_recording = any(a.kind == "audio" for m in selected for a in m.attachments)
    if has_recording:
        connection = await store.one(
            "SELECT base_url FROM connections WHERE id=?", (model.connection_id,)
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
    last_users = {m.id for m in [m for m in selected if m.role == "user"][-3:]}
    output = [ProviderMessage("system", system)]
    for m in selected:
        if m.role == "assistant" and m.status in ("error", "interrupted"):
            continue
        content = re.sub(r"\[\d+\]", "", m.content) if m.role == "assistant" else m.content
        images: list[bytes] = []
        for attachment in m.attachments:
            row = await store.one("SELECT path FROM attachments WHERE id=?", (attachment.id,))
            if not row:
                continue
            file = (data_dir / str(row["path"])).resolve()
            if not file.is_relative_to(data_dir.resolve()):
                raise AppError("validation_error", "Invalid attachment path.")
            if attachment.kind == "text":
                content = (
                    f'<file name="{escape(attachment.filename, quote=True)}">'
                    + file.read_text(errors="replace")
                    + "</file>\n"
                    + content
                )
            elif attachment.kind == "audio":
                from ..db.attachments import best_text

                text, duration = await best_text(store, attachment.id)
                seconds = int(duration)
                clock = f"{seconds // 3600}:{seconds // 60 % 60:02}:{seconds % 60:02}"
                content = (
                    f'<transcript name="{escape(attachment.filename, quote=True)}" '
                    f'duration="{clock}">\n'
                    + text.replace("</transcript>", "&lt;/transcript&gt;")
                    + "\n</transcript>\n"
                    + content
                )
            elif m.id in last_users:
                images.append(file.read_bytes())
            else:
                content = "[image omitted]\n" + content
        output.append(ProviderMessage(cast(Any, m.role), content, images))
    maximum = model.context_length or 8192
    reserve = int(params.get("max_tokens") or max(1024, min(8192, maximum * 0.25)))
    available = maximum - reserve - 256

    def size() -> int:
        return sum(int(len(m.content) * ratio) + 800 * len(m.images) + 4 for m in output)

    dropped = 0
    while size() > available and len(output) > 2:
        output.pop(1)
        dropped += 1
    if size() > available:
        raise AppError(
            "context_overflow", "The latest message exceeds the model's context window.", 422
        )
    if any(m.images for m in output) and model.vision is not True:
        raise AppError("vision_required", "Images need a vision model.", 422)
    return Context(output, size(), dropped, reserve, ratio, has_recording)
