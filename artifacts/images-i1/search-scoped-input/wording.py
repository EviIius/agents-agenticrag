"""Isolated equivalent-decline wording correction, never semantic qualification."""

import re

# Exact generic assertion signatures, without case IDs or topic/entity words.
# A fact-specific negation (e.g. HTTP no-content) never becomes abstention.
BASE = (
    r"not (?:established|known|specified|provided)|"
    r"(?:cannot|can't|unable to|do not|don't) (?:determine|know|establish|identify)|"
    r"no (?:information|evidence)"
)
SECOND = (
    r"not (?:established|known|specified|provided|state)|"
    r"(?:cannot|can't|unable to) (?:determine|establish|confirm)|"
    r"no (?:information|evidence)"
)
PATTERNS = frozenset(
    {
        BASE,
        SECOND,
        SECOND + r"|does not (?:specify|state|mention)",
        r"(can't|cannot|don't|do not|no way|not able|not know|not have)",
    }
)
EQUIVALENT = re.compile(
    r"\b(?:(?:does?|did) not|doesn't|don't|didn't) "
    r"(?:establish|specify|state|provide|identify|determine|confirm)\b|"
    r"\b(?:isn't|aren't|wasn't|weren't) (?:established|known|specified|provided)\b|"
    r"\bnot (?:established|known|specified|provided)\b|"
    r"\b(?:cannot|can't|unable to|do not|don't) "
    r"(?:determine|know|establish|identify|confirm)\b|\bno (?:information|evidence)\b",
    re.I,
)
META_NEGATION = re.compile(
    r"\b(?:not true|not the case|false|incorrect|wrong|deny|denies|denied|"
    r"disagree|disagrees|disagreed|don't (?:think|believe)|"
    r"do not (?:think|believe)|not (?:unknown|unable|impossible))\b",
    re.I,
)


def unquoted(answer):
    text = re.sub(r"```[\s\S]*?```|`[^`\n]*`", " ", answer)
    text = re.sub(r"(?m)^\s*>[^\n]*", " ", text)
    text = re.sub(
        r'"[^"\n]*"|“[^”]*”|‘[^’]*’|(?<!\w)\x27[^\x27\n]*\x27(?!\w)',
        " ",
        text,
    )
    return text.replace("’", "'")


def matches(pattern, answer):
    if pattern not in PATTERNS:
        return re.search(pattern, answer, re.I) is not None
    # Quotation/metalinguistic negation cannot supply a decline. This bounded
    # check may miss unfamiliar valid wording; it is not claim-support analysis.
    for sentence in re.split(r"[.!?\n]+", unquoted(answer)):
        if not META_NEGATION.search(sentence) and (
            re.search(pattern, sentence, re.I) or EQUIVALENT.search(sentence)
        ):
            return True
    return False


def required_facts(answer, expect):
    patterns = expect.get("must_include_last", expect.get("must_include", []))
    mandatory = all(matches(pattern, answer) for pattern in patterns)
    alternatives = expect.get("must_include_one_of", [])
    return mandatory and (
        not alternatives or any(all(matches(p, answer) for p in group) for group in alternatives)
    )
