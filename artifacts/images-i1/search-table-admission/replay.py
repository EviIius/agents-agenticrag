"""Frozen original-case evidence comparison. No new answers or model calls."""

import hashlib
import importlib.util
import json
import re
from pathlib import Path

import admission

ROOT = admission.ROOT
OUT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "retained_evidence_audit",
    ROOT / "artifacts/images-i1/search-task-evidence-audit/audit.py",
)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

from app.schemas import Passage
from app.search.chunk import chunk
from app.search.extract import extract
from app.search.rank import rank
from app.search.selection import bind_references, literal_condition_rows


def signature(groups):
    return [{"url": g[0].source_url, "ordinals": [p.ord for p in g]} for g in groups]


def projected(groups):
    result = []
    for n, group in enumerate(groups, 1):
        result.append(
            [
                bind_references(
                    p.model_copy(
                        update={
                            "text": re.sub(
                                r"</(?:source|search_results)\s*>",
                                "",
                                p.text,
                                flags=re.IGNORECASE,
                            )
                        }
                    ),
                    n,
                ).model_dump()
                for p in group
            ]
        )
    return result


def compare(document, case_id, index, kept):
    turn = kept["turn"]
    if not turn["sources"]:
        return {
            "case": case_id,
            "turn": index,
            "status": turn["web"]["status"],
            "changed": False,
            "model_calls": 0,
        }
    directory = Path(document["fixture_root"]) / case_id / str(index)
    fixture, _saved, candidates = audit.recorded_candidates(directory)
    fetched = {r["url"] for r in turn["reads"] if r["status"] != "failed"}
    pages = {r.url: extract(fixture.page(r.url)) for r in candidates if r.url in fetched}
    condition = turn["web"]["selection_condition"]
    if condition:
        condition = {**condition, "request_span": turn["question"]}
    passages = [
        p
        for r in candidates
        if r.url in pages
        for p in literal_condition_rows(
            r.url, pages[r.url].text, condition, turn["question"], chunk
        )
    ]
    if len(pages) < 2:
        passages += [
            Passage(source_url=r.url, ord=0, text=r.title + "\n" + r.snippet)
            for r in candidates
            if r.url not in pages and r.snippet.strip()
        ]
    selected_sources = {p.source_url for p in passages if p.selection_applied}
    passages = [p for p in passages if not selected_sources or p.selection_applied]
    ranked = rank(
        passages,
        turn["question"] + " " + " ".join(turn["web"]["queries"]),
        [r.url for r in candidates],
    )
    if any(p.selection_applied for p, _ in ranked):
        top = max(score for _, score in ranked)
        ranked = [(p, score + top if p.selection_applied else score) for p, score in ranked]
        ranked.sort(key=lambda item: item[1], reverse=True)
    payload = kept["answer_payload"]
    assert turn["message"]["stats"]["dropped_message_count"] == 0
    original_messages = [dict(m) for m in payload["messages"]]
    original_messages[0]["content"] = original_messages[0]["content"].removesuffix(
        "\n\n" + document["answer_prompt"]
    )
    original_messages[-1]["content"] = original_messages[-1]["content"].split(
        "</search_results>\n\n", 1
    )[-1]
    ratio = kept["ratio"]
    used = sum(int(len(m["content"]) * ratio) + 4 for m in original_messages)
    budget = max(1500, min(12000, int(0.45 * (16384 - 4096 - used))))
    before = admission.original_select(ranked, budget, 6, ratio)
    expected = [[p for p in s["passages"]] for s in turn["sources"]]
    actual = projected(before)
    assert actual == expected, (
        case_id,
        index,
        signature(before),
        [(s["url"], [p["ord"] for p in s["passages"]]) for s in turn["sources"]],
    )
    originals = [p.model_dump() for p in passages]
    after = admission.select(ranked, budget, 6, ratio, question=turn["question"])
    assert [p.model_dump() for p in passages] == originals
    assert [g[0].source_url for g in before] == [g[0].source_url for g in after]
    data = {
        "case": case_id,
        "turn": index,
        "status": turn["web"]["status"],
        "baseline_matches_original_selected_bytes": True,
        "changed": signature(before) != signature(after),
        "source_ratio": ratio,
        "budget": budget,
        "before": signature(before),
        "after": signature(after),
        "cost_before": sum(admission.cost(p, ratio) for g in before for p in g),
        "cost_after": sum(admission.cost(p, ratio) for g in after for p in g),
        "admitted_passages": [
            {
                "url": p.source_url,
                "ord": p.ord,
                "sha256": hashlib.sha256(p.text.encode()).hexdigest(),
                "all_fields_unchanged": p.model_dump() in originals,
            }
            for group in after
            for p in group
            if p not in [old for g in before for old in g]
        ],
        "model_calls": 0,
        "answer_quality_measured": False,
    }
    if case_id == "nba-all-losses":
        key = "https://landofbasketball.com/stats_teams/finals/finals_lost.htm"

        def row_count(groups):
            return sum(
                len(table["rows"])
                for group in groups
                for p in group
                if p.source_url == key
                for table in audit.markdown_tables(p.text)
            )

        data["original_table_rows_in_model_evidence_before"] = row_count(before)
        data["original_table_rows_in_model_evidence_after"] = row_count(after)
        table = next(
            table
            for group in after
            for p in group
            if p.source_url == key
            for table in audit.markdown_tables(p.text)
        )
        field = table["header"].index("Finals Lost")
        data["explicitly_positive_matching_rows_after"] = sum(
            r[field].isdigit() and int(r[field]) > 0 for r in table["rows"]
        )
        data["columns_preserved"] = len(table["header"])
        original_report = next(r for r in document["results"] if r["id"] == case_id)
        patterns = (
            [r["pattern"] for r in original_report["required_facts"]]
            if isinstance(original_report["required_facts"], list)
            else []
        )
        data["literal_coverage_note"] = (
            "Row/column coverage is structural evidence, "
            "not a new supported answer or semantic score."
        )
        data["original_required_patterns_recorded"] = patterns
    return data


def main():
    _path, document = audit.report()
    kept = audit.retained_turns(document)
    with audit.no_network():
        rows = [compare(document, case_id, index, turn) for (case_id, index), turn in kept.items()]
    changes = [r for r in rows if r["changed"]]
    target = next(r for r in rows if r["case"] == "nba-all-losses")
    assert target["original_table_rows_in_model_evidence_before"] == 0
    assert target["original_table_rows_in_model_evidence_after"] == 28
    assert (
        target["explicitly_positive_matching_rows_after"] == 23 and target["columns_preserved"] == 7
    )
    result = {
        "scope": "All 28 original full-case turns; only evidence selection replayed",
        "source_cases": len(document["results"]),
        "turns": len(rows),
        "original_selection_exact_replays": sum(
            r.get("baseline_matches_original_selected_bytes", False) for r in rows
        ),
        "changed_turns": len(changes),
        "changed_case_ids": [r["case"] for r in changes],
        "new_answers": 0,
        "native_calls": 0,
        "original_automatic_scores_unchanged": True,
        "candidate_not_release_qualified": True,
        "runs": rows,
    }
    path = OUT / "comparison.json"
    assert not path.exists()
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "runs"}, indent=2))


if __name__ == "__main__":
    main()
