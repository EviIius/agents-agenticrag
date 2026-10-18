"""Bounded P0 trial on original H0 tasks; one invocation and review per task."""

from __future__ import annotations

import fcntl
import hashlib
import http.client
import json
import re
import socket
import subprocess
import sys
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "hermes_h0"))

from protocol import (  # noqa: E402
    TOOL_NAMES,
    FixtureTools,
    GateFailure,
    Ledger,
    TaskGate,
    terminate,
)
from runtime_probe_result_v2 import (  # noqa: E402
    CONFIG,
    EVIDENCE,
    QA,
    ROOT,
    SYSTEM,
    launch,
    read_events,
    validate_wire,
)

PROFILE = "qwen3.8:27b-hermes-h0-64k"
BASE = "qwen3.8:27b-q4_K_M"
OUT = ROOT / "artifacts/pydantic/p0-native"
PRIVATE = QA / "native"
LOCK = Path.home() / ".local/share/workbench/data/native.lock"
CASES = json.loads((ROOT / "experiments/hermes_h0/cases.json").read_text())
SCHEDULE = []
for index, case in enumerate(CASES["cases"]):
    arms = ["pydantic", "direct"] if index % 2 == 0 else ["direct", "pydantic"]
    for arm in arms:
        SCHEDULE.append({"id": arm + "-" + case["id"], "case": case["id"], "arm": arm})
for index in range(3):
    arms = ["direct", "pydantic"] if index % 2 == 0 else ["pydantic", "direct"]
    for arm in arms:
        SCHEDULE.append({"id": f"warm{index + 1}-{arm}-H01", "case": "H01", "arm": arm})


def write(path, value):
    path.write_text(json.dumps(value, indent=2, default=str) + "\n")


def request(path, payload=None, *, app=False):
    port = 8787 if app else 11434
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}" + path, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.load(response)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare():
    review = json.loads((EVIDENCE / "offline-summary.json").read_text())
    assert review["passed"], "Scripted real-framework gates have not passed"
    frozen = json.loads((EVIDENCE / "frozen-candidate.json").read_text())
    assert all(sha(ROOT / p) == h for p, h in frozen["sources"].items())
    old = Path.home() / ".local/share/workbench/qa/hermes-h0-20261017/native-2/ledger.json"
    old_state = json.loads(old.read_text())
    assert old_state["calls"] == 4 and old_state["stopped"]
    resident = request("/api/ps")["models"]
    assert all(m["name"] == PROFILE for m in resident), "Other model resident; no automatic eject"
    original = json.loads((ROOT / "artifacts/hermes/h0-native-2/profile.json").read_text())
    show = request("/api/show", {"model": PROFILE})
    tag = next(m for m in request("/api/tags")["models"] if m["name"] == PROFILE)
    assert tag["digest"] == original["tag"]["digest"]
    for key in ["template", "system", "parameters", "capabilities", "model_info"]:
        assert show.get(key) == original["show"].get(key), ("Existing profile changed", key)
    assert {"completion", "tools"} <= set(show["capabilities"])
    assert re.search(r"num_ctx\s+65536", show["parameters"])
    OUT.mkdir(parents=True, exist_ok=False)
    PRIVATE.mkdir(mode=0o700, exist_ok=False)
    write(
        OUT / "before.json",
        {
            "resident": resident,
            "version": request("/api/version"),
            "health": request("/api/health", app=True),
        },
    )
    write(
        OUT / "profile.json",
        {"show": show, "tag": tag, "created": False, "new_weights": False, "inference_calls": 0},
    )
    write(
        OUT / "frozen-native.json",
        {
            "sources": frozen["sources"],
            "offline_manifest_sha256": sha(EVIDENCE / "frozen-candidate.json"),
            "offline_summary_sha256": sha(EVIDENCE / "offline-summary.json"),
            "model": PROFILE,
            "context": 65536,
            "schedule": SCHEDULE,
            "system": SYSTEM,
            "config": CONFIG,
            "resource_guards": {
                "swap_growth_mib": 512,
                "total_reported_model_bytes": 48 * 1024**3,
                "task_seconds": 180,
                "health_timeout_seconds": 2,
            },
            "criteria": ("Candidate first failure stops; reference quality failures are retained"),
            "previous_stopped_ledger": {"sha256": sha(old), "state": old_state},
            "new_calls_max": 36,
            "aggregate_ceiling": 42,
        },
    )
    state = {**old_state, "stopped": None}
    write(PRIVATE / "ledger.json", state)
    write(
        PRIVATE / "continuation.json",
        {
            "authorization": "New PydanticAI trial, not a Hermes continuation",
            "previous_ledger_sha256": sha(old),
            "previous_calls": 4,
            "ceiling": 42,
            "frozen_native_sha256": sha(OUT / "frozen-native.json"),
        },
    )
    print(json.dumps({"prepared": True, "profile": PROFILE, "previous_calls": 4}), flush=True)


class Backend:
    def __init__(self, trial, task, gate):
        self.trial, self.task, self.gate = trial, task, gate
        self.records = []
        self.stop = threading.Event()
        self.reason = None
        self.connections = []
        self.guard_tools = FixtureTools(CASES["sources"])
        self.first_content_seconds = None
        self.started = time.monotonic()
        self.active = 0
        self.capacity_held = False

    def fail(self, reason):
        self.reason = self.reason or reason
        self.gate.ledger.stop(self.reason)
        self.stop.set()

    def abort(self):
        for conn in list(self.connections):
            try:
                if conn.sock:
                    conn.sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            conn.close()

    def handler(self):
        backend = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, *args):
                pass

            def reply(self, status, value):
                raw = json.dumps(value).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def do_GET(self):
                backend.records.append({"method": "GET", "path": self.path})
                if self.path in {"/v1/models", "/api/v1/models"}:
                    self.reply(
                        200,
                        {
                            "object": "list",
                            "data": [{"id": PROFILE, "object": "model", "context_length": 65536}],
                        },
                    )
                elif self.path == "/api/version":
                    self.reply(200, request("/api/version"))
                else:
                    backend.fail("Unexpected metadata route")
                    self.reply(400, {"error": {"message": backend.reason}})

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                record = {"method": "POST", "path": self.path, "body": body}
                record["started_seconds"] = time.monotonic() - backend.started
                record["system_chars"] = sum(
                    len(m.get("content") or "")
                    for m in body.get("messages", [])
                    if m.get("role") == "system"
                )
                record["message_json_chars"] = len(json.dumps(body.get("messages", [])))
                backend.records.append(record)
                if self.path == "/api/show" and body.get("model") == PROFILE:
                    self.reply(200, request("/api/show", body))
                    return
                try:
                    if (
                        self.path != "/v1/chat/completions"
                        or backend.stop.is_set()
                        or not backend.capacity_held
                    ):
                        raise GateFailure("Unknown, post-stop or unscheduled inference request")
                    if any(e["kind"] == "tool_rejected" for e in read_events(backend.trial)):
                        raise GateFailure("Prior tool argument rejection")
                    validate_wire(body, PROFILE)
                    names = {t["function"]["name"] for t in body.get("tools", [])}
                    expected = TOOL_NAMES if backend.task["arm"] == "pydantic" else set()
                    if names != expected or body.get("stream") is not True:
                        raise GateFailure("Unexpected tools or non-streaming request")
                    backend.gate.admit(
                        {k: v for k, v in body.items() if k != "options"},
                        PROFILE,
                        baseline=backend.task["arm"] == "direct",
                    )
                except GateFailure as exc:
                    backend.fail(str(exc))
                    record["failure"] = str(exc)
                    self.reply(400, {"error": {"message": str(exc)}})
                    return
                conn = http.client.HTTPConnection("127.0.0.1", 11434, timeout=180)
                backend.connections.append(conn)
                backend.active += 1
                index = len([r for r in backend.records if r["path"] == "/v1/chat/completions"])
                held = []
                calls = {}
                completed = False
                try:
                    conn.request(
                        "POST",
                        "/v1/chat/completions",
                        json.dumps(body),
                        {"Content-Type": "application/json"},
                    )
                    response = conn.getresponse()
                    if response.status != 200:
                        raise GateFailure(f"Ollama HTTP {response.status}")
                    self.send_response(200)
                    self.send_header("Content-Type", "text/event-stream")
                    self.send_header("Connection", "close")
                    self.end_headers()
                    self.close_connection = True
                    with (backend.trial / f"upstream-{index:02d}.sse").open("wb") as capture:
                        while not backend.stop.is_set():
                            raw = response.readline(2_000_001)
                            if not raw:
                                break
                            capture.write(raw)
                            capture.flush()
                            if len(raw) > 2_000_000:
                                raise GateFailure("Oversized stream frame")
                            if raw.startswith(b"data: ") and raw.strip() != b"data: [DONE]":
                                data = json.loads(raw[6:])
                                if data.get("usage"):
                                    record["usage"] = data["usage"]
                                for choice in data.get("choices", []):
                                    delta = choice.get("delta", {})
                                    if (
                                        delta.get("content")
                                        and backend.first_content_seconds is None
                                    ):
                                        backend.first_content_seconds = (
                                            time.monotonic() - backend.started
                                        )
                                    if delta.get("content"):
                                        record.setdefault(
                                            "first_content_seconds",
                                            time.monotonic() - backend.started,
                                        )
                                    for tool in delta.get("tool_calls", []):
                                        item = calls.setdefault(
                                            tool.get("index", 0), {"name": "", "arguments": ""}
                                        )
                                        function = tool.get("function", {})
                                        item["name"] += function.get("name") or ""
                                        item["arguments"] += function.get("arguments") or ""
                                    if calls and choice.get("finish_reason"):
                                        for call in calls.values():
                                            # Validate before the framework dispatches a tool.
                                            backend.guard_tools.call(
                                                call["name"], json.loads(call["arguments"])
                                            )
                                        for previous in held:
                                            self.wfile.write(previous)
                                        held = []
                                        calls = {}
                            if calls:
                                held.append(raw)
                            else:
                                self.wfile.write(raw)
                                self.wfile.flush()
                            if raw.strip() == b"data: [DONE]":
                                completed = True
                                break
                    if not completed or held:
                        raise GateFailure("Incomplete native stream")
                    record["completed"] = True
                    record["finished_seconds"] = time.monotonic() - backend.started
                except Exception as exc:
                    backend.fail(type(exc).__name__ + ": " + str(exc))
                    record["failure"] = backend.reason
                finally:
                    conn.close()
                    backend.active -= 1

        return Handler


def swap_mib():
    value = subprocess.check_output(["sysctl", "-n", "vm.swapusage"], text=True)
    match = re.search(r"used =\s*([0-9.]+)([MG])", value)
    if not match:
        raise GateFailure("Unrecognized swap measurement")
    return float(match[1]) * (1024 if match[2] == "G" else 1)


def next_task():
    frozen = json.loads((OUT / "frozen-native.json").read_text())
    assert all(sha(ROOT / p) == h for p, h in frozen["sources"].items())
    controller = json.loads((OUT / "controller-continuation.json").read_text())
    assert sha(Path(__file__)) == controller["controller_sha256"]
    assert sha(OUT / "frozen-native.json") == controller["original_native_manifest_sha256"]
    ledger = Ledger(PRIVATE / "ledger.json")
    state = json.loads(ledger.path.read_text())
    assert not state["stopped"], state["stopped"]
    for task in SCHEDULE:
        done = OUT / task["id"] / "result.json"
        if done.exists():
            review = OUT / task["id"] / "manual-review.json"
            assert review.exists(), "Manual review required"
            if task["arm"] == "pydantic":
                assert json.loads(review.read_text())["passed"], "Candidate failed; do not continue"
        else:
            break
    else:
        print("P0 schedule complete; stop for review.")
        return
    trial = PRIVATE / task["id"]
    trial.mkdir(mode=0o700, exist_ok=False)
    out = OUT / task["id"]
    out.mkdir(exist_ok=False)
    case = next(c for c in CASES["cases"] if c["id"] == task["case"])
    started = time.monotonic()
    wait_started = started
    with LOCK.open("a+") as lock:
        while True:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() - wait_started > 30:
                    raise GateFailure("Live runtime busy; no native request started") from None
                time.sleep(0.1)
        gate = TaskGate(ledger, "p0/" + task["id"])
        backend = Backend(trial, task, gate)
        backend.capacity_held = True
        server = ThreadingHTTPServer(("127.0.0.1", 0), backend.handler())
        server.daemon_threads = True
        threading.Thread(target=server.serve_forever, daemon=True).start()
        if task["arm"] == "pydantic":
            child = launch(trial, server.server_port, PROFILE, case["question"], SYSTEM, task["id"])
        else:
            settings = {
                "trial_dir": str(trial),
                "port": server.server_port,
                "model": PROFILE,
                "question": case["question"]
                + "\n\nFull synthetic source corpus:\n"
                + json.dumps(CASES["sources"]),
                "system_prompt": SYSTEM,
            }
            write(trial / "settings.json", settings)
            with (
                (trial / "stdout.txt").open("w") as stdout,
                (trial / "stderr.txt").open("w") as stderr,
            ):
                child = subprocess.Popen(
                    [
                        sys.executable,
                        str(Path(__file__).parent / "direct_worker.py"),
                        str(trial / "settings.json"),
                    ],
                    stdout=stdout,
                    stderr=stderr,
                    start_new_session=True,
                )
        baseline_swap = swap_mib()
        samples = []
        profile_tag = json.loads((OUT / "profile.json").read_text())["tag"]
        while child.poll() is None and not backend.stop.wait(1):
            try:
                gate.check()
                used = swap_mib()
                resident = request("/api/ps")["models"]
                health_started = time.monotonic()
                health = request("/api/health", app=True)
                elapsed = time.monotonic() - health_started
                sample = {
                    "seconds": time.monotonic() - started,
                    "swap_mib": used,
                    "models": resident,
                    "health": health,
                    "health_seconds": elapsed,
                }
                samples.append(sample)
                if used - baseline_swap > 512:
                    raise GateFailure("Host swap growth exceeds 512 MiB")
                if elapsed > 2 or not health.get("ok"):
                    raise GateFailure("Live application health guard failed")
                if sum(m.get("size", 0) for m in resident) > 48 * 1024**3:
                    raise GateFailure("Reported model memory exceeds 48 GiB")
                for model in resident:
                    if model.get("name") != PROFILE or model.get("digest") != profile_tag["digest"]:
                        raise GateFailure("Unexpected model residency")
                    if model.get("context_length") != 65536:
                        raise GateFailure("Native context differs from approved 65536")
            except Exception as exc:
                backend.fail(type(exc).__name__ + ": " + str(exc))
                break
        if child.poll() is None:
            terminate(child)
        backend.abort()
        until = time.monotonic() + 3
        while backend.active and time.monotonic() < until:
            time.sleep(0.05)
        if backend.active:
            backend.fail("Upstream request did not close before releasing capacity")
        server.shutdown()
        server.server_close()
        backend.capacity_held = False
    result_path = trial / "worker-result.json"
    result = json.loads(result_path.read_text()) if result_path.exists() else {}
    passed = (
        child.returncode == 0 and not backend.stop.is_set() and bool(result.get("final_response"))
    )
    if not passed:
        backend.fail(backend.reason or "Worker failed or returned no final answer")
    summary = {
        "task": task,
        "protocol_resource_pass": passed,
        "awaiting_manual_claim_review": passed,
        "returncode": child.returncode,
        "reason": backend.reason,
        "answer": result.get("final_response"),
        "duration_seconds": time.monotonic() - started,
        "first_content_seconds": backend.first_content_seconds,
        "last_request_first_content_seconds": next(
            (
                r.get("first_content_seconds")
                for r in reversed(backend.records)
                if r["method"] == "POST" and r["path"] == "/v1/chat/completions"
            ),
            None,
        ),
        "baseline_swap_mib": baseline_swap,
        "max_swap_growth_mib": max([0] + [s["swap_mib"] - baseline_swap for s in samples]),
        "samples": samples,
        "native_ledger": json.loads(ledger.path.read_text()),
        "capacity_released_after_response_close": backend.active == 0,
    }
    write(trial / "http-requests.json", backend.records)
    write(trial / "result.json", summary)
    for file in trial.iterdir():
        if file.is_file() and file.name not in {"settings.json"}:
            (out / file.name).write_bytes(file.read_bytes())
    write(OUT / "ledger-latest.json", json.loads(ledger.path.read_text()))
    print(
        json.dumps(
            {
                k: summary[k]
                for k in [
                    "task",
                    "protocol_resource_pass",
                    "reason",
                    "answer",
                    "duration_seconds",
                    "first_content_seconds",
                    "max_swap_growth_mib",
                ]
            }
        ),
        flush=True,
    )
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    if sys.argv[1:] == ["prepare"]:
        prepare()
    elif sys.argv[1:] == ["next"]:
        next_task()
    else:
        raise SystemExit("Use prepare or next; no unreviewed automatic retry.")
