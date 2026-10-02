import asyncio
import re
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from ..providers.base import Adapter, ChatRequest, ProviderMessage

PROMPT = (
    "You plan web searches; you do not answer the user's question.\nToday "
    "is {Weekday, Month D, YYYY}.\n\nDetermine the requested ACTION from th"
    "e latest user message. Use the conversation only to resolve referenc"
    "es.\n- Set search=false for greetings/thanks, rewriting or shortening"
    " existing text, translating supplied words, summarizing supplied tex"
    "t, fictional/creative writing, or pure math/code without external fa"
    "cts. Real names inside these tasks do not make them factual lookups."
    "\n- Set search=true when external factual information would help, inc"
    "luding stable facts and current information.\n- When search=false, re"
    "turn queries=[].\n\nWhen searching:\n- Condense the latest request into"
    " one standalone keyword query for a simple lookup. Use 2–3 queries o"
    "nly for separate parts or comparisons.\n- Preserve exactly the reques"
    "ted relationship, population, time span and inclusion conditions. An"
    " entity can meet a condition at one time and its opposite at another"
    ". Do not add exclusions or require that a condition holds at all tim"
    "es when the user asks whether it happened at any time.\n- Keep exact "
    "names, numbers, versions and quoted phrases. Resolve short follow-up"
    "s from the conversation.\n- A date naming a historical event does not"
    " require recent publications. Use freshness=any for historical/stabl"
    "e facts; day/week for current news, weather, prices, scores and rele"
    "ases; month/year for recent developments.\n\nFirst output task: lookup"
    ", transform, creative, calculate, or conversation. Lookup means exte"
    "rnal facts are requested, even when you already know the answer. Tra"
    "nsform means edit, shorten, translate or summarize supplied text. Cr"
    "eative means compose fictional text. Calculate means pure math/code."
    " Conversation means small talk or thanks. Only lookup needs queries;"
    " all other tasks have queries=[] and freshness=any. Return JSON only"
    " with task, queries and freshness. For release notes use freshness=w"
    "eek; reserve day for today's changing conditions.\nFor comparisons of"
    " entities, use one query per entity covering every requested propert"
    "y of that entity. Cover all requested properties within the three-qu"
    "ery limit; do not spend all query slots on only some properties."
)


class Plan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    search: bool
    queries: list[str] = Field(max_length=3)
    freshness: Literal["any", "day", "week", "month", "year"]


class Intent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    task: Literal["lookup", "transform", "creative", "calculate", "conversation"]
    queries: list[str] = Field(max_length=3)
    freshness: Literal["any", "day", "week", "month", "year"]


SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["task", "queries", "freshness"],
    "properties": {
        "task": {
            "type": "string",
            "enum": ["lookup", "transform", "creative", "calculate", "conversation"],
        },
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
        intent = Intent.model_validate(raw, strict=True)
        if intent.task != "lookup" and intent.queries:
            raise ValueError("Non-lookup plan contains search queries")
        result = Plan(
            search=intent.task == "lookup", queries=intent.queries, freshness=intent.freshness
        )
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
