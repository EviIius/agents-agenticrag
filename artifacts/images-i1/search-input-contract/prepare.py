"""Freeze-ready materialization; all preparation uses synthetic inputs only."""

import difflib
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PREVIOUS = OUT.parent / "search-repair-v2"
sys.path[:0] = [str(ROOT / "server"), str(OUT)]
import contract  # noqa: E402


def replace(source, before, after):
    assert source.count(before) == 1, before
    return source.replace(before, after)


def main():
    assert not (OUT / "cases.json").exists(), "Already prepared; never overwrite a trial"
    shutil.copyfile(PREVIOUS / "cases.json", OUT / "cases.json")
    shutil.copytree(PREVIOUS / "fixtures", OUT / "fixtures")
    prompts = json.loads((PREVIOUS / "prompts.json").read_text())
    prompts["candidate"]["planner"] += contract.EXTRA_PROMPT
    (OUT / "prompts.json").write_text(json.dumps(prompts, indent=2) + "\n")
    (OUT / "schema.json").write_text(json.dumps(contract.SCHEMA, indent=2) + "\n")
    supplemental = []

    def case(
        identifier, question, search, required, source, *, history=None, attachment=None, held=False
    ):
        row = {
            "id": identifier,
            "split": "held_out" if held else "development",
            "turns": [{"user": question}],
            "expect": {
                "search": search,
                "must_include": required,
                "must_not_match": [],
                "min_citations": 1 if search else 0,
            },
        }
        if history:
            row["seed_history"] = history
        if attachment:
            row["seed_attachment"] = attachment
        supplemental.append(row)
        url = "https://example.org/synthetic-input-contract/" + identifier
        key = hashlib.sha256(url.encode()).hexdigest()
        directory = OUT / "fixtures" / identifier / "0"
        directory.mkdir(parents=True)
        title = "Synthetic input-contract evidence " + identifier
        (directory / "ddgs.search.json").write_text(
            json.dumps(
                [
                    {
                        "url": url,
                        "title": title,
                        "snippet": source,
                        "provider": "ddgs",
                        "published_at": None,
                    }
                ],
                indent=2,
            )
            + "\n"
        )
        (directory / (key + ".page.json")).write_text(
            json.dumps({"url": url, "content_type": "text/html"}, indent=2) + "\n"
        )
        (directory / (key + ".page.bin")).write_text(
            "<html><head><title>"
            + title
            + "</title></head><body><article><h1>"
            + title
            + "</h1><p>"
            + source
            + "</p><p>This is synthetic evidence for a local input-contract eval"
            "uation. It supplies only the facts explicitly stated above. It do"
            "es not identify any real person, private recording or private doc"
            "ument. A name or link is only a resource reference. An unavailabl"
            "e file has no supplied body. Other dates and attributes must not "
            "be inferred from this source.</p></article></body></html>"
        )

    case(
        "contract-01",
        "Rewrite 'Visit https://example.org/doc' more politely.",
        False,
        ["https://example.org/doc"],
        "The public Juniper Report lists twelve instruments.",
    )
    case(
        "contract-02",
        "Summarize the document named 'Juniper Report'.",
        True,
        ["twelve|12", "instrument"],
        "The Juniper Report lists twelve instruments.",
    )
    case(
        "contract-03",
        "Rewrite your previous refusal more politely.",
        False,
        ["manual"],
        "The public service manual specifies a two-year service interval.",
        history=[
            {"role": "user", "content": "Summarize the service manual."},
            {"role": "assistant", "content": "I do not have the manual's content."},
        ],
    )
    case(
        "contract-04",
        "Summarize this sentence and verify when Elmport Observatory opene"
        "d: It houses a small telescope.",
        True,
        ["1707"],
        "Elmport Observatory opened in 1707. Its telescope is small.",
    )
    case(
        "contract-05",
        "Summarize the attached document in one sentence.",
        False,
        ["17|seventeen", "two|2", "valve", "pump"],
        "The unrelated public report lists twelve instruments.",
        attachment="The synthetic plant uses seventeen valves and two pumps.",
    )
    case(
        "contract-06",
        "Then summarize it now.",
        True,
        ["three|3", "year"],
        "The Birch Pump handbook specifies a three-year maintenance interval.",
        history=[
            {"role": "user", "content": "Summarize the Birch Pump handbook."},
            {"role": "assistant", "content": "The file text has not been supplied."},
        ],
        held=True,
    )
    case(
        "contract-07",
        "Translate ciao mondo into English.",
        False,
        ["hello.*world|hi.*world"],
        "The unrelated public report lists twelve instruments.",
        held=True,
    )
    case(
        "contract-08",
        "Summarize the public Juniper Report. This request names it with <"
        "file name='Juniper Report'></file>; its body is not supplied.",
        True,
        ["twelve|12", "instrument"],
        "The Juniper Report lists twelve instruments.",
        held=True,
    )
    case(
        "contract-09",
        "Translate 'Juniper Report' into French.",
        False,
        ["rapport"],
        "The unrelated public report lists twelve instruments.",
        held=True,
    )
    (OUT / "supplemental-cases.json").write_text(json.dumps(supplemental, indent=2) + "\n")
    cases = json.loads((OUT / "cases.json").read_text())
    (OUT / "boundary-cases.json").write_text(json.dumps(cases + supplemental, indent=2) + "\n")
    declaration = json.loads((PREVIOUS / "execution.json").read_text())
    original_order = declaration["order"]
    extra = [
        ["supplemental-" + arm + "-" + c["id"], arm, c["id"]]
        for arm in ("baseline", "candidate")
        for c in supplemental
    ]
    declaration.update(
        order=original_order[:48] + extra + original_order[48:],
        boundary_end=66,
        candidate_count=1,
        additional_cases=9,
        additional_designated_heldout=4,
        original_boundaries_unchanged=True,
        unseen_claim=False,
    )
    (OUT / "execution.json").write_text(json.dumps(declaration, indent=2) + "\n")
    build_harness()


def build_harness():
    assert not (OUT / "experiment.py").exists()
    source = (PREVIOUS / "experiment.py").read_text()
    actual = replace(
        source,
        "    original_schema = planner.schema\n",
        """    if arm == "candidate":
        import contract
        from app.search.pipeline import Pipeline
        contract.datetime = FixedDateTime
        contract.install(Pipeline)
    original_schema = planner.schema
""",
    )
    assert actual.count('"cases.json"') == 3
    actual = actual.replace('"cases.json"', '"boundary-cases.json"')
    assert actual.count('selected.get("seed_history")') == 2
    actual = actual.replace(
        'selected.get("seed_history")',
        '(selected.get("seed_history") or selected.get("seed_attachment"))',
    )
    actual = replace(
        actual, 'enumerate(selected["seed_history"])', 'enumerate(selected.get("seed_history", []))'
    )
    actual = replace(
        actual,
        "            seeded = True\n",
        """            if selected.get("seed_attachment"):
                attachment_id = "synthetic-document-" + selected["id"]
                location = app.state.config.data_dir / "attachments" / (attachment_id + ".txt")
                location.parent.mkdir(exist_ok=True)
                location.write_text(selected["seed_attachment"])
                await app.state.store.execute(
                    "INSERT INTO attachments(id,kind,filename,mime_type,bytes,path,created_at) "
                    "VALUES (?,'text','synthetic-input.txt','text/plain',?,?,?)",
                    (attachment_id, location.stat().st_size,
                     str(location.relative_to(app.state.config.data_dir)), NOW.isoformat()),
                )
                kwargs["json"]["attachment_ids"] = [attachment_id]
            seeded = True
""",
    )
    actual = replace(
        actual,
        '"source": "ba51370 product tree"',
        '"source": "a531a85 unchanged product; isolated input-contract candidate"',
    )
    actual = replace(actual, '"schema_edit": False', '"schema_edit": arm == "candidate"')
    actual = replace(
        actual,
        "        start, end = 0, 48\n",
        '        start, end = 0, declaration["boundary_end"]\n',
    )
    actual = replace(
        actual,
        "        start, end = 48 + 2 * (pair - 1), 48 + 2 * pair\n",
        '        base = declaration["boundary_end"]\n        start, end = b'
        "ase + 2 * (pair - 1), base + 2 * pair\n",
    )
    (OUT / "experiment.py").write_text(actual)
    patch = "".join(
        difflib.unified_diff(
            source.splitlines(keepends=True),
            actual.splitlines(keepends=True),
            fromfile="search-repair-v2/experiment.py",
            tofile="search-input-contract/experiment.py",
        )
    )
    (OUT / "harness.patch").write_text(patch)
    print(
        "Prepared one isolated candidate, unchanged 24 boundaries, nine su"
        "pplemental cases, 72-child order; no inference."
    )


if __name__ == "__main__":
    build_harness() if "--harness-only" in sys.argv else main()
