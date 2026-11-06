import asyncio, fcntl, hashlib, json, os, sys, time, uuid
from pathlib import Path
root = Path("/Users/evilius/.codex/worktrees/harness-m0-1/agents-agenticrag")
frozen_path = root / "artifacts/assistant-as1b-20261105/source-manifest.json"
if hashlib.sha256(frozen_path.read_bytes()).hexdigest() != "1cb5e459fdd26b518495d3b401bd76dcbe0a133f28b1e7e5506e82770fae3a0a":
    raise SystemExit("The reviewed source manifest changed; stop.")
for path, digest in json.loads(frozen_path.read_text())["files"].items():
    if hashlib.sha256((root / path).read_bytes()).hexdigest() != digest:
        raise SystemExit("The reviewed source changed; stop.")
sys.path.insert(0, str(root / "server"))
from app.assistant.mac_probe import private_read, private_write
from app.assistant.mac_reader import ReadRequest, run_read_probe
phase = sys.argv[1] if len(sys.argv) == 2 else ""
phases = {"permission": 0, "read": 1, "revoked": 2}
if phase not in phases:
    raise SystemExit("Choose one reviewed AS1-B1 phase.")
stage = Path.home() / ".local/share/workbench/qa/assistant-as1b-20261105"
directory = stage / "native-b1"
directory.mkdir(mode=0o700, exist_ok=True)
lock = os.open(directory / "operator.lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
with os.fdopen(lock, "r+") as owned:
    fcntl.flock(owned, fcntl.LOCK_EX | fcntl.LOCK_NB)
    ledger = directory / "ledger.json"
    records = json.loads(private_read(ledger, 20000)) if ledger.exists() else []
    if len(records) != phases[phase]:
        raise SystemExit("Wrong phase or trial budget already consumed.")
    if phase != "permission":
        previous_phase = "permission" if phase == "read" else "read"
        previous = json.loads(private_read(stage / (previous_phase + ".summary.json"), 10000))
        if previous.get("gate_passed") is not True:
            raise SystemExit("The preceding protocol gate failed; stop.")
    private_write(directory / (phase + ".attempt"), b"reviewed AS1-B1 one-shot")
    request = ReadRequest(request_id=uuid.uuid4().hex, operation="request_access" if phase == "permission" else "read_selected", app=None if phase == "permission" else "messages", expires_at=time.time() + 15)
    started = time.monotonic()
    async def run():
        result = {"scope": "as1-b1", "phase": phase, "request_id": request.request_id,
                  "operation": request.operation, "automatic_retry": False, "model_calls": 0,
                  "screenshots": False, "private_text_in_tool_output": False}
        try:
            reply = await run_read_probe(stage / "build-02", "644c77ce9d8c0f0b14cfb310d6895b866a21578c583aa24428cbf15da8d88034", directory, request, approved_scope="as1-b1")
            passed = (reply.status in {"ok", "permission_required"}) if phase == "permission" else (reply.status == "ok" and reply.candidate is not None) if phase == "read" else (reply.status == "permission_required" and reply.candidate is None and reply.target_pid is None)
            result.update(status=reply.status, trusted=reply.trusted, helper_identity=reply.helper_identity,
                          helper_pid=reply.helper_pid, target_pid=reply.target_pid, gate_passed=passed)
            result.update(candidate_qualified=False, candidate_areas=0, candidate_text_collected=False)
            if reply.candidate is not None:
                items = reply.candidate.items
                result.update(candidate_areas=len(items), candidate_text_collected=any(item.value for item in items),
                              candidate_value_bytes=sum(len(item.value.encode()) for item in items),
                              candidate_identifiers_present=sum(bool(item.identifier) for item in items),
                              settable_excluded=reply.candidate.settable_excluded)
        except BaseException as error:
            result.update(status="failed", failure_type=type(error).__name__, gate_passed=False)
        result["elapsed_seconds"] = round(time.monotonic() - started, 3)
        private_write(stage / (phase + ".summary.json"), json.dumps(result, indent=2).encode())
        print(json.dumps(result, indent=2))
        if result["gate_passed"] is not True:
            raise SystemExit(1)
    asyncio.run(run())
