"""Exercise the actual corrected capture and protocol gate offline before freeze."""

import asyncio
import hashlib
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ORIGINAL = OUT.parent / "search-repair"


def main():
    spec = importlib.util.spec_from_file_location(
        "offline_verifier", ORIGINAL / "verify_harness.py"
    )
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    source = (OUT / "experiment.py").read_text()
    assert not (OUT / "offline-validation.json").exists()
    with TemporaryDirectory() as temporary:
        folder = Path(temporary)
        result = asyncio.run(helper.exercise(source, folder))
        assert result["synthetic_planner_streams"] == 1
        assert not result["fallback"] and not result["search"]
        assert result["invalid_sampling_rejected_before_provider"]
        assert len(result["traces"]) == 3
        assert result["traces"][-1]["error"] == "AssertionError"
        namespace = {"json": json}
        exec(helper.extract_function(source, "protocol_verified"), namespace)
        gate = namespace["protocol_verified"]
        document = {"results": [{"turns": [{}]}]}
        wires = [{"body": json.dumps(row["payload"])} for row in result["traces"][:2]]
        (folder / "wire.jsonl").write_text("\n".join(map(json.dumps, wires)))
        assert not gate(folder, document)  # Swallowed assertion is recorded and rejected.
        (folder / "trace.jsonl").write_text("\n".join(map(json.dumps, result["traces"][:2])))
        assert gate(folder, document)
        (folder / "trace.jsonl").write_text(json.dumps(result["traces"][1]))
        assert not gate(folder, document)  # Answer alone cannot advance the sequence.
    (OUT / "offline-validation.json").write_text(
        json.dumps(
            {
                "actual_harness_sha256": hashlib.sha256(source.encode()).hexdigest(),
                "bound_planner_request_accepted": True,
                "valid_transform_skips_search": True,
                "invalid_sampling_rejected_before_provider": True,
                "protocol_gate_accepts_complete_planner_answer": True,
                "protocol_gate_rejects_missing_planner_or_swallowed_assertion": True,
                "mode": "Synthetic adapter with rejecting network transport; no inference",
                "real_model_calls": 0,
                "details": result,
            },
            indent=2,
        )
        + "\n"
    )
    print("Actual retest harness passes offline request and protocol validation; no inference.")


if __name__ == "__main__":
    main()
