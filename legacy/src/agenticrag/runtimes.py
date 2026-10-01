from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Literal
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .config import (
    ProviderConfig,
    ProviderRole,
    validate_local_base_url,
    validate_openai_base_url,
)
from .errors import ConfigurationError, ProviderError


StructuredMode = Literal["json_schema", "json_object", "prompt"]


RUNTIME_PROFILES: tuple[dict[str, Any], ...] = (
    {
        "id": "lm-studio",
        "name": "LM Studio",
        "description": "Desktop model management with OpenAI-compatible chat and embeddings.",
        "chat_base_url": "http://127.0.0.1:1234/v1",
        "embedding_base_url": "http://127.0.0.1:1234/v1",
        "structured_output_mode": "json_schema",
        "launch": "lms server start",
        "docs": "https://lmstudio.ai/docs/developer/core/server",
    },
    {
        "id": "ollama",
        "name": "Ollama",
        "description": "Simple local model runner with OpenAI-compatible chat, tools, and embeddings.",
        "chat_base_url": "http://127.0.0.1:11434/v1",
        "embedding_base_url": "http://127.0.0.1:11434/v1",
        "structured_output_mode": "json_object",
        "launch": "ollama serve",
        "docs": "https://docs.ollama.com/api/openai-compatibility",
    },
    {
        "id": "llama-cpp",
        "name": "llama.cpp",
        "description": "Portable GGUF inference for CPU and GPU deployments.",
        "chat_base_url": "http://127.0.0.1:8080/v1",
        "embedding_base_url": "http://127.0.0.1:8081/v1",
        "structured_output_mode": "json_schema",
        "launch": "llama-server -m model.gguf --host 127.0.0.1 --port 8080 --jinja",
        "docs": "https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md",
    },
    {
        "id": "vllm",
        "name": "vLLM",
        "description": "High-throughput OpenAI-compatible serving for GPU-backed models.",
        "chat_base_url": "http://127.0.0.1:8000/v1",
        "embedding_base_url": "http://127.0.0.1:8001/v1",
        "structured_output_mode": "json_schema",
        "launch": "vllm serve <model> --host 127.0.0.1 --port 8000",
        "docs": "https://docs.vllm.ai/en/latest/serving/online_serving/openai_compatible_server/",
    },
    {
        "id": "openai-compatible",
        "name": "OpenAI-compatible",
        "description": "A local server exposing /v1/models, chat/completions, and embeddings.",
        "chat_base_url": "http://127.0.0.1:8080/v1",
        "embedding_base_url": "http://127.0.0.1:8081/v1",
        "structured_output_mode": "prompt",
        "launch": "Start your runtime, then enter its loopback /v1 endpoint.",
        "docs": "docs/deployment.md",
    },
    {
        "id": "openai",
        "name": "OpenAI (hosted, opt-in)",
        "description": "Hosted OpenAI models and Responses API tools. Billable; prompts leave the local boundary.",
        "provider_kind": "openai",
        "chat_base_url": "https://api.openai.com/v1",
        "embedding_base_url": "https://api.openai.com/v1",
        "structured_output_mode": "json_schema",
        "launch": "Enter a key for this process only, or set AGENTICRAG_OPENAI_API_KEY.",
        "docs": "https://developers.openai.com/api/docs/models",
    },
)


@dataclass(frozen=True)
class RuntimeSelection:
    runtime: str
    role: ProviderRole
    base_url: str
    model: str
    structured_output_mode: StructuredMode = "json_schema"
    api_key: str | None = None
    timeout_seconds: float = 90.0
    provider_kind: Literal["local", "openai"] = "local"

    def __post_init__(self) -> None:
        profiles = {item["id"]: item for item in RUNTIME_PROFILES}
        if self.runtime not in profiles:
            raise ConfigurationError(f"Unknown runtime profile: {self.runtime}")
        expected_kind = profiles[self.runtime].get("provider_kind", "local")
        if self.provider_kind != expected_kind:
            raise ConfigurationError("Runtime profile and provider kind do not match")
        normalized_url = (
            validate_openai_base_url(self.base_url)
            if self.provider_kind == "openai"
            else validate_local_base_url(self.base_url)
        )
        object.__setattr__(self, "base_url", normalized_url)
        model = self.model.strip()
        if not model or len(model) > 512 or any(ord(char) < 32 for char in model):
            raise ConfigurationError("Model identifier must contain 1 to 512 visible characters")
        object.__setattr__(self, "model", model)
        if self.structured_output_mode not in {"json_schema", "json_object", "prompt"}:
            raise ConfigurationError("Unsupported structured output mode")
        if not 0 < self.timeout_seconds <= 600:
            raise ConfigurationError("Provider timeout must be between 0 and 600 seconds")
        if self.provider_kind == "openai" and not self.api_key:
            raise ConfigurationError("An OpenAI API key is required for the hosted profile")

    def provider_config(self) -> ProviderConfig:
        return ProviderConfig(
            kind=self.provider_kind,
            role=self.role,
            base_url=self.base_url,
            model=self.model,
            api_key=self.api_key,
            timeout_seconds=self.timeout_seconds,
            structured_output_mode=self.structured_output_mode,
            runtime=self.runtime,
        )

    def public_dict(self) -> dict[str, object]:
        return {
            "runtime": self.runtime,
            "provider_kind": self.provider_kind,
            "role": self.role.value,
            "base_url": self.base_url,
            "model": self.model,
            "structured_output_mode": self.structured_output_mode,
            "credential_configured": bool(self.api_key),
            "timeout_seconds": self.timeout_seconds,
        }


def ollama_supports_vision(config: ProviderConfig) -> bool:
    """Ask the selected local Ollama runtime instead of guessing from a model name."""
    if config.runtime != "ollama":
        return False
    request = Request(
        f"{config.base_url.removesuffix('/v1')}/api/show",
        data=json.dumps({"model": config.model}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=10) as response:  # noqa: S310 - validated loopback runtime
            details = json.load(response)
    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
        raise ProviderError("Could not verify the selected model's image capability") from exc
    capabilities = details.get("capabilities") if isinstance(details, dict) else None
    return isinstance(capabilities, list) and "vision" in capabilities


def discover_models(config: ProviderConfig) -> dict[str, object]:
    """Probe the already validated OpenAI-compatible models endpoint."""

    started = time.perf_counter()
    headers = {"Accept": "application/json", "User-Agent": "agenticrag/0.3"}
    if config.api_key:
        headers["Authorization"] = f"Bearer {config.api_key}"
    request = Request(f"{config.base_url}/models", headers=headers, method="GET")
    try:
        with urlopen(request, timeout=min(config.timeout_seconds, 15.0)) as response:  # noqa: S310
            raw = response.read(2 * 1024 * 1024 + 1)
    except HTTPError as exc:
        raise ProviderError(f"Model discovery returned HTTP {exc.code}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise ProviderError(f"Could not reach the configured runtime: {exc}") from exc
    if len(raw) > 2 * 1024 * 1024:
        raise ProviderError("Model discovery response exceeded 2 MiB")
    try:
        payload = json.loads(raw.decode("utf-8"))
        rows = payload["data"]
        models = sorted(
            {str(row["id"]) for row in rows if isinstance(row, dict) and row.get("id")}
        )
    except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise ProviderError("Model discovery returned an invalid OpenAI-compatible response") from exc
    return {
        "reachable": True,
        "latency_ms": max(0, round((time.perf_counter() - started) * 1_000)),
        "models": models,
        "configured_model_available": config.model in models,
    }
