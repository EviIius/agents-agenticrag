"""One capability-only diagnostic; no private text values are requested/printed."""

import asyncio
import json
import os
import sys
import time
import uuid
from pathlib import Path

ROOT = Path("/Users/evilius/.codex/worktrees/harness-m0-1/agents-agenticrag")
sys.path.insert(0, str(ROOT / "server"))
from app.assistant.contracts import Contract
from app.assistant.mac_probe import ProbeFailure, helper_pid, private_read, private_write
from app.assistant.mac_reader import ReadRequest, run_read_probe


class Row(Contract):
    value_modifiability_status: int
    value_settable: bool
    attribute_names_status: int
    has_value: bool
    has_character_count: bool
    parameterized_names_status: int
    has_string_for_range: bool


def validate(raw: bytes, request: ReadRequest, pid: int) -> dict:
    value = json.loads(raw)
    assert set(value) == {
        "protocol", "request_id", "operation", "app", "status", "trusted",
        "helper_identity", "helper_pid", "target_pid", "bundle_id", "diagnostics",
    }
    assert type(value["protocol"]) is int and value["protocol"] == 1
    assert value["request_id"] == request.request_id and value["operation"] == "read_selected"
    assert value["app"] == "messages" and value["bundle_id"] == "com.apple.MobileSMS"
    assert value["helper_identity"] == "dev.agenticrag.aether.desktop-trial"
    assert type(value["helper_pid"]) is int and value["helper_pid"] == pid
    assert type(value["target_pid"]) is int and value["target_pid"] > 1
    assert value["status"] == "ok" and value["trusted"] is True
    diagnostic = value["diagnostics"]
    assert set(diagnostic) == {"area_count", "areas"}
    assert type(diagnostic["area_count"]) is int and 1 <= diagnostic["area_count"] <= 8
    assert len(diagnostic["areas"]) == diagnostic["area_count"]
    rows = [Row.model_validate(row).model_dump() for row in diagnostic["areas"]]
    return {"area_count": len(rows), "areas": rows}


async def main() -> None:
    stage = Path.home() / ".local/share/workbench/qa/assistant-as1b-20261105"
    directory = stage / "native-capabilities"
    directory.mkdir(mode=0o700, exist_ok=True)
    private_write(directory / "one-shot.attempt", b"capability flags only; max one")
    request = ReadRequest(
        request_id=uuid.uuid4().hex, operation="read_selected", app="messages",
        expires_at=time.time() + 15,
    )
    result = {"scope": "capability-flags-only", "request_id": request.request_id,
              "model_calls": 0, "text_value_requested": False, "screenshots": False,
              "automatic_retry": False, "gate_passed": False}
    try:
        try:
            # The transport owns the exact process/deadline. Its old candidate
            # parser deliberately refuses this separate diagnostics-only reply.
            await run_read_probe(
                stage / "build-04-capabilities",
                "88ad28d7ee64042f2f99a0094677ffaaf7a214ac79eb07bfd6b4228ca3c1d0ac",
                directory, request, approved_scope="as1-b1",
            )
            raise RuntimeError("Unexpected candidate protocol.")
        except ProbeFailure:
            pass
        job = directory / request.request_id
        diagnostic = validate(private_read(job / "response.json", 16000), request, helper_pid(job))
        result.update(diagnostic)
        result["gate_passed"] = True
    except BaseException as error:
        result["failure_type"] = type(error).__name__
    private_write(stage / "capabilities.summary.json", json.dumps(result, indent=2).encode())
    print(json.dumps(result, indent=2))
    if result["gate_passed"] is not True:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
