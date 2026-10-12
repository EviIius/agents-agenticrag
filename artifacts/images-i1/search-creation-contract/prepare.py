"""Declare creation/editing regressions once; preserve prior input bytes/order."""

import hashlib
import html
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
PREVIOUS = OUT.parent / "search-conversation-guard"


def main():
    assert not (OUT / "creation-cases.json").exists()
    inputs = [
        (
            "Create a JavaScript function that multiplies two numbers.",
            False,
            ["function|=>"],
            "No external facts are requested.",
            {},
        ),
        (
            "Generate a short original story about an imaginary lighthouse.",
            False,
            [],
            "No external facts are requested.",
            {},
        ),
        (
            "Write a Python function that adds two numbers.",
            False,
            ["def|lambda"],
            "No external facts are requested.",
            {
                "seed_history": [
                    {
                        "role": "user",
                        "content": "Supplied note: The fictional port has three gates.",
                    },
                    {"role": "assistant", "content": "The fictional port has three gates."},
                ]
            },
        ),
        (
            "Rewrite: def add(a, b): return a + b",
            False,
            ["def|lambda"],
            "No external facts are requested.",
            {},
        ),
        (
            "Rewrite the code in the Marven utility script to use two arguments.",
            True,
            ["def|lambda"],
            "The Marven utility script contains exactly: def combine(a, b): return a + b.",
            {},
        ),
        (
            "Write a Python function and verify whether Drel Observatory opened in 2034.",
            True,
            ["2031"],
            "Drel Observatory opened in 2031. No function behavior was specified.",
            {},
        ),
        (
            "Create a Python function that returns the string 'latest release'.",
            False,
            ["def|lambda", "latest release"],
            "No external facts are requested.",
            {},
        ),
        (
            "Create a Python function based on the current documentation for the Neral API.",
            True,
            ["/v3/tiles", "GET|get"],
            "The current Neral API documentation specifies GET /v3/tiles. "
            "This is the only documented route and method; no authentication, "
            "parameters or response shape are documented.",
            {},
        ),
    ]
    cases = []
    for number, (question, search, required, source, seeded) in enumerate(inputs, 1):
        identifier = "creation-" + str(number).zfill(2)
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
                **seeded,
            }
        )
        folder = OUT / "fixtures" / identifier / "0"
        folder.mkdir(parents=True)
        url = "https://example.org/synthetic-creation-contract/" + identifier
        key = hashlib.sha256(url.encode()).hexdigest()
        title = "Synthetic creation/editing record " + identifier
        (folder / "ddgs.search.json").write_text(
            json.dumps(
                [{"url": url, "title": title, "snippet": source, "provider": "ddgs"}], indent=2
            )
            + "\n"
        )
        (folder / (key + ".page.json")).write_text(
            json.dumps({"url": url, "content_type": "text/html"}, indent=2) + "\n"
        )
        (folder / (key + ".page.bin")).write_text(
            "<html><head><title>" + html.escape(title) + "</title></head><body><article>"
            "<h1>" + html.escape(title) + "</h1><p>" + html.escape(source) + "</p>"
            "<p>This is synthetic local evaluation evidence about fictional systems. "
            "Only the statements above are established. No further identity, date, "
            "API detail or relationship is established. Local program output is a "
            "proposed artifact rather than evidence of external API behavior. "
            "No private recording, document or user data appears here.</p></article></body></html>"
        )
    (OUT / "creation-cases.json").write_text(json.dumps(cases, indent=2) + "\n")
    previous_cases = json.loads((PREVIOUS / "boundary-cases.json").read_text())
    (OUT / "boundary-cases.json").write_text(json.dumps(previous_cases + cases, indent=2) + "\n")
    declaration = json.loads((PREVIOUS / "execution.json").read_text())
    extra = [
        ["creation-" + arm + "-" + case["id"], arm, case["id"]]
        for arm in ("baseline", "candidate")
        for case in cases
    ]
    declaration.update(
        {
            "order": declaration["order"][:82] + extra + declaration["order"][82:],
            "boundary_end": 98,
            "creation_cases": 8,
            "creation_designated_heldout": 4,
            "previous_88_child_relative_order_unchanged": True,
            "previous_41_cases_and_fixtures_unchanged": True,
        }
    )
    (OUT / "execution.json").write_text(json.dumps(declaration, indent=2) + "\n")
    print("Prepared eight separate creation/editing cases and 104-child order; no inference.")


if __name__ == "__main__":
    main()
