"""Read retained synthetic answers, write new diagnostics; never run a model."""

import hashlib
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "server"))
sys.path.insert(0, str(Path(__file__).parent))

from candidate import prompt  # noqa: E402
from check import warn_copy  # noqa: E402

from app.runs.agent_prompt import prompt as v1  # noqa: E402
from app.schemas import Message  # noqa: E402


def main():
    out = ROOT / "artifacts/agent-loop/coverage-v1"
    out.mkdir(parents=True, exist_ok=True)
    replays = []
    for task in ("S1-H01", "S1-H02"):
        source = ROOT / f"artifacts/agent-loop/n1/{task}/result.json"
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        original = Message.model_validate(json.loads(source.read_text())["message"])
        copy, report = warn_copy(original, original.agent.source_count)
        replays.append(
            {
                "task": task,
                "source_sha256": digest,
                "report": asdict(report),
                "original_notice": original.agent.notice,
                "proposed_notice": copy.agent.notice.model_dump() if copy.agent.notice else None,
                "content_unchanged": copy.content == original.content,
                "original_grade_unchanged": True,
            }
        )
        assert hashlib.sha256(source.read_bytes()).hexdigest() == digest
    (out / "replay.json").write_text(
        json.dumps(
            {
                "native_calls": 0,
                "detection_only": True,
                "answer_gain_established": False,
                "replays": replays,
            },
            indent=2,
        )
        + "\n"
    )
    candidates = {
        kind: {
            "v1_sha256": hashlib.sha256(v1(kind).encode()).hexdigest(),
            "v2_sha256": hashlib.sha256(prompt(kind).encode()).hexdigest(),
            "v2_prompt": prompt(kind),
            "executed_natively": False,
        }
        for kind in ("web", "library")
    }
    (out / "candidate-prompts.json").write_text(json.dumps(candidates, indent=2) + "\n")
    print(
        json.dumps(
            {
                "native_calls": 0,
                "gap_counts": {item["task"]: len(item["report"]["gaps"]) for item in replays},
                "candidate_executed": False,
            }
        )
    )


if __name__ == "__main__":
    main()
