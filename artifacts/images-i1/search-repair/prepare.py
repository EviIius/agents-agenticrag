"""Materialize a single declared synthetic suite and exact proposed prompts."""

import ast
import hashlib
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent

PLANNER = (
    "A transformation requires content supplied in the latest message or the "
    "conversation. A title, URL or description of an external page identifies a "
    "resource; it does not supply that resource's content. Summarizing an external "
    "resource or factual subject whose content is absent is lookup, not transform. "
    "Transform supplied words, quotations, excerpts and an earlier conversation "
    "answer without searching unless the user also requests external facts."
)
ANSWER = (
    "Evidence must establish the requested subject, relationship and time period. "
    'First-person words such as "I" or "you" in a source refer to that source\'s '
    "participants; do not equate them with the requesting user without an explicit "
    "link in the conversation. Facts about unrelated subjects do not answer the "
    "requested fact. When that link or a requested detail is missing, state that it "
    "is not established by these sources. Do not substitute unrelated biographies "
    "or records, or state an unsupported value followed by a disclaimer."
)


def original(name):
    tree = ast.parse((ROOT / "server/app/search" / name).read_text())
    statement = next(
        n
        for n in tree.body
        if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "PROMPT" for t in n.targets)
    )
    return ast.literal_eval(statement.value)


def main():
    fixtures = OUT / "fixtures"
    fixtures.mkdir(exist_ok=False)
    cases = json.loads((OUT / "cases.json").read_text())
    assert len(cases) == len({c["id"] for c in cases}) == 24
    assert sum(c["split"] == "held_out" for c in cases) == 8
    for group in {c["group"] for c in cases}:
        assert sum(c["group"] == group for c in cases) == 6
    padding = (
        "This is a synthetic evaluation record about fictional participants and places. "
        "Only the statements in this record are available as evidence. No additional "
        "identity, dates, measurements or relationships are implied. The record is "
        "deliberately limited in scope; omitted details cannot be recovered from it. "
    )
    for case in cases:
        directory = fixtures / case["id"] / "0"
        directory.mkdir(parents=True)
        url = "https://example.org/synthetic-boundary/" + case["id"]
        title = "Synthetic boundary record: " + case["id"]
        content = case.get("fixture", "This unrelated record supplies no requested external fact.")
        body = "<html><head><title>" + title + "</title></head><body><article><p>"
        body += escape(content + " " + padding) + "</p></article></body></html>"
        key = hashlib.sha256(url.encode()).hexdigest()
        (directory / (key + ".page.bin")).write_bytes(body.encode())
        (directory / (key + ".page.json")).write_text(
            json.dumps({"url": url, "content_type": "text/html"}) + "\n"
        )
        (directory / "ddgs.search.json").write_text(
            json.dumps(
                [
                    {
                        "url": url,
                        "title": title,
                        "snippet": content,
                        "provider": "Synthetic boundary fixture",
                    }
                ],
                indent=2,
            )
            + "\n"
        )
    prompts = {"baseline": {"planner": original("planner.py"), "answer": original("prompt.py")}}
    prompts["candidate"] = {
        "planner": prompts["baseline"]["planner"] + "\n" + PLANNER,
        "answer": prompts["baseline"]["answer"] + "\n" + ANSWER,
    }
    (OUT / "prompts.json").write_text(json.dumps(prompts, indent=2) + "\n")
    print("Prepared 24 separate synthetic cases, 8 held out, and one exact prompt candidate.")


if __name__ == "__main__":
    main()
