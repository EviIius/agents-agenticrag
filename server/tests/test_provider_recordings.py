"""Check the real wire fixtures adapters will consume, including observed routing failures."""

import json
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

import pytest

FIXTURES = Path(__file__).parent / "fixtures/providers"
RECORDINGS = sorted(FIXTURES.glob("*.request.json"))


def metadata(name: str) -> dict[str, Any]:
    return dict(json.loads((FIXTURES / f"{name}.request.json").read_text()))


def packets(name: str) -> list[dict[str, Any]]:
    meta = metadata(name)
    raw = (FIXTURES / meta["raw"]).read_text()
    if meta["content_type"].startswith("text/event-stream"):
        return [
            dict(json.loads(line.removeprefix("data: ")))
            for line in raw.splitlines()
            if line.startswith("data: ") and line != "data: [DONE]"
        ]
    return [dict(json.loads(line)) for line in raw.splitlines() if line]


@pytest.mark.parametrize("path", RECORDINGS, ids=lambda path: path.stem)
def test_capture_provenance_and_integrity(path: Path) -> None:
    meta = json.loads(path.read_text())
    assert datetime.fromisoformat(meta["recorded_at"]).tzinfo is not None
    assert meta["request"]["url"].startswith(("http://127.0.0.1:11434/", "http://127.0.0.1:1234/"))
    assert sha256((FIXTURES / meta["raw"]).read_bytes()).hexdigest() == meta["sha256"]
    assert meta["status"] in (200, 400, 404)


@pytest.mark.parametrize("provider", ["ollama", "lmstudio"])
def test_recorded_text_reasoning_and_length(provider: str) -> None:
    plain = packets(f"{provider}-plain")
    reasoning = packets(f"{provider}-reasoning")
    length = packets(f"{provider}-length")
    if provider == "ollama":
        assert any(chunk.get("message", {}).get("content") for chunk in plain)
        assert any(chunk.get("message", {}).get("thinking") for chunk in reasoning)
        assert length[-1]["done_reason"] == "length"
        assert length[-1]["eval_count"] == 20
    else:
        assert any(choice["delta"].get("content") for c in plain for choice in c["choices"])
        assert any(choice["delta"].get("reasoning") for c in reasoning for choice in c["choices"])
        assert any(choice["finish_reason"] == "length" for c in length for choice in c["choices"])
        assert any(c.get("usage", {}).get("completion_tokens") == 20 for c in length)


def test_recorded_gemma_image_input_completed() -> None:
    assert metadata("ollama-vision")["request"]["body"]["messages"][0]["images"]
    assert packets("ollama-vision")[-1]["done"]
    assert packets("ollama-vision")[-1]["done_reason"] == "stop"


def test_runtime_unknown_model_discrepancy_is_preserved() -> None:
    assert metadata("ollama-unknown")["status"] == 404
    loaded = metadata("lmstudio-unknown-loaded")
    assert loaded["status"] == 200
    returned = {packet["model"] for packet in packets("lmstudio-unknown-loaded")}
    assert loaded["request"]["body"]["model"] not in returned
    assert metadata("lmstudio-unknown")["status"] == 400


def test_lmstudio_loaded_context_and_unload_contract() -> None:
    for label in ("plain", "reasoning", "length"):
        loaded = json.loads((FIXTURES / f"lmstudio-models-{label}.json").read_text())
        request_model = metadata(f"lmstudio-load-{label}")["request"]["body"]["model"]
        model = next(model for model in loaded["models"] if model["key"] == request_model)
        assert any(i["config"]["context_length"] == 16384 for i in model["loaded_instances"])
        unload = metadata(f"lmstudio-unload-{label}-0")
        assert unload["request"]["body"]["instance_id"] in {
            instance["id"] for instance in model["loaded_instances"]
        }
        assert unload["status"] == 200
