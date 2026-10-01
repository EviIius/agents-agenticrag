import asyncio
import re
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from ..providers.base import Adapter, ChatRequest, ProviderMessage

PROMPT = (
    "You write web search queries for an assistant. Today is {Weekday, Mont"
    "h D, YYYY}.\nDecide whether searching the web would help answer the use"
    "r's latest message, and if so write up to 3 queries.\n\nRules:\n- search="
    "false only for small talk, requests to rewrite/translate/summarize tex"
    "t already in this conversation, creative writing, or pure math/code wi"
    "th no facts to look up.\n- Queries must stand alone: resolve pronouns a"
    'nd references from the conversation (e.g. "what about 2019?" → "2019 N'
    'BA Finals result").\n- Write keywords a search engine understands, not '
    "full sentences. Keep names, numbers, versions and quoted phrases exact"
    ".\n- 1 query for a simple lookup. 2–3 only for questions with separate "
    'parts or comparisons.\n- freshness: "day" or "week" for news, prices, s'
    'cores, releases, weather; "month" or "year" for recent developments; o'
    'therwise "any".\nReply with JSON only.'
)


class Plan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    search: bool
    queries: list[str] = Field(max_length=3)
    freshness: Literal["any", "day", "week", "month", "year"]


SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["search", "queries", "freshness"],
    "properties": {
        "search": {"type": "boolean"},
        "queries": {
            "type": "array",
            "maxItems": 3,
            "items": {"type": "string", "minLength": 2, "maxLength": 120},
        },
        "freshness": {"type": "string", "enum": ["any", "day", "week", "month", "year"]},
    },
}


def heuristic(latest: str, history: list[ProviderMessage]) -> str:
    previous = next((m.content for m in reversed(history) if m.role == "user"), "")
    if len(latest.split()) < 6 and re.search(
        r"\b(it|that|those|they|this|what about|and)\b", latest, re.I
    ):
        latest = previous[:120] + " " + latest
    return latest[:200].strip()


async def plan(
    adapter: Adapter,
    model: str,
    latest: str,
    history: list[ProviderMessage],
    loaded: bool,
    context: int | None,
    force: bool = False,
) -> tuple[Plan, bool]:
    transcript = "\n".join(
        m.role.title() + ": " + re.sub(r"\[\d+\]", "", m.content)[:600]
        for m in history[-6:]
        if m.role in ("user", "assistant")
    )
    req = ChatRequest(
        model,
        [
            ProviderMessage(
                "system",
                PROMPT.format(
                    **{
                        "Weekday, Month D, YYYY": datetime.now()
                        .astimezone()
                        .strftime("%A, %B %-d, %Y")
                    }
                ),
            ),
            ProviderMessage(
                "user",
                "Conversation so far:\n"
                + transcript
                + "\n\nLatest user message:\n"
                + latest[:2000],
            ),
        ],
        {"temperature": 0.2, "max_tokens": 256},
        context,
        "off",
        SCHEMA,
    )
    try:
        async with asyncio.timeout(20 if loaded else 60):
            raw = await adapter.complete_json(req)
        result = Plan.model_validate(raw, strict=True)
        queries: list[str] = []
        seen: set[str] = set()
        for q in result.queries:
            q = q.strip()
            if len(q) > 120 or (q and len(q) < 2):
                raise ValueError("Invalid query length")
            if q and q.casefold() not in seen:
                queries.append(q)
                seen.add(q.casefold())
        result.queries = queries
        if force:
            result.search = True
        if result.search and not queries:
            raise ValueError("No queries")
        return result, False
    except Exception:
        return Plan(search=True, queries=[heuristic(latest, history)], freshness="any"), True
