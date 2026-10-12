"""Read-only preservation, actual call counts and live health closeout."""

import asyncio
import hashlib
import json
import subprocess
from pathlib import Path

import httpx

import native

ROOT, OUT = native.ROOT, native.OUT


async def main():
    native.frozen()
    manifest = json.loads((OUT / "manifest.json").read_text())
    tree = subprocess.check_output(
        ["git", "ls-tree", "-r", "-z", "6f3c9bb1", "--", "artifacts", "server/evals/web"],
        cwd=ROOT,
    )
    old_count = 0
    for row in tree.split(b"\0"):
        if not row:
            continue
        head, name = row.split(b"\t", 1)
        data = (ROOT / name.decode()).read_bytes()
        assert (
            hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
            == head.split()[2].decode()
        ), name
        old_count += 1
    old_manifest = json.loads(
        (ROOT / "artifacts/images-i1/search-scoped-input/manifest.json").read_text()
    )
    for name, expected in old_manifest["files"].items():
        assert native.digest(ROOT / name) == expected, name
    installed = Path.home() / ".local/share/workbench/app/server"
    for name, expected in manifest["installed_search_and_context_source_matches"].items():
        assert native.digest(installed / name) == expected, name
    archived = json.loads((OUT / "regenerated-test-evidence.json").read_text())
    for name, row in archived["files"].items():
        assert native.digest(ROOT / row["fresh"]) == row["fresh_sha256"]
        if "restored_sha256" in row:
            assert native.digest(ROOT / name) == row["restored_sha256"]
    state = json.loads((OUT / "ordered-results.json").read_text())
    counts = {"planners": 0, "answers": 0, "empty_message_warm_loads": 0}
    for run in state["runs"]:
        folder = OUT / run["label"]
        assert native.digest(ROOT / run["report"]) == run["report_sha256"]
        for line in (folder / "wire.jsonl").read_text().splitlines():
            record = json.loads(line)
            assert hashlib.sha256(record["body"].encode()).hexdigest() == record["sha256"]
            body = json.loads(record["body"])
            key = (
                "empty_message_warm_loads"
                if not body.get("messages")
                else "planners"
                if body.get("format") is not None
                else "answers"
            )
            counts[key] += 1
    assert counts == {"planners": 2, "answers": 2, "empty_message_warm_loads": 2}
    assert len(state["runs"]) == 2 and len(state["unexecuted"]) == 4 and state["stop"]
    async with httpx.AsyncClient(timeout=15, trust_env=False) as client:
        results = {}
        for name, url in {
            "local_health": "http://127.0.0.1:8787/api/health",
            "verified_https_health": "https://jakes-mac-mini.tailc4d343.ts.net/api/health",
            "ollama_version": "http://127.0.0.1:11434/api/version",
        }.items():
            response = await client.get(url)
            response.raise_for_status()
            results[name] = {"status": response.status_code, "body": response.json()}
    assert results["ollama_version"]["body"]["version"] == "0.35.0"
    product = subprocess.check_output(
        [
            "git",
            "diff",
            "--name-only",
            "6f3c9bb1",
            "--",
            "server",
            "web",
            "transcribe",
            "scripts",
            "deploy",
            "image_worker",
        ],
        cwd=ROOT,
        text=True,
    ).splitlines()
    assert not product, product
    privacy = json.loads((OUT / "privacy-final.json").read_text())
    assert not privacy["failures"]
    native.write(
        "closeout-integrity.json",
        {
            "frozen_at": "b6dc54b8",
            "current_frozen_files": len(manifest["files"]),
            "prior_frozen_files": len(old_manifest["files"]),
            "prior_committed_evidence_and_eval_files": old_count,
            "installed_search_and_context_files_unchanged": len(
                manifest["installed_search_and_context_source_matches"]
            ),
            "fresh_test_outputs_verified": len(archived["files"]),
            "native_calls": counts,
            "unexecuted_children": state["unexecuted"],
            "stop": state["stop"],
            "product_changes": product,
            "privacy": privacy,
            **results,
            "deployment_or_restart": False,
            "research_image_workflow_calls": 0,
        },
    )
    print(
        json.dumps({"preserved_old_files": old_count, "calls": counts, "health": results}, indent=2)
    )


if __name__ == "__main__":
    asyncio.run(main())
