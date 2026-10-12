"""No inference: call count, evidence, sampling and continuation guards."""

import json
from pathlib import Path

import native
import pytest


def records(folder: Path):
    planner = {
        "model": native.MODEL,
        "messages": [{"role": "user", "content": "synthetic"}],
        "stream": True,
        "format": {"type": "object"},
        "options": {"temperature": 0.2, "num_predict": 256, "num_ctx": 16384},
    }
    answer = {
        "model": native.MODEL,
        "messages": [{"role": "user", "content": "synthetic source"}],
        "stream": True,
        "options": {"num_ctx": 16384},
    }
    traces = [
        {
            "payload": payload,
            "error": None,
            "capacity_enabled": True,
            "events": [
                {"type": "Usage", "value": {}},
                {"type": "Finish", "value": {"reason": "stop"}},
            ],
        }
        for payload in (planner, answer)
    ]
    wires = [{"model": native.MODEL, "messages": [], "stream": False}, planner, answer]
    selection = {"after": []}
    document = {
        "results": [
            {"id": "nba-all-losses", "turns": [{"sources": [], "web": {"plan_fallback": False}}]}
        ]
    }
    return traces, wires, selection, document


def save(folder, traces, wires, selection):
    (folder / "trace.jsonl").write_text("".join(json.dumps(r) + "\n" for r in traces))
    (folder / "wire.jsonl").write_text(
        "".join(json.dumps({"body": json.dumps(r)}) + "\n" for r in wires)
    )
    (folder / "admission.jsonl").write_text(json.dumps(selection) + "\n")


def test_exact_three_wire_calls_and_original_parameters(tmp_path):
    rows = records(tmp_path)
    save(tmp_path, *rows[:3])
    assert all(native.protocol(tmp_path, rows[3]).values())


@pytest.mark.parametrize(
    "fault",
    [
        "extra_answer",
        "extra_warm",
        "changed_sampling",
        "tools",
        "stream_error",
        "no_capacity",
        "no_finish",
        "wrong_evidence",
        "fallback",
        "wire_tamper",
    ],
)
def test_protocol_rejects_faults(tmp_path, fault):
    traces, wires, selection, document = records(tmp_path)
    if fault == "extra_answer":
        traces.append(traces[-1])
        wires.append(wires[-1])
    elif fault == "extra_warm":
        wires.append(wires[0])
    elif fault == "changed_sampling":
        traces[-1]["payload"]["options"]["temperature"] = 0.7
    elif fault == "tools":
        traces[-1]["events"].append({"type": "ToolCall", "value": {}})
    elif fault == "stream_error":
        traces[-1]["error"] = "RuntimeError"
    elif fault == "no_capacity":
        traces[-1]["capacity_enabled"] = False
    elif fault == "no_finish":
        traces[-1]["events"].pop()
    elif fault == "wrong_evidence":
        document["results"][0]["turns"][0]["sources"] = [{"passages": [{"text": "changed"}]}]
    elif fault == "fallback":
        document["results"][0]["turns"][0]["web"]["plan_fallback"] = True
    elif fault == "wire_tamper":
        wires[-1] = {**wires[-1], "keep_alive": 1}
    save(tmp_path, traces, wires, selection)
    assert not all(native.protocol(tmp_path, document).values())


def test_original_case_arguments_do_not_enable_experiments():
    args = native.evaluation_args()
    assert args.case == "nba-all-losses" and args.temperature is None
    assert args.ranking == "keyword" and not args.replay_plans
    assert not args.live and not args.record and args.replay_corpus
    assert all(
        getattr(args, name) == "spec"
        for name in [
            "planner_trial",
            "answer_trial",
            "table_trial",
            "evidence_format",
            "ranking_query",
            "fill_trial",
        ]
    )
    assert not args.question_first and not args.filter_proof and not args.search_key_db


@pytest.mark.parametrize("fault", ["stopped", "failed_manual", "missing_review", "changed_report"])
def test_no_continuation_after_failure_or_unreviewed_result(tmp_path, monkeypatch, fault):
    monkeypatch.setattr(native, "OUT", tmp_path)
    monkeypatch.setattr(native, "frozen", lambda: None)
    (tmp_path / "make-e2e.log").write_text("473 passed; 3 skipped")
    (tmp_path / "make-check.log").write_text("508 passed")
    (tmp_path / "execution.json").write_text(json.dumps({"order": [["later", "candidate"]]}))
    state = {
        "runs": [{"label": "previous", "arm": "candidate", "report_sha256": "original"}],
        "stop": "failure" if fault == "stopped" else None,
    }
    (tmp_path / "ordered-results.json").write_text(json.dumps(state))
    if fault != "missing_review":
        (tmp_path / "previous-review.json").write_text(
            json.dumps(
                {
                    "protocol_verified": True,
                    "passed": fault != "failed_manual",
                    "report_sha256": "changed" if fault == "changed_report" else "original",
                }
            )
        )
    # If the guard falls through, this is a bug, not a network attempt.
    monkeypatch.setattr(native, "preflight", lambda: pytest.fail("Unreviewed native continuation"))
    with pytest.raises((AssertionError, FileNotFoundError)):
        native.run_next()
