"""Unpromoted generic prompt trials. Production continues using SPEC E4 verbatim."""

TASK_AND_SCOPE = (
    "\n\nDecision clarifications:\n"
    "- Classify the latest requested task before writing queries. Text editing, formatting, "
    "translation, summarization of supplied text, and fictional writing need no search, even "
    "when their text mentions real people, places, products, or events. Return search=false "
    "and an empty queries array for those tasks.\n"
    "- For factual requests, preserve the exact population, time span, and inclusion or "
    "exclusion conditions the user asks about. Never add an exclusion, change a condition, "
    "or replace a broad request with a narrower category.\n"
    "- Resolve short follow-ups using the conversation, while keeping the latest task and "
    "its requested scope intact. Do not turn an editing instruction into a fact lookup."
)
