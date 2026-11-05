import asyncio
import fcntl
import json
import os
import sys
import time
import uuid
from pathlib import Path

root = Path("/Users/evilius/.codex/worktrees/harness-m0-1/agents-agenticrag")
sys.path.insert(0, str(root / "server"))
from app.assistant.mac_probe import ProbeRequest, private_read, private_write, run_probe

phase = sys.argv[1] if len(sys.argv) == 2 else ""
if phase not in {"notes-window", "revoked"}:
    raise SystemExit("Choose one approved follow-up phase.")
stage = Path.home() / ".local/share/workbench/qa/assistant-as1-20261104"
directory = stage / "native-followup"
directory.mkdir(mode=0o700, exist_ok=True)
lock = os.open(directory / "operator.lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
with os.fdopen(lock, "r+") as owned:
    fcntl.flock(owned, fcntl.LOCK_EX | fcntl.LOCK_NB)
    ledger = directory / "ledger.json"
    records = json.loads(private_read(ledger, 20_000)) if ledger.exists() else []
    if len(records) != (0 if phase == "notes-window" else 1):
        raise SystemExit("Wrong phase or follow-up budget already consumed.")
    if phase == "revoked":
        previous = json.loads(private_read(stage / "followup-notes-window.summary.json", 10_000))
        if previous.get("gate_passed") is not True:
            raise SystemExit("The first follow-up did not pass; stop.")
    private_write(directory / (phase + ".attempt"), b"approved AS1-A2 one-shot")
    request = ProbeRequest(request_id=uuid.uuid4().hex, operation="structure", app="notes", expires_at=time.time() + 15)
    started = time.monotonic()
    async def run():
        result = {"scope": "as1-a2", "phase": phase, "request_id": request.request_id,
                  "operation": "structure", "app": "notes", "automatic_retry": False}
        try:
            reply = await run_probe(stage / "build-03", "2b42d2f56b37226e5b26ecb6009957422fd8faea9eaf7635744c715c2c99d4ef", directory, request, approved_scope="as1-a")
            passed = (reply.status == "ok" and bool(reply.nodes) and reply.nodes[0].role == "AXWindow") if phase == "notes-window" else (reply.status == "permission_required" and reply.trusted is False and not reply.nodes and reply.target_pid is None)
            result.update(status=reply.status, trusted=reply.trusted, helper_identity=reply.helper_identity,
                          helper_pid=reply.helper_pid, target_pid=reply.target_pid, node_count=len(reply.nodes),
                          truncated=reply.truncated, gate_passed=passed)
        except BaseException as error:
            result.update(status="failed", failure_type=type(error).__name__, gate_passed=False)
        result.update(elapsed_seconds=round(time.monotonic() - started, 3), message_text_collected=False, screenshots=False, model_calls=0)
        private_write(stage / ("followup-" + phase + ".summary.json"), json.dumps(result, indent=2).encode())
        print(json.dumps(result, indent=2))
        if result["gate_passed"] is not True:
            raise SystemExit(1)
    asyncio.run(run())
