"""Deployment settings; product settings belong in SQLite."""

import json
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

APP_NAME: str = str(
    json.loads((Path(__file__).parents[2] / "shared/config.json").read_text())["APP_NAME"]
)
VERSION = "1.0.0-alpha.0"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="WORKBENCH_", extra="ignore", populate_by_name=True
    )
    data_dir: Path = Path.home() / ".local/share/workbench/data"
    host: str = "127.0.0.1"
    port: int = 8787
    allowed_hosts: str = Field(
        default="",
        validation_alias=AliasChoices("WORKBENCH_ALLOWED_HOSTS", "AGENTICRAG_ALLOWED_HOSTS"),
    )
    tailscale_owner: str = ""
    dev: bool = False
    log_level: str = "INFO"
    web_fixtures: Path | None = None

    @property
    def hosts(self) -> set[str]:
        return {"localhost", "127.0.0.1", "::1"} | {
            value.strip().lower() for value in self.allowed_hosts.split(",") if value.strip()
        }
