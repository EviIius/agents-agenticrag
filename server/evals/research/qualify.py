"""Bind a fresh daily-model protocol probe to unchanged runtime metadata."""

import asyncio
import json
from pathlib import Path

import httpx
import probe_tools

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "artifacts/phase-8/8a/qualification"


async def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    daily = "qwen3:30b-a3b-workbench-32k"  # Explicit user daily-model selection.
    async with httpx.AsyncClient() as client:

        async def metadata():
            tags = (await client.get("http://127.0.0.1:11434/api/tags")).json()
            model = next(m for m in tags["models"] if m["name"] == daily)
            show = (
                await client.post("http://127.0.0.1:11434/api/show", json={"model": daily})
            ).json()
            version = (await client.get("http://127.0.0.1:11434/api/version")).json()["version"]
            return {
                "digest": model["digest"],
                "runtime_version": version,
                "capabilities": show["capabilities"],
                "parameters": show.get("parameters"),
                "model_info": show["model_info"],
            }

        before = await metadata()
        inventory = json.loads((ROOT / "artifacts/phase-8/gate/model-inventory.json").read_text())
        selected = next(m for m in inventory if m["model_id"] == daily)
        assert selected["context_length"] == 32768 and "tools" in before["capabilities"]
        (OUT / "model-inventory.json").write_text(json.dumps([selected], indent=2) + "\n")
        (OUT / "runtime-endpoints.json").write_text('["http://127.0.0.1:11434"]\n')
        probe_tools.OUT = OUT
        await probe_tools.main()
        after = await metadata()
    (OUT / "metadata.json").write_text(
        json.dumps({"before": before, "after": after, "unchanged": before == after}, indent=2)
        + "\n"
    )
    probe = json.loads((OUT / "tool-probe.json").read_text())["models"][0]
    assert before == after and probe["fraction"] >= 0.95
    qualification = [
        {
            "digest": before["digest"],
            "runtime_version": before["runtime_version"],
            "context_length": selected["context_length"],
            "fraction": probe["fraction"],
            "evidence": "artifacts/phase-8/8a/qualification/tool-probe.json",
        }
    ]
    (ROOT / "server/app/runs/research-qualified.json").write_text(
        json.dumps(qualification, indent=2) + "\n"
    )


if __name__ == "__main__":
    asyncio.run(main())
