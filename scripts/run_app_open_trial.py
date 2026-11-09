"""Frozen two-task local-model proof. Explicit trial only; no live app registration."""

import argparse
import asyncio
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Literal

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
from app.assistant.app_open import (
    NativeAppOpener,
    OpenDecision,
    perform_open,
    prompt_hash,
    propose_open,
)
from app.assistant.mac_probe import private_read, private_write
from app.capacity import Capacity
from app.providers.base import ChatRequest, validate_reasoning
from app.providers.ollama import Ollama
from app.schemas import ModelInfo

import httpx

BASE_STAGE = Path.home() / ".local/share/workbench/qa/assistant-app-open-20261108"
STAGE = BASE_STAGE / "v2"
CASES: tuple[tuple[Literal["notes", "messages"], str], ...] = (
    ("notes", "Bring Notes to the front."),
    ("messages", "Open Messages."),
)
PROFILE = "qwen3.8:27b-atelier-eval-32k"
CONNECTION = "3fd2cccc30b34c82b93e528148a8aba6"


def resources() -> dict[str, float]:
    pressure = subprocess.check_output(["/usr/bin/memory_pressure", "-Q"], timeout=3).decode()
    swap = subprocess.check_output(["/usr/sbin/sysctl", "vm.swapusage"], timeout=3).decode()
    free = re.search(r"System-wide memory free percentage: (\d+)%", pressure)
    used = re.search(r"used = ([\d.]+)M", swap)
    if not free or not used:
        raise RuntimeError("Resource snapshot unavailable.")
    return {"memory_free_percent": float(free[1]), "swap_used_mib": float(used[1])}


class MeasuredCapacity(Capacity):
    wait_seconds = 0.0

    @asynccontextmanager
    async def lease(self, *, background: bool = False) -> AsyncIterator[None]:
        start = time.monotonic()
        async with super().lease(background=background):
            self.wait_seconds = time.monotonic() - start
            yield


async def trial(index: int, manifest: dict[str, Any]) -> dict[str, Any]:
    directory = STAGE / "native"
    directory.mkdir(mode=0o700, exist_ok=True)
    app, task = CASES[index]
    result: dict[str, Any] = {
        "task": task,
        "expected_app": app,
        "model_requests": 0,
        "automatic_retry": False,
        "private_text": False,
        "screenshots": False,
        "input_or_send": False,
        "gate_passed": False,
        "prompt_sha256": prompt_hash(),
    }
    start = time.monotonic()
    adapter: Ollama | None = None
    try:
        # A phase marker prevents retries even if preparation or request dispatch fails.
        private_write(directory / (app + ".attempt"), b"one-shot; no retries")
        result["resources_before"] = resources()
        if result["resources_before"]["memory_free_percent"] < 15:
            raise RuntimeError("Resource gate failed before dispatch.")
        async with asyncio.timeout(180):
            async with httpx.AsyncClient(
                base_url="http://127.0.0.1:8787", trust_env=False
            ) as client:
                response = await client.get("/api/models", params={"refresh": True})
                response.raise_for_status()
                model = next(
                    ModelInfo.model_validate(m)
                    for m in response.json()
                    if m["model_id"] == PROFILE and m["connection_id"] == CONNECTION
                )
                response = await client.get("/api/connections")
                response.raise_for_status()
                connection = next(c for c in response.json() if c["id"] == CONNECTION)
            if not connection["enabled"] or connection["base_url"] != "http://127.0.0.1:11434":
                raise RuntimeError("The reviewed local connection changed.")
            if not model.chat_capable or model.context_length != 32768:
                raise RuntimeError("The reviewed daily profile changed.")
            params = dict(model.params_defaults)
            reasoning = params.pop("reasoning", None)
            validate_reasoning(model, reasoning)
            settings = ChatRequest(PROFILE, [], params, model.context_length, reasoning)

            async def record_request(request: httpx.Request) -> None:
                if request.url.path != "/api/chat" or result["model_requests"] != 0:
                    raise RuntimeError("Unexpected additional runtime request.")
                private_write(directory / (app + ".http-request.json"), request.content)
                result["model_requests"] = 1
                result["actual_payload_sha256"] = hashlib.sha256(request.content).hexdigest()

            adapter = Ollama(
                CONNECTION,
                connection["base_url"],
                connection["keep_alive"],
                client=httpx.AsyncClient(
                    trust_env=False,
                    timeout=httpx.Timeout(180, connect=5),
                    event_hooks={"request": [record_request]},
                ),
            )
            adapter.models = {model.model_id: model}
            capacity = MeasuredCapacity(Path.home() / ".local/share/workbench/data/native.lock")
            adapter.capacity = capacity
            result.update(
                model=PROFILE,
                context_length=model.context_length,
                saved_params=params,
                reasoning=reasoning,
                keep_alive=connection["keep_alive"],
                initially_loaded=model.loaded,
            )
            requested = time.monotonic()
            if index == 0:
                # Replay exactly the retained correct Notes intent. No second Notes
                # inference and no resetting/reusing the original failed ledger.
                retained = private_read(BASE_STAGE / "notes.summary.json", 6000)
                if hashlib.sha256(retained).hexdigest() != manifest["retained_notes_sha256"]:
                    raise RuntimeError("The retained model decision changed.")
                original = json.loads(retained)
                if original["model_requests"] != 1 or original["prompt_sha256"] != prompt_hash():
                    raise RuntimeError("The retained model decision is not from this trial.")
                decision = OpenDecision.model_validate(original["decision"])
                result["replayed_model_decision"] = True
                result["reserved_requests"] = 0
            else:
                # Count durably before the sole new inference. No warm-up or retries.
                private_write(directory / (app + ".request"), json.dumps(result).encode())
                result["reserved_requests"] = 1
                decision = await propose_open(adapter, settings, task)
            result.update(
                model_wall_seconds=round(time.monotonic() - requested, 3),
                queue_seconds=round(capacity.wait_seconds, 3),
                decision=decision.model_dump(),
            )
            if decision.action != "open_app" or decision.app != app:
                raise RuntimeError("The proposal failed the declared task.")
            receipt = await perform_open(
                NativeAppOpener(STAGE / "OpenApp", manifest["executable_sha256"]), decision
            )
            result["verified_foreground"] = receipt.model_dump()
            result["resources_after"] = resources()
            if result["resources_after"]["memory_free_percent"] < 15 or (
                result["resources_after"]["swap_used_mib"]
                - result["resources_before"]["swap_used_mib"]
                > 1024
            ):
                raise RuntimeError("The resource gate failed.")
            result["gate_passed"] = True
    except BaseException as error:
        # No model/system text is printed as an exception; only its type.
        result["failure_type"] = type(error).__name__
    finally:
        if adapter is not None:
            await adapter.close()
        if "resources_after" not in result:
            try:
                result["resources_after"] = resources()
            except Exception:
                result["resources_after_unavailable"] = True
        result["wall_seconds"] = round(time.monotonic() - start, 3)
        private_write(STAGE / (app + ".summary.json"), json.dumps(result, indent=2).encode())
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("app", choices=[case[0] for case in CASES])
    parser.add_argument("--manifest-sha256", required=True)
    args = parser.parse_args()
    frozen_path = ROOT / "artifacts/assistant-app-open-20261108/source-manifest-v2.json"
    if hashlib.sha256(frozen_path.read_bytes()).hexdigest() != args.manifest_sha256:
        raise SystemExit("Source manifest changed; stop.")
    frozen = json.loads(frozen_path.read_text())
    for path, digest in frozen["files"].items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != digest:
            raise SystemExit("Trial source changed; stop.")
    manifest = json.loads(private_read(STAGE / "build.json", 2000))
    if manifest != frozen["build"] or frozen["prompt_sha256"] != prompt_hash():
        raise SystemExit("The reviewed opener build/prompt changed; stop.")
    directory = STAGE / "native"
    directory.mkdir(mode=0o700, exist_ok=True)
    lock = os.open(directory / "operator.lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    with os.fdopen(lock, "r+") as owned:
        fcntl.flock(owned, fcntl.LOCK_EX | fcntl.LOCK_NB)
        index = next(i for i, case in enumerate(CASES) if case[0] == args.app)
        ledger = directory / "ledger.json"
        records = json.loads(private_read(ledger, 2000)) if ledger.exists() else []
        if len(records) != index:
            raise SystemExit("Wrong phase or the two-task budget was consumed.")
        if index:
            previous = json.loads(private_read(STAGE / "notes.summary.json", 6000))
            if previous.get("gate_passed") is not True:
                raise SystemExit("The first task failed; no second task.")
        records.append({"app": args.app, "request_id": uuid.uuid4().hex})
        temporary = directory / (records[-1]["request_id"] + ".ledger")
        private_write(temporary, json.dumps(records).encode())
        os.replace(temporary, ledger)
        result = asyncio.run(trial(index, manifest))
        print(json.dumps(result, indent=2))
        if result["gate_passed"] is not True:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
