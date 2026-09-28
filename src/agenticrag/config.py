from __future__ import annotations

import ipaddress
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Literal, Mapping
from urllib.parse import urlsplit

from .errors import ConfigurationError


class ProviderRole(str, Enum):
    CHAT = "chat"
    EMBEDDING = "embedding"


@dataclass(frozen=True)
class StoreConfig:
    backend: str
    sqlite_path: str
    postgres_dsn: str | None
    objects_root: str

    def public_dict(self) -> dict[str, object]:
        return {
            "backend": self.backend,
            "sqlite_path": self.sqlite_path if self.backend == "sqlite" else None,
            "postgres_dsn_configured": bool(self.postgres_dsn),
            "objects_root": self.objects_root if self.backend == "postgres" else None,
        }


@dataclass(frozen=True)
class IngestionConfig:
    max_file_bytes: int
    max_pages: int
    max_segments: int
    docling_artifacts_path: str | None


@dataclass(frozen=True)
class ProviderConfig:
    kind: str
    role: ProviderRole
    base_url: str
    model: str
    api_key: str | None
    timeout_seconds: float
    structured_output_mode: Literal["json_schema", "json_object", "prompt"] = "json_schema"
    runtime: str | None = None

    @property
    def label(self) -> str:
        parsed = urlsplit(self.base_url)
        endpoint = f"{parsed.netloc}{parsed.path}"
        return f"{self.kind}:{self.model}@{endpoint}"

    def public_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "role": self.role.value,
            "base_url": self.base_url,
            "model": self.model,
            "credential_configured": bool(self.api_key),
            "timeout_seconds": self.timeout_seconds,
            "structured_output_mode": self.structured_output_mode,
        }


def load_provider_config(
    role: ProviderRole,
    environ: Mapping[str, str] | None = None,
) -> ProviderConfig:
    env = os.environ if environ is None else environ
    prefix = role.value.upper()
    kind = env.get(f"AGENTICRAG_{prefix}_PROVIDER", "local").strip().lower()
    timeout = _positive_float(env.get("AGENTICRAG_HTTP_TIMEOUT_SECONDS", "90"))
    structured_output_mode = _structured_output_mode(
        env.get(f"AGENTICRAG_{prefix}_STRUCTURED_OUTPUT", "json_schema")
    )

    if kind == "local":
        default_port = "8080" if role is ProviderRole.CHAT else "8081"
        base_url = env.get(
            f"AGENTICRAG_LOCAL_{prefix}_BASE_URL",
            f"http://127.0.0.1:{default_port}/v1",
        ).strip()
        model = env.get(f"AGENTICRAG_LOCAL_{prefix}_MODEL", "").strip()
        if not model:
            raise ConfigurationError(
                f"AGENTICRAG_LOCAL_{prefix}_MODEL is required for the local {role.value} provider"
            )
        _require_loopback(base_url)
        return ProviderConfig(
            kind=kind,
            role=role,
            base_url=_normalize_base_url(base_url),
            model=model,
            api_key=None,
            timeout_seconds=timeout,
            structured_output_mode=structured_output_mode,
        )

    if kind == "openai":
        base_url = env.get("AGENTICRAG_OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
        model = env.get(f"AGENTICRAG_OPENAI_{prefix}_MODEL", "").strip()
        api_key = env.get("AGENTICRAG_OPENAI_API_KEY", "").strip()
        if not model:
            raise ConfigurationError(
                f"AGENTICRAG_OPENAI_{prefix}_MODEL is required when {role.value} uses OpenAI"
            )
        if not api_key:
            raise ConfigurationError(
                f"AGENTICRAG_OPENAI_API_KEY is required when {role.value} uses OpenAI"
            )
        base_url = validate_openai_base_url(base_url)
        return ProviderConfig(
            kind=kind,
            role=role,
            base_url=base_url,
            model=model,
            api_key=api_key,
            timeout_seconds=timeout,
            structured_output_mode=structured_output_mode,
        )

    raise ConfigurationError(
        f"Unsupported {role.value} provider {kind!r}; expected 'local' or 'openai'"
    )


def load_store_config(
    sqlite_path: str = ".data/corpus.db",
    environ: Mapping[str, str] | None = None,
) -> StoreConfig:
    env = os.environ if environ is None else environ
    backend = env.get("AGENTICRAG_STORE", "sqlite").strip().lower()
    if backend == "sqlite":
        return StoreConfig(backend, sqlite_path, None, "")
    if backend == "postgres":
        dsn = env.get("AGENTICRAG_POSTGRES_DSN", "").strip()
        if not dsn:
            raise ConfigurationError(
                "AGENTICRAG_POSTGRES_DSN is required when AGENTICRAG_STORE=postgres"
            )
        objects_root = env.get("AGENTICRAG_OBJECTS_PATH", ".data/objects").strip()
        if not objects_root:
            raise ConfigurationError("AGENTICRAG_OBJECTS_PATH cannot be empty")
        return StoreConfig(backend, sqlite_path, dsn, str(Path(objects_root)))
    raise ConfigurationError("AGENTICRAG_STORE must be 'sqlite' or 'postgres'")


def load_ingestion_config(
    environ: Mapping[str, str] | None = None,
) -> IngestionConfig:
    env = os.environ if environ is None else environ
    artifacts = env.get("AGENTICRAG_DOCLING_ARTIFACTS_PATH", "").strip() or None
    return IngestionConfig(
        max_file_bytes=_positive_int(
            env.get("AGENTICRAG_MAX_FILE_BYTES", str(50 * 1024 * 1024)),
            "AGENTICRAG_MAX_FILE_BYTES",
        ),
        max_pages=_positive_int(env.get("AGENTICRAG_MAX_PAGES", "500"), "AGENTICRAG_MAX_PAGES"),
        max_segments=_positive_int(
            env.get("AGENTICRAG_MAX_SEGMENTS", "100000"), "AGENTICRAG_MAX_SEGMENTS"
        ),
        docling_artifacts_path=artifacts,
    )


def _positive_float(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ConfigurationError("AGENTICRAG_HTTP_TIMEOUT_SECONDS must be numeric") from exc
    if parsed <= 0:
        raise ConfigurationError("AGENTICRAG_HTTP_TIMEOUT_SECONDS must be positive")
    return parsed


def _positive_int(value: str, name: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ConfigurationError(f"{name} must be an integer") from exc
    if parsed <= 0:
        raise ConfigurationError(f"{name} must be positive")
    return parsed


def _structured_output_mode(
    value: str,
) -> Literal["json_schema", "json_object", "prompt"]:
    normalized = value.strip().lower()
    if normalized not in {"json_schema", "json_object", "prompt"}:
        raise ConfigurationError(
            "Structured output mode must be 'json_schema', 'json_object', or 'prompt'"
        )
    return normalized  # type: ignore[return-value]


def _normalize_base_url(url: str) -> str:
    _validate_http_url(url)
    return url.rstrip("/")


def _validate_http_url(url: str) -> None:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ConfigurationError("Provider base URL must be an absolute HTTP(S) URL")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ConfigurationError("Provider base URL cannot contain credentials, query, or fragment")


def _require_loopback(url: str) -> None:
    _validate_http_url(url)
    host = urlsplit(url).hostname
    if host == "localhost":
        return
    try:
        if host is not None and ipaddress.ip_address(host).is_loopback:
            return
    except ValueError:
        pass
    allowed_hosts = {
        item.strip().lower()
        for item in os.environ.get("AGENTICRAG_LOCAL_RUNTIME_HOSTS", "").split(",")
        if item.strip()
    }
    if host is not None and host.lower() in allowed_hosts:
        return
    raise ConfigurationError(
        "Local provider URLs must use localhost, a loopback IP, or a hostname explicitly listed "
        "in AGENTICRAG_LOCAL_RUNTIME_HOSTS"
    )


def validate_local_base_url(url: str) -> str:
    """Validate and normalize a local runtime URL for interactive configuration."""

    _require_loopback(url)
    return _normalize_base_url(url)


def validate_openai_base_url(url: str) -> str:
    """Validate the official OpenAI API boundary used for credentialed sessions."""

    _require_secure_remote(url)
    normalized = _normalize_base_url(url)
    parsed = urlsplit(normalized)
    if parsed.scheme != "https" or parsed.hostname != "api.openai.com":
        raise ConfigurationError(
            "OpenAI API keys may only be sent to https://api.openai.com"
        )
    if parsed.path not in {"", "/", "/v1"}:
        raise ConfigurationError("OpenAI base URL must be https://api.openai.com/v1")
    return "https://api.openai.com/v1"


def _require_secure_remote(url: str) -> None:
    _validate_http_url(url)
    parsed = urlsplit(url)
    if parsed.scheme == "https":
        return
    host = parsed.hostname
    if host == "localhost":
        return
    try:
        if host is not None and ipaddress.ip_address(host).is_loopback:
            return
    except ValueError:
        pass
    raise ConfigurationError("Remote provider URLs must use HTTPS so API credentials are protected")
