import json
import re
from pathlib import Path

from evals.web.grading import citation_coverage, cited_list_items, required_facts

CASES = json.loads((Path(__file__).parents[1] / "evals/web/cases.yaml").read_text())


def test_result_table_counts_are_equivalent_to_series_score() -> None:
    expect = next(case["expect"] for case in CASES if case["id"] == "nba-2021")
    table = (
        "The Phoenix Suns lost to Milwaukee Bucks.\n"
        "| Team | Coach | Wins |\n|---|---|---|\n"
        "| Milwaukee Bucks | Coach A | 4 |\n| Phoenix Suns | Coach B | 2 | [1]"
    )
    assert required_facts(table, expect)
    assert not required_facts(table.replace("| 4 |", "| 3 |"), expect)
    assert not required_facts(table.replace("Coach | Wins", "Coach | Losses"), expect)
    assert not required_facts(
        table.replace("Milwaukee Bucks | Coach A | 4", "Milwaukee Bucks | Coach A | 2"), expect
    )


def test_non_losing_team_is_rejected_even_with_invented_loss_count() -> None:
    expect = next(case["expect"] for case in CASES if case["id"] == "nba-all-losses")
    forbidden = expect["must_not_match"]
    for answer in ["- Chicago Bulls (6 losses) [1]", "| Denver Nuggets | 1 | [1]"]:
        assert any(re.search(pattern, answer, re.I) for pattern in forbidden)
    assert not any(
        re.search(pattern, "Excluded: Chicago Bulls have no Finals losses. [1]", re.I)
        for pattern in forbidden
    )


def test_list_requires_each_item_citation_and_rejects_wrong_population_total() -> None:
    assert cited_list_items("- A: 2 [1]\n- B: 3 [1]")
    assert cited_list_items("| Name | Value |\n|---|---|\n| A | 2 [1] |\n| B | 3 [1] |")
    assert not cited_list_items("From source [1]:\n- A: 2\n- B: 3")
    assert not cited_list_items("- A: 2 [1]\n- B: 3")
    forbidden = next(
        case["expect"]["must_not_match"] for case in CASES if case["id"] == "nba-all-losses"
    )
    assert any(
        re.search(pattern, "This list includes all 28 teams.", re.I) for pattern in forbidden
    )
    assert not any(
        re.search(pattern, "Of 28 finalists, this list includes 23 that lost.", re.I)
        for pattern in forbidden
    )


def test_release_requires_cited_version_changes_and_official_provenance() -> None:
    expect = next(case["expect"] for case in CASES if case["id"] == "ollama-latest")
    official = [{"n": 1, "url": "https://github.com/ollama/ollama/releases/tag/v1.2.3"}]
    answer = "Latest release: v1.2.3 [1].\n\nChanges include:\n- Added a feature [1]."
    assert expect["min_citations"] == 1
    assert citation_coverage(answer, official, expect)
    assert citation_coverage(
        "Latest version v1.2.3 [1]. Changes include:\n- Added a feature [1].", official, expect
    )
    assert citation_coverage(
        "Version v1.2.3 [1].\nChanges include:\n- Updates to the engine [1].\n- Fix a hang [1].",
        official,
        expect,
    )
    assert not citation_coverage(answer.replace("v1.2.3 [1]", "v1.2.3"), official, expect)
    assert not citation_coverage(answer.replace("feature [1]", "feature"), official, expect)
    assert not citation_coverage(answer + "\n- Fixed another feature.", official, expect)
    assert not citation_coverage(answer.replace("[1]", "[2]"), official, expect)
    assert not citation_coverage(
        answer, [{"n": 1, "url": "https://example.org/release-copy"}], expect
    )
    assert not citation_coverage("See the official notes [1].", official, expect)
    assert citation_coverage("Ordinary answer", [], {})
