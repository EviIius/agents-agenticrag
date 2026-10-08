"""Offline checks for gate evidence and strict native-call validation."""

import json
from pathlib import Path

import pytest
from probe_tools import validate
from run_search_gate import OUT, WEB, settings

HERE = Path(__file__).resolve().parent
TOOLS = json.loads((HERE / "tools.json").read_text())
SCHEMAS = {t["function"]["name"]: t["function"]["parameters"] for t in TOOLS}


@pytest.mark.parametrize(
    "call",
    [
        '{"name": "finish"}',
        {"content": "I will call finish now"},
        {"function": {"name": [], "arguments": {}}},
        {"function": {"name": "send_email", "arguments": {}}},
        {"function": {"name": "web_search", "arguments": "not JSON"}},
        {"function": {"name": "web_search", "arguments": []}},
        {"function": {"name": "web_search", "arguments": {}}},
        {"function": {"name": "web_search", "arguments": {"query": 12}}},
        {"function": {"name": "web_search", "arguments": {"query": " "}}},
        {"function": {"name": "web_search", "arguments": {"query": "x" * 201}}},
        {"function": {"name": "web_search", "arguments": {"query": "public", "freshness": "hour"}}},
        {"function": {"name": "read_page", "arguments": {"url": "https://example.com"}}},
        {"function": {"name": "finish", "arguments": {"answer": "x"}}},
    ],
)
def test_rejects_malformed_or_prose_calls(call):
    assert validate(call, SCHEMAS)[0] is False


@pytest.mark.parametrize(
    "name,arguments",
    [
        ("web_search", {"query": "x" * 200, "freshness": "week"}),
        ("read_page", {"url": "https://example.com", "focus": "launch date"}),
        ("finish", {}),
    ],
)
def test_valid_native_calls_accept_object_or_json_arguments(name, arguments):
    assert validate({"function": {"name": name, "arguments": arguments}}, SCHEMAS) == (
        True,
        "valid",
    )
    assert validate({"function": {"name": name, "arguments": json.dumps(arguments)}}, SCHEMAS) == (
        True,
        "valid",
    )


def test_protocol_prompts_are_independent_and_cover_all_tools():
    cases = json.loads((HERE / "probe_cases.json").read_text())
    assert len(cases) == len({c["id"] for c in cases}) == 40
    assert {c["expected_tool"] for c in cases} == set(SCHEMAS)
    assert all(c["messages"] and c["messages"][-1]["role"] == "user" for c in cases)


def test_research_cases_require_multiple_public_references():
    cases = json.loads((HERE / "cases.yaml").read_text())
    assert len(cases) == len({c["id"] for c in cases}) == 15
    for case in cases:
        references = case["research"]["references"]
        assert len({ref["url"] for ref in references}) >= 2
        assert all(ref["url"].startswith("https://") and ref["facts"] for ref in references)
        assert case["expect"]["search"] is True
        assert len(case["expect"]["must_include"]) >= 2
        assert case["expect"]["min_citations"] == 2


def test_search_wrapper_keeps_production_trials_and_sampling_unchanged():
    for mode in ["baseline-record", "baseline-replay", "release-live", "release-replay"]:
        config = settings(mode, "synthetic-model", "")
        assert config.temperature is None
        assert config.answer_trial == config.planner_trial == "spec"
        assert config.table_trial == config.evidence_format == config.ranking_query == "spec"
        assert config.fill_trial == "spec" and config.filter_proof == ""
        assert config.question_first is False and config.replay_plans is False
        assert config.ranking == "keyword"
        if mode.startswith("baseline"):
            assert config.cases_file == str(HERE / "cases.yaml")
            assert config.fixture_root == str(OUT / "web-fixtures")
        else:
            assert config.cases_file == str(WEB / "cases.yaml")
    assert settings("release-live", "synthetic-model", "").live is True
    assert settings("baseline-record", "synthetic-model", "").record is True
    assert settings("baseline-replay", "synthetic-model", "").replay_corpus is True
