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

TASK_AND_SCOPE_V2 = TASK_AND_SCOPE + (
    "\n- For a factual task, form the first query by condensing the latest message itself. "
    "Keep its requested relationship and all inclusion conditions. Additional queries "
    "may cover separate aspects, but must not substitute a different task or population. "
    "Do not infer that an entity satisfying one condition cannot also satisfy another.\n"
    "- A request to translate supplied words or write a fictional story is a transformation "
    "or creative task, even without earlier conversation. Return search=false."
)

DIRECT_AND_CONSISTENT = (
    "\n- Answer the latest requested task directly. Preserve its inclusion conditions. "
    "Distinguish entity roles, outcomes, dates and measurements exactly as the passages do.\n"
    "- Check that your conclusion follows the cited evidence and agrees with the rest "
    "of your answer. Do not reverse relationships or supply an unsupported conclusion. "
    "Include exact requested measurements when the passages provide them; if they are "
    "missing, say what the evidence does and does not establish."
)
