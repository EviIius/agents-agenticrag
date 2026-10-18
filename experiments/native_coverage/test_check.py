import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "server"))
sys.path.insert(0, str(Path(__file__).parent))

from candidate import REMINDER, prompt  # noqa: E402
from check import check, warn_copy  # noqa: E402

from app.runs.agent_prompt import prompt as v1  # noqa: E402
from app.schemas import AgentInfo, AgentPart, ErrorDetail, Message, Stats  # noqa: E402

FIXTURES = json.loads((Path(__file__).parent / "fixtures.json").read_text())


@pytest.mark.parametrize("case", FIXTURES, ids=[c["id"] for c in FIXTURES])
def test_scope_and_false_positive_boundaries(case):
    report = check(case["text"], case["sources"])
    assert report.status == case["status"]
    assert [gap.line for gap in report.gaps] == case["gap_lines"]
    assert not report.claim_support_checked and not report.sentence_coverage_checked


@pytest.mark.parametrize("count", [-1, True, 1.5, "1"])
def test_invalid_source_metadata_is_not_silently_accepted(count):
    with pytest.raises(ValueError):
        check("- Synthetic value", count)


def message():
    return Message(
        id="fake-coverage",
        chat_id="fake",
        parent_id=None,
        role="assistant",
        content="- Synthetic value",
        reasoning="Synthetic reasoning",
        status="complete",
        created_at="2026-10-18",
        stats=Stats(),
        agent=AgentInfo(source_count=1),
        parts=[AgentPart(type="text", text="- Synthetic value")],
    )


def test_warning_changes_only_notice_on_a_copy():
    original = message()
    before = original.model_dump()
    annotated, report = warn_copy(original, 1)
    assert len(report.gaps) == 1 and original.model_dump() == before
    after = annotated.model_dump()
    notice = after["agent"].pop("notice")
    before["agent"].pop("notice")
    assert after == before
    assert notice["code"] == "citation_coverage"
    assert "verified" not in notice["message"].lower()


@pytest.mark.parametrize("state", ["ordinary", "stopped", "streaming", "error", "notice"])
def test_ordinary_partial_and_existing_notice_messages_unchanged(state):
    original = message()
    if state == "ordinary":
        original.agent = None
    elif state == "notice":
        original.agent.notice = ErrorDetail(code="invalid_citation", message="Existing warning")
    else:
        original.status = state
    annotated, report = warn_copy(original, 1)
    assert report.gaps
    assert annotated.model_dump() == original.model_dump()


def test_retained_results_detect_failure_without_regrading_or_rewriting():
    for task, gaps in (("S1-H01", 0), ("S1-H02", 4)):
        file = ROOT / f"artifacts/agent-loop/n1/{task}/result.json"
        before = hashlib.sha256(file.read_bytes()).hexdigest()
        result = json.loads(file.read_text())
        original = Message.model_validate(result["message"])
        annotated, report = warn_copy(original, original.agent.source_count)
        assert len(report.gaps) == gaps
        assert annotated.content == original.content
        assert hashlib.sha256(file.read_bytes()).hexdigest() == before
        manual = json.loads((file.parent / "manual-review.json").read_text())
        assert manual["checks"]["citations"] is (gaps == 0)


def test_v2_is_only_a_generic_unexecuted_append_and_v1_stays_frozen():
    hashes = {
        "web": "d973c913f70a422ddeaf193eb6738121bd16c18917a2b75e5a024cd3df942b92",
        "library": "0edb998196d7a6116c8f6f50d8f0ecf6c471f9cd9da3f73e60ebdf2aedd743e5",
    }
    for kind, digest in hashes.items():
        assert hashlib.sha256(v1(kind).encode()).hexdigest() == digest
        assert prompt(kind) == v1(kind) + "\n" + REMINDER
    assert not any(token in REMINDER for token in ("Lantern", "Cedar", "480", "[1]"))


def test_issued_citation_is_not_proof_of_claim_support_or_sentence_coverage():
    report = check("- Unsupported fictional detail [1]. Another uncited claim.", 1)
    assert report.status == "no_obvious_gaps"
    assert not report.claim_support_checked and not report.sentence_coverage_checked
