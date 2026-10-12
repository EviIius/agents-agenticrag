"""Offline retained-failure trace. Does not install a policy or make model calls."""

from __future__ import annotations

import asyncio
import copy
import gzip
import hashlib
import importlib.util
import json
import re
import socket
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PRIOR = ROOT / "artifacts/images-i1/search-scoped-input"
sys.path.insert(0, str(ROOT / "server"))

from app.search.chunk import chunk
from app.search.extract import extract
from app.search.fetch import RawPage
from app.search.fixtures import Fixtures
from app.search.merge import merge
from app.search.rank import rank, select


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@contextmanager
def no_network():
    def reject(*_args, **_kwargs):
        raise AssertionError("Offline audit forbids network connections")

    with (
        patch.object(socket.socket, "connect", reject),
        patch.object(socket.socket, "connect_ex", reject),
    ):
        yield


def load_contract():
    name = "retained_scope_contract"
    spec = importlib.util.spec_from_file_location(name, PRIOR / "contract.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def report():
    analysis = json.loads((PRIOR / "full-failure-analysis.json").read_text())
    path = ROOT / analysis["full_report"]
    assert sha(path) == analysis["full_report_sha256"]
    return path, json.loads(path.read_text())


def retained_turns(document):
    traces = [
        json.loads(line)
        for line in (PRIOR / "full-pair-1-candidate/trace.jsonl")
        .read_text()
        .splitlines()
    ]
    planners = [t for t in traces if t["payload"].get("format") is not None]
    answers = [t for t in traces if t["payload"].get("format") is None]
    hosts = [
        json.loads(line)
        for line in (PRIOR / "full-pair-1-candidate/host-decisions.jsonl")
        .read_text()
        .splitlines()
    ]
    turns = [
        (r["id"], index, t)
        for r in document["results"]
        for index, t in enumerate(r["turns"])
    ]
    assert len(turns) == len(planners) == len(answers) == len(hosts) == 28
    ratio = 0.3
    rows = {}
    for (case_id, index, turn), planner, answer, host in zip(
        turns, planners, answers, hosts, strict=True
    ):
        raw = json.loads(
            "".join(
                e["value"]["text"]
                for e in planner["events"]
                if e["type"] == "TextDelta"
            )
        )
        rows[(case_id, index)] = {
            "turn": turn,
            "native": raw,
            "planner_payload": planner["payload"],
            "answer_payload": answer["payload"],
            "host": host,
            "ratio": ratio,
        }
        # Reconstruct the actual persisted estimator; each answer updates it.
        chars = sum(len(m["content"]) for m in answer["payload"]["messages"])
        prompt_tokens = turn["message"]["stats"]["prompt_tokens"]
        if chars and prompt_tokens:
            ratio = 0.7 * ratio + 0.3 * max(0.05, min(1, prompt_tokens / chars))
    return rows


async def replay_plan(contract, question, native, force=False, materials=()):
    class RetainedAdapter:
        calls = 0

        async def complete_json(self, _request):
            self.calls += 1
            return copy.deepcopy(native)

    adapter = RetainedAdapter()
    decision = {}
    token = contract.MATERIALS.set(tuple(materials))
    state = contract.DECISION.set(decision)
    try:
        plan, fallback = await contract.plan(
            adapter, "retained-offline", question, [], True, 16384, force
        )
        assert adapter.calls == 1
        return {"plan": plan.model_dump(), "fallback": fallback, "host": decision}
    finally:
        contract.MATERIALS.reset(token)
        contract.DECISION.reset(state)


def markdown_tables(text):
    """Diagnostic exact header/cell binding; no numeric or semantic inference."""
    groups, current = [], []
    for line in text.splitlines() + [""]:
        if line.strip().startswith("|"):
            current.append(line.strip())
        elif current:
            groups.append(current)
            current = []
    result = []
    for group in groups:
        cells = [
            [v.strip().replace(r"\|", "|") for v in re.split(r"(?<!\\)\|", line)[1:-1]]
            for line in group
        ]
        header = cells[0]
        body = [
            row
            for row in cells[1:]
            if row != header and not all(re.fullmatch(r":?-+:?", v) for v in row)
        ]
        if header and body and all(len(row) == len(header) for row in body):
            result.append({"header": header, "rows": body})
    return result


def exact_cell(tables, key_header, key, field, value):
    """An exact diagnostic relation needs unique headers and the correct row."""
    for table in tables:
        header = table["header"]
        if header.count(key_header) != 1 or header.count(field) != 1:
            continue
        a, b = header.index(key_header), header.index(field)
        if any(row[a] == key and row[b] == value for row in table["rows"]):
            return True
    return False


def recorded_candidates(directory):
    fixture = Fixtures(directory)
    saved = json.loads((directory / "run.json").read_text())["web"]
    batches = []
    for query in saved["queries"]:
        for provider in ("ollama", "searxng", "exa", "ddgs"):
            try:
                found = fixture.search(provider, query, saved["freshness"])
            except (ValueError, FileNotFoundError):
                continue
            if found:
                batches.append(found)
                break
    return fixture, saved, merge(batches, [])


def page_trace(fixture, source, selected):
    from lxml import html

    raw = fixture.page(source.url)
    page = extract(raw)
    passages = chunk(source.url, page.text)
    document = html.fromstring(raw.data) if "html" in raw.content_type else None
    tables = document.xpath("//table") if document is not None else []
    largest = max(tables, key=lambda t: len(t.xpath(".//tr")), default=None)
    largest_rows = largest.xpath(".//tr") if largest is not None else []
    header_cells = [
        re.sub(r"\s+", " ", c.text_content()).strip()
        for row in largest_rows[:2]
        for c in row.xpath("./th|./td")
    ]
    selected_ord = {p["ord"] for p in selected}
    for retained in selected:
        actual = next(p for p in passages if p.ord == retained["ord"])
        assert actual.text == retained["text"] and actual.heading == retained["heading"]
    record = {
        "url": source.url,
        "raw_url": raw.url,
        "raw_sha256": hashlib.sha256(raw.data).hexdigest(),
        "raw_bytes": len(raw.data),
        "raw_html_tables": len(tables),
        "largest_raw_table_rows": len(largest_rows),
        "largest_raw_table_first_two_row_cells": header_cells,
        "extracted_sha256": hashlib.sha256(page.text.encode()).hexdigest(),
        "extracted_characters": len(page.text),
        "australian_currency_name_or_code_literal_present": bool(
            re.search(r"\bAustralian dollar\b|\bAUD\b", page.text, re.IGNORECASE)
        ),
        "hits_80000_character_cap": len(page.text) == 80000,
        "extracted_pipe_lines": sum(
            l.lstrip().startswith("|") for l in page.text.splitlines()
        ),
        "chunk_count": len(passages),
        "selected_ordinals": sorted(selected_ord),
        "selected_chunks_reproduced_exactly": len(selected),
        "chunks": [
            {
                "ord": p.ord,
                "heading": p.heading,
                "characters": len(p.text),
                "sha256": hashlib.sha256(p.text.encode()).hexdigest(),
                "selected": p.ord in selected_ord,
                "markdown_tables": markdown_tables(p.text),
            }
            for p in passages
        ],
    }
    return page, passages, record


def case_trace(case_id, retained, document):
    turn = retained["turn"]
    directory = Path(document["fixture_root"]) / case_id / "0"
    fixture, saved, candidates = recorded_candidates(directory)
    fetched = {r["url"] for r in turn["reads"] if r["status"] != "failed"}
    actual = {s["url"]: s["passages"] for s in turn["sources"]}
    pages, passages, details = {}, [], []
    for result in candidates:
        if result.url not in fetched:
            continue
        page, chunks, detail = page_trace(fixture, result, actual.get(result.url, []))
        pages[result.url] = page
        passages.extend(chunks)
        details.append(detail)
    payload = retained["answer_payload"]
    system = payload["messages"][0]["content"].removesuffix(
        "\n\n" + document["answer_prompt"]
    )
    ratio = retained["ratio"]
    assert (
        len(payload["messages"]) == 2
    )  # The three audited cases have no conversation history.
    used = int(len(system) * ratio) + 4 + int(len(turn["question"]) * ratio) + 4
    reserve = 4096
    assert payload["options"] == {"num_ctx": 16384}
    budget = max(1500, min(12000, int(0.45 * (16384 - reserve - used))))
    order = [c.url for c in candidates]
    diagnostics = {}
    for mode in ("actual_combined_query", "question_only_diagnostic"):
        query = turn["question"]
        if mode == "actual_combined_query":
            query += " " + " ".join(turn["web"]["queries"])
        ranked = rank(passages, query, order)
        groups = select(ranked, budget, 6, ratio)
        selection = {g[0].source_url: [p.ord for p in g] for g in groups}
        diagnostics[mode] = {
            "selection": selection,
            "ranking": [
                {"url": p.source_url, "ord": p.ord, "score": score}
                for p, score in ranked
            ],
        }
    expected = {url: [p["ord"] for p in selected] for url, selected in actual.items()}
    assert diagnostics["actual_combined_query"]["selection"] == expected
    # Inspect every readable archived page too, not only the selected six.
    archived = []
    for path in sorted(directory.glob("*.page.json")):
        meta = json.loads(path.read_text())
        if meta.get("error"):
            archived.append({"url": meta["url"], "error": meta["error"]})
            continue
        # Metadata records the redirected raw URL; the filename is keyed by
        # the requested URL. Read the adjacent bytes, not a reconstructed key.
        raw_path = path.with_suffix(".bin")
        raw = RawPage(
            meta["url"],
            raw_path.read_bytes()
            if raw_path.exists()
            else gzip.decompress(raw_path.with_suffix(".bin.gz").read_bytes()),
            meta["content_type"],
        )
        try:
            page = extract(raw)
        except ValueError as exc:
            archived.append({"url": meta["url"], "extraction_error": str(exc)})
            continue
        archived.append(
            {
                "url": meta["url"],
                "raw_sha256": hashlib.sha256(raw.data).hexdigest(),
                "australian_currency_name_or_code_literal_present": bool(
                    re.search(
                        r"\bAustralian dollar\b|\bAUD\b", page.text, re.IGNORECASE
                    )
                ),
                "australian_currency_literal_context": [
                    page.text[max(0, match.start() - 80) : match.end() + 100]
                    for match in re.finditer(
                        r"\bAustralian dollar\b|\bAUD\b", page.text, re.IGNORECASE
                    )
                ],
            }
        )
    return {
        "case": case_id,
        "original_question": turn["question"],
        "automatic_passed": next(
            r["passed"] for r in document["results"] if r["id"] == case_id
        ),
        "recorded_provider_queries": saved["queries"],
        "native_queries": turn["web"]["queries"],
        "provider_result_replay": "Fixed recorded batches ignore fresh planner queries; only ranking uses them.",
        "calibrated_context_ratio": ratio,
        "reserve": reserve,
        "source_token_budget": budget,
        "all_actual_selected_passages_reproduced": True,
        "ranking_selection_reproduced": True,
        "question_only_same_selected_ordinals": diagnostics["question_only_diagnostic"][
            "selection"
        ]
        == expected,
        "pages": details,
        "archived_pages": archived,
        "ranking_diagnostics": diagnostics,
        "actual_answer_sha256": hashlib.sha256(turn["raw_answer"].encode()).hexdigest(),
        "native_calls": 0,
    }, pages


def preserve_prior():
    manifest = json.loads((PRIOR / "manifest.json").read_text())
    for name, digest in manifest["files"].items():
        assert sha(ROOT / name) == digest, name
    before = subprocess.check_output(
        [
            "git",
            "ls-tree",
            "-r",
            "-z",
            "cb5a1a4b",
            "--",
            "artifacts",
            "server/evals/web",
        ],
        cwd=ROOT,
    )
    count = 0
    for row in before.split(b"\0"):
        if not row:
            continue
        head, name = row.split(b"\t", 1)
        data = (ROOT / name.decode()).read_bytes()
        assert (
            hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
            == head.split()[2].decode()
        ), name
        count += 1
    return {
        "prior_frozen_files": len(manifest["files"]),
        "prior_committed_evidence_and_eval_files": count,
    }


def write(name, value):
    path = OUT / name
    assert not path.exists(), name
    path.write_text(json.dumps(value, indent=2) + "\n")


def main():
    before = preserve_prior()
    report_path, document = report()
    turns = retained_turns(document)
    contract = load_contract()
    with no_network():
        tasks = {}
        for case_id in ("haiku", "fiction"):
            saved = turns[(case_id, 0)]
            replay = asyncio.run(
                replay_plan(contract, saved["turn"]["question"], saved["native"])
            )
            assert replay["host"] == saved["host"] and replay["plan"]["search"]
            tasks[case_id] = {"native": saved["native"], "replay": replay}
        write(
            "task-replay.json",
            {"native_calls": 0, "original_policy_unchanged": True, "cases": tasks},
        )
        for case_id in ("nba-all-losses", "capital-compare", "table-page"):
            record, _pages = case_trace(case_id, turns[(case_id, 0)], document)
            write(case_id + "-trace.json", record)
    after = preserve_prior()
    assert before == after
    product = subprocess.check_output(
        [
            "git",
            "diff",
            "--name-only",
            "cb5a1a4b",
            "--",
            "server",
            "web",
            "shared",
            "scripts",
            "image_worker",
            "transcribe",
        ],
        cwd=ROOT,
        text=True,
    ).splitlines()
    assert not product, product
    write(
        "verification.json",
        {
            **after,
            "prior_full_report": str(report_path.relative_to(ROOT)),
            "prior_full_report_sha256": sha(report_path),
            "retained_turns_accounted_for_context_ratio": 28,
            "audited_source_cases": 3,
            "replayed_task_cases": 2,
            "native_calls": 0,
            "network_connections_allowed": False,
            "original_scores_and_inputs_unchanged": True,
            "product_changes": product,
            "deployment": False,
            "research_image_workflow_calls": 0,
        },
    )
    print(
        json.dumps(
            {
                **after,
                "native_calls": 0,
                "task_replays": 2,
                "source_traces": 3,
                "exact_rank_selection_replays": 3,
            }
        )
    )


if __name__ == "__main__":
    main()
