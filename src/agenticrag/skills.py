from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .errors import ConfigurationError, WorkflowError


_NAME = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")


@dataclass(frozen=True)
class SkillDocument:
    name: str
    description: str
    instructions: str
    sha256: str
    source: str = "project-local"

    def metadata(self) -> dict[str, str]:
        return {
            "name": self.name,
            "description": self.description,
            "sha256": self.sha256,
            "source": self.source,
        }


class SkillRegistry:
    """Loads bounded local skills from explicit project and Agent Skills roots."""

    def __init__(
        self,
        root: str | Path,
        *,
        additional_roots: Sequence[str | Path] = (),
        max_skills: int = 64,
        max_skill_bytes: int = 64 * 1024,
    ) -> None:
        if max_skills <= 0 or max_skill_bytes <= 0:
            raise ValueError("Skill limits must be positive")
        self.root = Path(root).expanduser().resolve()
        self.roots = (
            (self.root, "project-local"),
            *tuple(
                (Path(item).expanduser().resolve(), "agent-skills")
                for item in additional_roots
                if Path(item).expanduser().resolve() != self.root
            ),
        )
        self.max_skills = max_skills
        self.max_skill_bytes = max_skill_bytes

    def discover(self) -> tuple[SkillDocument, ...]:
        paths: list[tuple[Path, Path, str]] = []
        for root, source in self.roots:
            if not root.exists():
                continue
            if not root.is_dir():
                raise ConfigurationError(f"Skills root is not a directory: {root}")
            paths.extend(
                (path, root, source)
                for path in sorted(root.glob("*/SKILL.md"), key=lambda item: item.as_posix())
            )
        if len(paths) > self.max_skills:
            raise ConfigurationError(
                f"Skills root contains {len(paths)} skills; limit is {self.max_skills}"
            )
        skills: list[SkillDocument] = []
        names: set[str] = set()
        for path, root, source in paths:
            resolved = path.resolve(strict=True)
            if not resolved.is_relative_to(root):
                raise ConfigurationError("Skill path escapes the configured skills root")
            skill = self._read(resolved, source)
            if skill.name in names:
                raise ConfigurationError(f"Duplicate skill name: {skill.name}")
            names.add(skill.name)
            skills.append(skill)
        return tuple(skills)

    def metadata(self) -> tuple[dict[str, str], ...]:
        return tuple(skill.metadata() for skill in self.discover())

    def load(self, name: str) -> SkillDocument:
        if not _NAME.fullmatch(name):
            raise WorkflowError("Skill name is invalid")
        by_name = {skill.name: skill for skill in self.discover()}
        if name not in by_name:
            raise WorkflowError(f"Unknown or unavailable skill: {name}")
        return by_name[name]

    def _read(self, path: Path, source: str) -> SkillDocument:
        size = path.stat().st_size
        if size > self.max_skill_bytes:
            raise ConfigurationError(
                f"Skill file {path.name} is {size} bytes; limit is {self.max_skill_bytes}"
            )
        try:
            raw = path.read_bytes()
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ConfigurationError(f"Skill must be valid UTF-8: {path}") from exc
        if "\x00" in text:
            raise ConfigurationError(f"Skill cannot contain NUL bytes: {path}")
        metadata, instructions = _frontmatter(text)
        name = metadata.get("name", "").strip()
        description = metadata.get("description", "").strip()
        if not _NAME.fullmatch(name):
            raise ConfigurationError(f"Skill has an invalid name: {path}")
        if not description or len(description) > 2_000:
            raise ConfigurationError(f"Skill description must contain 1 to 2000 characters: {path}")
        if not instructions.strip():
            raise ConfigurationError(f"Skill instructions are empty: {path}")
        return SkillDocument(
            name=name,
            description=description,
            instructions=instructions.strip(),
            sha256=hashlib.sha256(raw).hexdigest(),
            source=source,
        )


def _frontmatter(text: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ConfigurationError("SKILL.md must start with YAML-style frontmatter")
    try:
        end = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration as exc:
        raise ConfigurationError("SKILL.md frontmatter is not terminated") from exc
    metadata: dict[str, str] = {}
    in_metadata = False
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[:1].isspace():
            if in_metadata:
                continue
            raise ConfigurationError("Skill frontmatter contains an unexpected nested field")
        key, separator, value = line.partition(":")
        normalized_key = key.strip()
        if not separator or normalized_key not in {"name", "description", "metadata"}:
            raise ConfigurationError(
                "Skill frontmatter supports only name and description, plus standard metadata"
            )
        in_metadata = normalized_key == "metadata"
        if in_metadata:
            continue
        if normalized_key in metadata:
            raise ConfigurationError(f"Duplicate skill frontmatter field: {normalized_key}")
        cleaned = value.strip().strip('"').strip("'")
        metadata[normalized_key] = cleaned
    return metadata, "\n".join(lines[end + 1 :])
