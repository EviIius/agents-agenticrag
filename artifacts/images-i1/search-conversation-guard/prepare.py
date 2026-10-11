"""Prepare separate ordinary-task cases/order once; no native model invocation."""

import hashlib
import html
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
PREVIOUS = OUT.parent / "search-input-fallback"


def main():
    assert not (OUT / "ordinary-cases.json").exists()
    cases = []
    inputs = [
        ("Hello! How are you today?", False, [], "No external facts are requested."),
        ("Thank you, that helped.", False, [], "No external facts are requested."),
        (
            "Hi! What is Nolven Station's opening year?",
            True,
            ["2032"],
            "Nolven Station opened in 2032.",
        ),
        (
            "Thanks! What does Fenn Archive charge for admission?",
            True,
            ["four|4", "credit"],
            "Fenn Archive charges four credits for admission.",
        ),
        ("Write a two-line poem about moonlight.", False, [], "No external facts are requested."),
        (
            "Write a Python function that adds two numbers.",
            False,
            ["def|lambda"],
            "No external facts are requested.",
        ),
        ("What is 31 multiplied by 12?", False, ["372"], "No external facts are requested."),
        (
            "Rewrite 'Hello! How are you?' more politely.",
            False,
            [],
            "No external facts are requested.",
        ),
    ]
    for number, (question, search, required, source) in enumerate(inputs, 1):
        identifier = "social-" + str(number).zfill(2)
        cases.append(
            {
                "id": identifier,
                "split": "development" if number <= 4 else "held_out",
                "turns": [{"user": question}],
                "expect": {
                    "search": search,
                    "must_include": required,
                    "must_not_match": [],
                    "min_citations": 1 if search else 0,
                },
            }
        )
        folder = OUT / "fixtures" / identifier / "0"
        folder.mkdir(parents=True)
        url = "https://example.org/synthetic-social-guard/" + identifier
        key = hashlib.sha256(url.encode()).hexdigest()
        title = "Synthetic ordinary-task record " + identifier
        (folder / "ddgs.search.json").write_text(
            json.dumps(
                [
                    {
                        "url": url,
                        "title": title,
                        "snippet": source,
                        "provider": "ddgs",
                    }
                ],
                indent=2,
            )
            + "\n"
        )
        (folder / (key + ".page.json")).write_text(
            json.dumps(
                {
                    "url": url,
                    "content_type": "text/html",
                },
                indent=2,
            )
            + "\n"
        )
        (folder / (key + ".page.bin")).write_text(
            "<html><head><title>" + html.escape(title) + "</title></head><body><article>"
            "<h1>" + html.escape(title) + "</h1><p>" + html.escape(source) + "</p>"
            "<p>This is synthetic local evaluation evidence about fictional places. "
            "Only the statements above are available as evidence. No other subject, "
            "identity, date, measurement or relationship is established. Unrelated "
            "records do not provide a source for social replies, poems or arithmetic. "
            "This fixture contains no private recording, document or user information."
            "</p></article></body></html>"
        )
    (OUT / "ordinary-cases.json").write_text(json.dumps(cases, indent=2) + "\n")
    original = json.loads((OUT / "cases.json").read_text())
    supplemental = json.loads((OUT / "supplemental-cases.json").read_text())
    (OUT / "boundary-cases.json").write_text(
        json.dumps(original + supplemental + cases, indent=2) + "\n"
    )
    declaration = json.loads((PREVIOUS / "execution.json").read_text())
    before, after = declaration["order"][:66], declaration["order"][66:]
    ordinary = [
        ["ordinary-" + arm + "-" + case["id"], arm, case["id"]]
        for arm in ("baseline", "candidate")
        for case in cases
    ]
    declaration.update(
        {
            "order": before + ordinary + after,
            "boundary_end": 82,
            "ordinary_cases": 8,
            "ordinary_designated_heldout": 4,
            "original_72_child_relative_order_unchanged": True,
            "previous_33_cases_and_fixtures_unchanged": True,
        }
    )
    (OUT / "execution.json").write_text(json.dumps(declaration, indent=2) + "\n")
    print("Prepared eight separate ordinary-task cases and 88-child order; no inference.")


if __name__ == "__main__":
    main()
