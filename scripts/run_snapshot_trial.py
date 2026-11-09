"""Two one-shot private snapshot checks, with no inference, input or private output."""

import argparse
import asyncio
import fcntl
import hashlib
import json
import os
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
from app.assistant.mac_probe import private_read, private_write
from app.assistant.mac_snapshot import SnapshotRequest, run_snapshot

STAGE = Path.home() / ".local/share/workbench/qa/assistant-readonly-20261108"


async def trial(phase: str, manifest: dict) -> dict:
    request = SnapshotRequest(request_id=uuid.uuid4().hex, expires_at=time.time() + 15)
    start = time.monotonic()
    result = {
        "scope": "readonly-self",
        "phase": phase,
        "request_id": request.request_id,
        "model_calls": 0,
        "input_or_send": False,
        "screenshots": False,
        "private_values_in_output": False,
        "automatic_retry": False,
        "gate_passed": False,
    }
    try:
        reply = await run_snapshot(
            STAGE / "build-02",
            manifest["build_manifest_sha256"],
            STAGE / "native-v2",
            request,
            approved_scope="readonly-self",
        )
        result.update(
            status=reply.status,
            failure_stage=reply.failure_stage,
            helper_pid=reply.helper_pid,
            target_pid=reply.target_pid,
            trusted=reply.trusted,
            snapshot_qualified=False,
        )
        if phase == "read":
            result["gate_passed"] = reply.status == "ok" and reply.snapshot is not None
        else:
            result["gate_passed"] = (
                reply.status == "permission_required"
                and reply.trusted is False
                and reply.snapshot is None
                and reply.target_pid is None
            )
        if reply.snapshot is not None:
            snapshot = reply.snapshot
            items = snapshot.items
            result.update(
                access=snapshot.access,
                area_count=len(items),
                nonempty_value_count=sum(bool(item.value) for item in items),
                accepted_value_bytes=sum(len(item.value.encode()) for item in items),
                value_settable_count=sum(item.value_settable for item in items),
                identifier_count=sum(bool(item.identifier) for item in items),
                distinct_nonempty_identifier_count=len(
                    {item.identifier for item in items if item.identifier}
                ),
                description_count=sum(bool(item.description) for item in items),
                subrole_count=sum(bool(item.subrole) for item in items),
                group_identifier_present=bool(snapshot.group_identifier),
                window_title_present=bool(snapshot.window_title),
            )
    except BaseException as error:
        result.update(status="failed", failure_type=type(error).__name__)
    result["elapsed_seconds"] = round(time.monotonic() - start, 3)
    private_write(STAGE / ("v2-" + phase + ".summary.json"), json.dumps(result, indent=2).encode())
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=["read", "revoked"])
    parser.add_argument("--manifest-sha256", required=True)
    args = parser.parse_args()
    source = ROOT / "artifacts/assistant-readonly-20261108/source-manifest-v2.json"
    if hashlib.sha256(source.read_bytes()).hexdigest() != args.manifest_sha256:
        raise SystemExit("The frozen snapshot manifest changed.")
    manifest = json.loads(source.read_text())
    for path, digest in manifest["files"].items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != digest:
            raise SystemExit("The frozen snapshot source changed.")
    directory = STAGE / "native-v2"
    directory.mkdir(mode=0o700, exist_ok=True)
    descriptor = os.open(directory / "operator.lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, "r+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        ledger = directory / "ledger.json"
        records = json.loads(private_read(ledger, 2000)) if ledger.exists() else []
        if len(records) != (0 if args.phase == "read" else 1):
            raise SystemExit("Wrong phase or the two-request budget is consumed.")
        if args.phase == "revoked":
            first = json.loads(private_read(STAGE / "v2-read.summary.json", 6000))
            if first.get("gate_passed") is not True:
                raise SystemExit("The read failed; its remaining request is not available.")
        private_write(directory / (args.phase + ".attempt"), b"one-shot; no automatic retry")
        result = asyncio.run(trial(args.phase, manifest))
        print(json.dumps(result, indent=2))
        if result["gate_passed"] is not True:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
