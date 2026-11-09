"""Three declared read-only store requests. Only sanitized counts/statuses reach stdout."""

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
from app.assistant.mac_messages_store import StoreRequest, run_store, validate_store
from app.assistant.mac_probe import private_read, private_write

STAGE = Path.home() / ".local/share/workbench/qa/assistant-messages-store-20261109"


async def trial(phase: str, manifest: dict) -> dict:
    request = StoreRequest(
        request_id=uuid.uuid4().hex,
        operation="resolve_self" if phase == "resolve" else "read_thread",
        expires_at=time.time() + 15,
    )
    start = time.monotonic()
    result = {
        "phase": phase,
        "request_id": request.request_id,
        "scope": "messages-store-self",
        "gate_passed": False,
        "model_calls": 0,
        "input_or_send": False,
        "private_values_in_output": False,
        "automatic_retry": False,
    }
    try:
        reply = await run_store(
            STAGE / "build-07",
            manifest["build_manifest_sha256"],
            STAGE / "native",
            request,
            approved_scope="messages-store-self",
        )
        result.update(status=reply.status, helper_pid=reply.helper_pid)
        if phase == "resolve":
            selected = json.loads(private_read(STAGE / "selection.json", 1024))
            result["gate_passed"] = (
                reply.status == "ok"
                and reply.target is not None
                and reply.target.address == selected["address"]
            )
            result["native_target_present"] = reply.target is not None
        elif phase == "read":
            first = json.loads(private_read(STAGE / "resolve.summary.json", 6000))
            original = StoreRequest.model_validate_json(
                private_read(STAGE / "native" / first["request_id"] / "request.json", 4096)
            )
            bound = validate_store(
                private_read(STAGE / "native" / first["request_id"] / "response.json", 100_000),
                original,
            )
            result["gate_passed"] = (
                reply.status == "ok"
                and reply.snapshot is not None
                and reply.snapshot.target == bound.target
            )
            if reply.snapshot:
                messages = reply.snapshot.messages
                result.update(
                    message_count=len(messages),
                    text_bytes=sum(len(m.text.encode()) for m in messages),
                    incoming_count=sum(not m.from_me for m in messages),
                    outgoing_count=sum(m.from_me for m in messages),
                    latest_incoming_present=reply.snapshot.latest_incoming_guid is not None,
                    native_guids_unique=len({m.guid for m in messages}) == len(messages),
                    source_still_unqualified=True,
                )
        else:
            result["gate_passed"] = (
                reply.status == "permission_required"
                and reply.target is None
                and reply.snapshot is None
            )
    except BaseException as error:
        result.update(status="failed", failure_type=type(error).__name__)
    result["elapsed_seconds"] = round(time.monotonic() - start, 3)
    private_write(STAGE / (phase + ".summary.json"), json.dumps(result, indent=2).encode())
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=["resolve", "read", "revoked"])
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--user-setup-confirmed", action="store_true")
    parser.add_argument("--user-revocation-confirmed", action="store_true")
    args = parser.parse_args()
    if args.phase == "resolve" and not args.user_setup_confirmed:
        raise SystemExit(
            "User confirmation of private selection and exact helper access is required."
        )
    if args.phase == "revoked" and not args.user_revocation_confirmed:
        raise SystemExit("User confirmation of manual revocation is required.")
    source = ROOT / "artifacts/assistant-messages-store-20261109/source-manifest.json"
    if hashlib.sha256(source.read_bytes()).hexdigest() != args.manifest_sha256:
        raise SystemExit("The frozen store manifest changed.")
    manifest = json.loads(source.read_bytes())
    for name, sha in manifest["files"].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != sha:
            raise SystemExit("The frozen store source changed.")
    directory = STAGE / "native"
    directory.mkdir(mode=0o700, exist_ok=True)
    descriptor = os.open(directory / "operator.lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, "r+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        records = (
            json.loads(private_read(directory / "ledger.json", 6000))
            if (directory / "ledger.json").exists()
            else []
        )
        expected = ["resolve", "read", "revoked"].index(args.phase)
        if len(records) != expected:
            raise SystemExit("Wrong phase or the three-request scope is consumed/stopped.")
        for previous in ["resolve", "read"][:expected]:
            summary = json.loads(private_read(STAGE / (previous + ".summary.json"), 6000))
            if summary.get("gate_passed") is not True:
                raise SystemExit("The previous gate failed; unused requests stay sealed.")
        private_write(directory / (args.phase + ".attempt"), b"one-shot; no retries")
        result = asyncio.run(trial(args.phase, manifest))
        print(json.dumps(result, indent=2))
        if result["gate_passed"] is not True:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
