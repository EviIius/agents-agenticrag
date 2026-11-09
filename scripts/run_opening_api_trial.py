"""Exactly two declared synthetic tasks through the isolated task/SSE API."""

import argparse
import asyncio
import hashlib
import json
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
from app.assistant.app_open import OpenDecision, PROMPT
from app.assistant.mac_probe import private_read, private_write
from app.assistant.contracts import TERMINAL
from run_app_open_trial import resources

TRIAL_HOME = Path.home() / ".local/share/workbench/qa/assistant-chat-open-20261108"


async def run() -> dict:
    source = json.loads(private_read(TRIAL_HOME / "source-settings.json", 10000))
    result = {
        "cases": [],
        "gate_passed": False,
        "extra_warmup_calls": 0,
        "private_message_content_used": False,
        "screenshots_of_desktop": False,
    }
    async with httpx.AsyncClient(
        base_url="http://127.0.0.1:18787", trust_env=False, timeout=185
    ) as client:
        private_write(
            TRIAL_HOME / "api-trial.attempt", b"two ordered tasks; stop first unexpected failure"
        )
        response = await client.post(
            "/api/chats",
            json={
                "connection_id": source["connection_id"],
                "model_id": source["model_id"],
            },
        )
        response.raise_for_status()
        chat_id = response.json()["id"]
        result["chat_id"] = chat_id
        for index, (text, expected) in enumerate(
            [
                ("Please bring Notes to the foreground.", "complete"),
                ("Open Calculator.", "needs_input"),
            ],
            1,
        ):
            before = resources()
            if before["memory_free_percent"] < 15:
                raise RuntimeError("Resource gate failed before dispatch.")
            started = time.monotonic()
            async with asyncio.timeout(180):
                body = {
                    "request_key": f"native-api-trial-{index}",
                    "text": text,
                    "mode": "open_app",
                }
                response = await client.post(f"/api/chats/{chat_id}/assistant-tasks", json=body)
                response.raise_for_status()
                task_id = response.json()["id"]
                states = []
                final = None
                async with client.stream("GET", f"/api/assistant/tasks/{task_id}/events") as stream:
                    stream.raise_for_status()
                    async for line in stream.aiter_lines():
                        if not line.startswith("data:"):
                            continue
                        task = json.loads(line.removeprefix("data:").strip())["task"]
                        states.append({"state": task["state"], "stage": task["stage"]})
                        if task["state"] in TERMINAL:
                            final = task
                            break
                if final is None:
                    raise RuntimeError("No terminal task event.")
                after = resources()
                calls = json.loads(private_read(TRIAL_HOME / "http-calls.json", 2000))
                payload = json.loads(private_read(TRIAL_HOME / f"payload-{index}.json", 20000))
                expected_options = {"num_ctx": source["context_length"]}
                for name, value in source["params_defaults"].items():
                    if (
                        name in {"temperature", "top_p", "top_k", "max_tokens", "seed"}
                        and value is not None
                    ):
                        expected_options["num_predict" if name == "max_tokens" else name] = value
                reasoning = source["params_defaults"].get("reasoning")
                expected_think = {"off": False, "on": True}.get(reasoning, reasoning)
                payload_ok = (
                    payload["options"] == expected_options
                    and payload["keep_alive"] == source["keep_alive"]
                    and payload.get("think") == expected_think
                    and payload["messages"]
                    == [{"role": "system", "content": PROMPT}, {"role": "user", "content": text}]
                    and payload["format"] == OpenDecision.model_json_schema()
                )
                replay = await client.post(f"/api/chats/{chat_id}/assistant-tasks", json=body)
                replay.raise_for_status()
                reserved = json.loads(private_read(TRIAL_HOME / "model-budget/ledger.json", 5000))
                passed = (
                    final["state"] == expected
                    and len(calls) == index
                    and len(reserved) == index
                    and payload_ok
                    and replay.json()["id"] == task_id
                    and after["memory_free_percent"] >= 15
                    and after["swap_used_mib"] - before["swap_used_mib"] <= 1024
                    and (
                        final["opened_app"]["name"] == "Notes" and final["native_dispatched"]
                        if index == 1
                        else final["opened_app"] is None and not final["native_dispatched"]
                    )
                )
                record = {
                    "task": text,
                    "state": final["state"],
                    "gate_passed": passed,
                    "wall_seconds": round(time.monotonic() - started, 3),
                    "actual_model_calls_so_far": len(calls),
                    "settings_preserved": payload_ok,
                    "verified_opened_app": final["opened_app"],
                    "native_dispatched": final["native_dispatched"],
                    "states": states,
                    "resources_before": before,
                    "resources_after": after,
                }
                result["cases"].append(record)
                private_write(
                    TRIAL_HOME / f"case-{index}.json", json.dumps(record, indent=2).encode()
                )
                if not passed:
                    return result
        result["gate_passed"] = True
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest-sha256", required=True)
    args = parser.parse_args()
    file = ROOT / "artifacts/assistant-chat-open-20261108/source-manifest.json"
    if hashlib.sha256(file.read_bytes()).hexdigest() != args.manifest_sha256:
        raise SystemExit("The declared API-trial manifest changed.")
    manifest = json.loads(file.read_text())
    for path, digest in manifest["files"].items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != digest:
            raise SystemExit("The frozen API trial source changed.")
    result = {"gate_passed": False}
    try:
        result = asyncio.run(run())
    except BaseException as error:
        result["failure_type"] = type(error).__name__
    private_write(TRIAL_HOME / "api-trial.summary.json", json.dumps(result, indent=2).encode())
    print(json.dumps(result, indent=2))
    if not result["gate_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
