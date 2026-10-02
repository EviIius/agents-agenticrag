import math
import re
from collections import Counter

from ..schemas import Passage

_TOKEN = re.compile(r"[a-z0-9]+")
_STOP = frozenset(
    "a an and are as at be by for from has have how in is it its of on or that the "
    "this to was were "
    "what when where which who why will with did does do "
    "about into than then there their they".split()
)


def tokenize(text: str) -> list[str]:
    tokens = []
    for term in _TOKEN.findall(text.lower()):
        if term in _STOP:
            continue
        # Fold regular English noun plurals for passage matching. Provider
        # queries and the source text shown to the user remain exact.
        if len(term) > 4 and term.endswith("ies"):
            term = term[:-3] + "y"
        elif len(term) > 4 and term.endswith("s") and not term.endswith(("ss", "us", "is")):
            term = term[:-1]
        tokens.append(term)
    return tokens


def bm25(query: str, docs: list[str], k1: float = 1.2, b: float = 0.75) -> list[float]:
    q = set(tokenize(query))
    toks = [tokenize(d) for d in docs]
    n = len(toks)
    avgdl = (sum(len(t) for t in toks) / n) if n else 0.0
    df = Counter(term for t in toks for term in set(t))
    out = []
    for t in toks:
        tf, dl, s = Counter(t), len(t), 0.0
        for term in q:
            f = tf.get(term, 0)
            if not f:
                continue
            idf = math.log(1 + (n - df[term] + 0.5) / (df[term] + 0.5))
            s += idf * f * (k1 + 1) / (f + k1 * (1 - b + b * dl / (avgdl or 1)))
        out.append(s)
    return out


def rrf(rankings: list[list[str]], k: int = 60) -> dict[str, float]:
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, key in enumerate(ranking, start=1):
            scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank)
    return scores


def cosine(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or not a:
        raise ValueError("Invalid embedding dimensions")
    denominator = math.sqrt(sum(x * x for x in a) * sum(x * x for x in b))
    return sum(x * y for x, y in zip(a, b, strict=True)) / denominator if denominator else 0.0


def rank(
    passages: list[Passage],
    query: str,
    source_order: list[str],
    vectors: list[list[float]] | None = None,
) -> list[tuple[Passage, float]]:
    keyword = bm25(query, [p.heading + "\n" + p.text for p in passages])
    keys = [str(i) for i in range(len(passages))]
    matched = [key for key in keys if keyword[int(key)] > 0]
    lexical = sorted(matched or keys, key=lambda k: (-keyword[int(k)], int(k)))
    rankings = [lexical]
    if vectors:
        similarities = [cosine(vectors[0], v) for v in vectors[1:]]
        rankings.append(sorted(keys, key=lambda k: (-similarities[int(k)], int(k))))
    fused = rrf(rankings)
    for key in keys:
        fused.setdefault(key, 0.0)
        # A search-position prior must not turn a zero lexical match into
        # a positive relevance score. Semantic matches still qualify in hybrid.
        if fused[key] > 0:
            fused[key] += 1 / (60 + source_order.index(passages[int(key)].source_url) + 1)
        passage = passages[int(key)]
        bibliography = passage.heading.strip().casefold() in {
            "references",
            "bibliography",
            "works cited",
        }
        citations = re.findall(r"(?m)^\s*(?:\d+\.\s|↑\s|(?:\d+\s+){2,})", passage.text)
        if (
            bibliography
            and len(citations) >= 2
            and not (set(tokenize(query)) & {"reference", "bibliography", "citation"})
        ):
            # Repeated titles in a bibliography are discovery links, rather
            # than the article's factual summary. Keep them available when
            # requested, but prevent repetition from crowding out body text.
            fused[key] *= 0.25
    return [(passages[int(k)], fused[k]) for k in sorted(keys, key=lambda k: (-fused[k], int(k)))]


def select(
    ranked: list[tuple[Passage, float]], budget: int, maximum: int, ratio: float = 0.3
) -> list[list[Passage]]:
    if not ranked:
        return []
    best: dict[str, float] = {}
    for p, score in ranked:
        best[p.source_url] = max(best.get(p.source_url, 0), score)
    eligible = {url for url, score in best.items() if score >= 0.15 * ranked[0][1]}
    if len(eligible) < 2:
        eligible = set(sorted(best, key=lambda u: -best[u])[:2])
    selected: dict[str, list[Passage]] = {}
    used = 0
    for p, _ in ranked:
        cost = math.ceil(len(p.text) * ratio) + 20
        if (
            p.source_url in eligible
            and p.source_url not in selected
            and len(selected) < maximum
            and used + cost <= budget
        ):
            selected[p.source_url] = [p]
            used += cost
    for p, _ in ranked:
        chosen = selected.get(p.source_url)
        cost = math.ceil(len(p.text) * ratio) + 20
        if chosen is not None and p not in chosen and len(chosen) < 3 and used + cost <= budget:
            chosen.append(p)
            used += cost
    return [sorted(group, key=lambda p: p.ord) for group in selected.values()]
