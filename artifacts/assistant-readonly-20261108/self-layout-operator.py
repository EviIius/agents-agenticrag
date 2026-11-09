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
if phase != "selected-self-layout":
    raise SystemExit("Choose one approved follow-up phase.")
stage = Path.home() / ".local/share/workbench/qa/assistant-as1-20261104"
directory = stage / "native-layout-20261108b"
directory.mkdir(mode=0o700, exist_ok=True)
lock = os.open(directory / "operator.lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
with os.fdopen(lock, "r+") as owned:
    fcntl.flock(owned, fcntl.LOCK_EX | fcntl.LOCK_NB)
    ledger = directory / "ledger.json"
    records = json.loads(private_read(ledger, 20_000)) if ledger.exists() else []
    if len(records) != 0:
        raise SystemExit("Wrong phase or follow-up budget already consumed.")
    private_write(directory / (phase + ".attempt"), b"one-shot role-only layout diagnosis; cap one")
    request = ProbeRequest(request_id=uuid.uuid4().hex, operation="structure", app="messages", expires_at=time.time() + 15)
    started = time.monotonic()
    async def run():
        result = {"scope": "as1-selected-self-layout", "phase": phase, "request_id": request.request_id,
                  "operation": "structure", "app": "messages", "automatic_retry": False}
        try:
            reply = await run_probe(stage / "build-03", "2b42d2f56b37226e5b26ecb6009957422fd8faea9eaf7635744c715c2c99d4ef", directory, request, approved_scope="as1-a")
            passed = reply.status == "ok" and bool(reply.nodes) and reply.nodes[0].role == "AXWindow"
            result.update(status=reply.status, trusted=reply.trusted, helper_identity=reply.helper_identity,
                          helper_pid=reply.helper_pid, target_pid=reply.target_pid, node_count=len(reply.nodes),
                          truncated=reply.truncated, gate_passed=passed)
        except BaseException as error:
            result.update(status="failed", failure_type=type(error).__name__, gate_passed=False)
        result.update(elapsed_seconds=round(time.monotonic() - started, 3), message_text_collected=False, screenshots=False, model_calls=0)
        private_write(stage / ("20261108-" + phase + ".summary.json"), json.dumps(result, indent=2).encode())
        print(json.dumps(result, indent=2))
        if result["gate_passed"] is not True:
            raise SystemExit(1)
    asyncio.run(run())
