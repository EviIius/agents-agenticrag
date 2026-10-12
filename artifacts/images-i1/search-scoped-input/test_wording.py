"""Equivalent-decline positives/negatives; non-decline regex parity."""

import importlib.util
from pathlib import Path

import pytest
import wording

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "original_grading", ROOT / "server/evals/web/grading.py"
)
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)


@pytest.mark.parametrize(
    "answer",
    [
        "The provided information does not establish the requested fact.",
        "The source does not specify the missing measurement.",
        "Those records do not establish your identity.",
        "The value isn't known from these records.",
        "The date isn’t established by the source.",
        "It is not established by these sources.",
        "I cannot determine that from this source.",
        "There is no evidence for that in the provided record.",
        "The records didn't provide the missing value.",
    ],
)
@pytest.mark.parametrize("pattern", list(wording.PATTERNS))
def test_equivalent_decline_forms(answer, pattern):
    assert wording.required_facts(answer, {"must_include": [pattern]})


@pytest.mark.parametrize(
    "answer",
    [
        'The sentence says "does not establish".',
        "The phrase 'not established' was quoted.",
        "The phrase ‘cannot determine’ appears in the passage.",
        "> The value is not known.\nA quotation is not my answer.",
        "`not established` is a string literal.",
        "```text\nI cannot determine it.\n```\nThat is an example.",
        "It is not true that the sources do not establish the answer.",
        "It is false that I cannot determine it.",
        "I don't think I cannot determine it.",
        "The claim that there is no evidence is incorrect.",
        "The fact is not unknown.",
        "I am not unable to identify it.",
        "The evidence establishes the value.",
    ],
)
def test_quoted_negated_and_affirmative_forms_are_not_declines(answer):
    assert not wording.required_facts(answer, {"must_include": [wording.BASE]})


@pytest.mark.parametrize(
    "expect,answer",
    [
        (
            {"must_include": [r"(no|not|cannot|without).{0,50}(body|content)"]},
            "No body is permitted.",
        ),
        ({"must_include": ["23", "41"]}, "23, but the other value is not established."),
        ({"must_include": ["source-only"]}, "The missing fact is not established."),
        ({"must_include_one_of": [["x", "y"], ["z"]]}, "x and y"),
        ({"must_include_last": ["372"], "must_include": ["999"]}, "372"),
        (
            {"must_include": [wording.BASE, "372"]},
            "The answer is not established; 372 is supplied.",
        ),
    ],
)
def test_non_decline_patterns_and_alternative_structure_keep_original_semantics(expect, answer):
    assert wording.required_facts(answer, expect) == original.required_facts(answer, expect)


def test_equivalent_decline_does_not_waive_other_required_values():
    expect = {"must_include": [wording.BASE, "372"]}
    assert not wording.required_facts(
        "The provided evidence does not establish the answer.", expect
    )


def test_wording_match_does_not_prove_semantic_safety():
    # This positive wording with an unsupported addition must still fail manual
    # subject/claim support. Do not disguise lexical scoring as a semantic judge.
    answer = "The provided evidence does not establish your age. You are 47 years old."
    assert wording.required_facts(answer, {"must_include": [wording.BASE]})
