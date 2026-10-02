import json
import re
from pathlib import Path

from evals.web.grading import required_facts

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
