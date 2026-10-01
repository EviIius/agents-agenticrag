"""Verify product settings and chat actions against real Ollama, with isolated data."""

import asyncio
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.config import Settings  # noqa: E402
from app.main import create_app  # noqa: E402


async def main() -> None:
    captures: list[dict[str, Any]] = []
    checks: list[str] = []
    with TemporaryDirectory(prefix="workbench-real-controls-") as directory:
        app = create_app(Settings(data_dir=Path(directory), dev=True))
        async with (
            app.router.lifespan_context(app),
            httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://localhost"
            ) as client,
        ):
            connection = (await client.post("/api/connections", json={})).json()
            await client.patch("/api/settings", json={"auto_title": False})
            model_id = "qwen3:30b-a3b-instruct-2507-q4_K_M"
            adapter = await app.state.registry.adapter(connection["id"])

            async def capture(request: httpx.Request) -> None:
                if request.url.path == "/api/chat":
                    body = json.loads(request.content)
                    if body.get("messages"):
                        captures.append(body)

            adapter.client.event_hooks["request"].append(capture)
            chat = (
                await client.post(
                    "/api/chats",
                    json={
                        "connection_id": connection["id"],
                        "model_id": model_id,
                    },
                )
            ).json()
            chat_url = "/api/chats/" + chat["id"]
            leaf = None

            async def answer(label: str) -> None:
                nonlocal leaf
                response = await client.post(
                    chat_url + "/messages",
                    json={
                        "content": "Reply with just OK. " + label,
                        "parent_id": leaf,
                    },
                )
                assert response.status_code == 202, response.text
                run = app.state.runs.runs[response.json()["run_id"]]
                await run.task
                assert run.message.status == "complete", run.message.error
                assert run.message.content
                leaf = run.message.id

            await answer("Runtime defaults check")
            assert set(captures[-1].get("options", {})) == {"num_ctx"}
            checks.append("Untouched sampling parameters are omitted from real Ollama requests")
            params = {"temperature": 0.55, "top_p": 0.85, "top_k": 37, "max_tokens": 64, "seed": 42}
            response = await client.patch(
                chat_url,
                json={
                    "params": params,
                    "system_prompt": "Be concise. Live parameter verification.",
                },
            )
            assert response.status_code == 200, response.text
            pref = {"connection_id": connection["id"], "model_id": model_id}
            assert (
                await client.put("/api/models/prefs", json={**pref, "context_length": 4096})
            ).status_code == 200
            await answer("Custom parameter check")
            assert captures[-1]["options"] == {
                "temperature": 0.55,
                "top_p": 0.85,
                "top_k": 37,
                "num_predict": 64,
                "seed": 42,
                "num_ctx": 4096,
            }
            assert captures[-1]["messages"][0]["content"].startswith(
                "Be concise. Live parameter verification."
            )
            checks.append(
                "Temperature, top P/K, output cap, seed, context and system prompt "
                "reach real Ollama"
            )
            await client.put(
                "/api/models/prefs",
                json={**pref, "params": {"temperature": 0.25, "max_tokens": 64}},
            )
            await client.patch(chat_url, json={"params": {}})
            await answer("Saved model defaults check")
            assert captures[-1]["options"] == {
                "temperature": 0.25,
                "num_predict": 64,
                "num_ctx": 4096,
            }
            checks.append("Reset chat parameters inherit saved model defaults")
            await client.put("/api/models/prefs", json={**pref, "params": {}})
            await answer("Restored runtime defaults check")
            assert captures[-1]["options"] == {"num_ctx": 4096}
            checks.append("Clearing model defaults restores runtime sampling defaults")
            await client.patch(chat_url, json={"title": "Verified real chat", "pinned": True})
            detail = (await client.get(chat_url)).json()
            assert detail["chat"]["title"] == "Verified real chat" and detail["chat"]["pinned"]
            await client.patch(chat_url, json={"pinned": False})
            assert not (await client.get(chat_url)).json()["chat"]["pinned"]
            checks.append("Rename, pin and unpin persist in the product database")
            for format in ("json", "md"):
                response = await client.get(chat_url + "/export", params={"format": format})
                assert (
                    response.status_code == 200
                    and "attachment" in response.headers["content-disposition"]
                )
                assert (
                    "Verified real chat" in response.text
                    and "Runtime defaults check" in response.text
                )
            checks.append("Markdown and JSON exports contain the real conversation")
            assert (await client.delete(chat_url)).status_code == 204
            assert (await client.get(chat_url)).status_code == 404
            assert not (await client.get("/api/chats?q=Verified")).json()["items"]
            checks.append("Delete removes the chat and its history search entries")
            await adapter.load(model_id, captures[0]["options"]["num_ctx"])
            report = {
                "model": model_id,
                "real_runtime": True,
                "isolated_data": True,
                "checks": checks,
                "requests": captures,
            }
            Path("../artifacts/phase-2/live-controls.json").write_text(json.dumps(report, indent=2))
            print(json.dumps({"passed": len(checks), "checks": checks}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
