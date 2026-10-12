"""Bind the manual diagnosis to retained source traces; no model inference."""

import json
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent


def load(name):
    return json.loads((OUT / name).read_text())


def main():
    nba = load("nba-all-losses-trace.json")
    currency = load("capital-compare-trace.json")
    recent = load("table-page-trace.json")
    table_page = next(p for p in nba["pages"] if "finals_lost.htm" in p["url"])
    table = table_page["chunks"][3]
    header = table["markdown_tables"][0]["header"]
    rows = table["markdown_tables"][0]["rows"]
    losses = header.index("Finals Lost")
    selected = [c for p in nba["pages"] for c in p["chunks"] if c["selected"]]

    def cost(chunk):
        return math.ceil(chunk["characters"] * nba["calibrated_context_ratio"]) + 20

    used = sum(cost(c) for c in selected)
    data_cost = cost(table)
    replacement_cost = used - cost(table_page["chunks"][2]) + data_cost
    assert used == 4978 and data_cost == 463 and replacement_cost == 5333
    assert replacement_cost <= nba["source_token_budget"] == 5502
    literal_hits = [
        p
        for p in currency["archived_pages"]
        if p.get("australian_currency_name_or_code_literal_present")
    ]
    assert len(literal_hits) == 1
    latest_page = next(
        p for p in recent["pages"] if "2024-nba-finals-mavericks" in p["url"]
    )
    assert latest_page["selected_ordinals"] == [1, 3, 5]
    record = {
        "reviewer": "Codex; offline original-case mechanical trace and targeted semantic review",
        "native_calls": 0,
        "original_scores_unchanged": True,
        "next_one_correction": "Data-bearing table admission within existing three-passages/source and token budgets",
        "table_admission": {
            "url": table_page["url"],
            "ord": 3,
            "sha256": table["sha256"],
            "row_count": len(rows),
            "explicit_positive_loss_rows": sum(
                r[losses].isdigit() and int(r[losses]) > 0 for r in rows
            ),
            "dash_values_kept_literal_not_zero": sum(r[losses] == "-" for r in rows),
            "actual_selected_ordinals": [0, 1, 2],
            "actual_table_selected": False,
            "actual_source_budget": 5502,
            "actual_used_cost": used,
            "table_cost": data_cost,
            "table_fits_even_without_replacement": used + data_cost <= 5502,
            "one_caption_replacement_cost": replacement_cost,
            "counterfactual_only_no_rerendered_answer": True,
        },
        "mechanical_findings": {
            "creative": "Existing native schema allows task=creative plus queries; host rejects it then chooses lookup. Empty-query host-only replay stays local. Blindly trusting creative still admits an unrelated factual request, so empty queries alone are not semantic qualification.",
            "champions_page": "Raw primary table has 81 rows; extraction loses the main table, preserving four legend pipe rows. Original raw/extracted bytes and selected passages remain separately bound.",
            "series_page": "Raw primary table has 1069 rows; extracted text hits 80000-character cap and starts with a data row used as a header. Multi-stage rows are not a verified Finals-only population.",
            "flattened_roles": "Raw Champion/Runner-Up headers become plain lines; only first selected chunk contains them. Later selected chunks have values without repeated roles. Actual answer reversals remain genuine contradictions.",
            "query_drift": "Fresh plan adds later-won relationship, but frozen batches ignore fresh queries. Original-question-only ranking reproduces identical selections in all three traces; causal changed retrieval is not established.",
            "currency": "All six supplied pages lack Australian-dollar/AUD text. Only unfetched JPY/USD archive has name/code in a menu; no country/property binding is established by that string hit. Native queries include both requested properties, unlike the old recorded provider queries.",
            "recent": "Saved queries cover 2022/2023/2024, not five current seasons. Even a game interpretation is not supported: later 2024 games 4/5 exist in fetched chunks 7/9 but selection keeps games 1/2/3, and answer mixes older games. Exact user granularity is ambiguous; neither completeness claim is qualified.",
        },
        "currency_unfetched_literal_hits": literal_hits,
        "recent_later_omitted_chunks": [
            {
                "ord": c["ord"],
                "sha256": c["sha256"],
                "table_header": c["markdown_tables"][0]["header"],
            }
            for c in latest_page["chunks"]
            if c["ord"] in (7, 9)
        ],
        "limits": [
            "Diagnostic header/cell checks establish exact relations only; they are not a general semantic verifier or new production grader.",
            "Source admission feasibility is not a model support/completeness pass.",
            "No original case/report is regraded and no release threshold is changed.",
            "Task-query invariants, lost extraction structure, missing coverage and answer compliance remain separate unresolved gates.",
        ],
    }
    target = OUT / "diagnosis.json"
    assert not target.exists()
    target.write_text(json.dumps(record, indent=2) + "\n")
    print(
        json.dumps(
            {
                "selected_cost": used,
                "table_cost": data_cost,
                "replacement_cost": replacement_cost,
                "budget": 5502,
                "native_calls": 0,
            }
        )
    )


if __name__ == "__main__":
    main()
