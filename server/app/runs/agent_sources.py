"""Stable per-run numbering and existing source storage/rendering; no evidence selector."""

import json
from typing import Literal

from ..db.core import Store
from ..library.prompt import build as library_block
from ..providers.base import ChatRequest, ProviderMessage
from ..schemas import Source, WebRead
from ..search.merge import canonical
from ..search.prompt import build as web_block


class Sources:
    def __init__(self, store: Store, message_id: str, kind: Literal["web", "library"]) -> None:
        self.store, self.message_id, self.kind = store, message_id, kind
        self.values: dict[tuple[object, ...], Source] = {}

    async def add(self, incoming: list[Source]) -> str:
        returned = []
        for value in incoming:
            key = (
                (value.document_id, value.page_start, value.page_end)
                if self.kind == "library"
                else (canonical(value.url),)
            )
            old = self.values.get(key)
            source = value.model_copy(
                deep=True, update={"n": old.n if old else len(self.values) + 1, "cited": False}
            )
            # A repeated snippet must not downgrade evidence from a page already read.
            if old and old.kind == "page" and source.kind == "snippet":
                source = old
            returned.append(source)
            if self.kind == "web":
                await self.store.execute(
                    "INSERT OR REPLACE INTO message_sources "
                    "(message_id,n,url,title,site_name,published_at,kind,passages_json,cited) "
                    "VALUES (?,?,?,?,?,?,?,?,?)",
                    (
                        self.message_id,
                        source.n,
                        source.url,
                        source.title,
                        source.site_name,
                        source.published_at,
                        source.kind,
                        json.dumps([p.model_dump() for p in source.passages]),
                        int(source.cited),
                    ),
                )
            else:
                await self.store.execute(
                    "INSERT OR REPLACE INTO message_library_sources "
                    "(message_id,n,document_id,filename,page_start,page_end,passages_json,cited) "
                    "VALUES (?,?,?,?,?,?,?,?)",
                    (
                        self.message_id,
                        source.n,
                        source.document_id,
                        source.title,
                        source.page_start,
                        source.page_end,
                        json.dumps(
                            [
                                {
                                    "text": p.text,
                                    "heading": p.heading,
                                    "page_start": p.page_start,
                                    "page_end": p.page_end,
                                }
                                for p in source.passages
                            ]
                        ),
                        int(source.cited),
                    ),
                )
            self.values[key] = source
        request = ChatRequest("", [ProviderMessage("system", ""), ProviderMessage("user", "")])
        (web_block if self.kind == "web" else library_block)(request, returned)
        return request.messages[-1].content

    async def read(self, value: WebRead) -> None:
        await self.store.execute(
            "INSERT OR REPLACE INTO web_reads VALUES (?,?,?,?,?,?)",
            (self.message_id, value.url, value.title, value.site_name, value.status, value.reason),
        )
