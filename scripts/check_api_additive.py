"""Reject breaking OpenAPI changes against the synthetic Phase 3 contract."""

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
METADATA = {"description", "summary", "title", "example", "examples", "default", "operationId"}


def compare(old: Any, new: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(old, dict):
        if not isinstance(new, dict):
            return [f"{path}: object changed type"]
        for key, value in old.items():
            if key in METADATA:
                continue
            if key not in new:
                errors.append(f"{path}.{key}: removed")
            elif key == "required" and isinstance(value, list):
                if set(value) != set(new[key]):
                    errors.append(f"{path}.required: required fields changed")
            elif key == "enum":
                if not set(value).issubset(new[key]):
                    errors.append(f"{path}.enum: removed value")
            else:
                errors.extend(compare(value, new[key], f"{path}.{key}"))
        if "required" not in old and isinstance(new.get("required"), list) and new["required"]:
            errors.append(f"{path}.required: added required fields")
    elif isinstance(old, list):
        if not isinstance(new, list) or len(old) != len(new):
            return [f"{path}: structural list changed"]
        for index, (before, after) in enumerate(zip(old, new, strict=True)):
            errors.extend(compare(before, after, f"{path}[{index}]"))
    elif old != new:
        errors.append(f"{path}: contract value changed")
    return errors


def main() -> None:
    sys.path.insert(0, str(ROOT / "server"))
    from app.main import create_app

    baseline = json.loads((ROOT / "artifacts/baseline/openapi-phase3.json").read_text())
    current = create_app().openapi()
    errors = compare(baseline, current)
    if errors:
        raise SystemExit("\n".join(errors))
    print("API additive guard: Phase 3 contract preserved.")


if __name__ == "__main__":
    main()
