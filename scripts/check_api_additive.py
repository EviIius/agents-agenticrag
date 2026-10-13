"""Reject breaking OpenAPI changes against the synthetic Phase 3 contract."""

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
METADATA = {"description", "summary", "title", "example", "examples", "default", "operationId"}


def compare(old: Any, new: Any, path: str = "$", roots: tuple[Any,Any] | None = None) -> list[str]:
    roots = roots or (old,new)
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
            elif key == "parameters" and isinstance(value, list):
                errors.extend(parameters(value, new[key], f"{path}.parameters"))
            elif key == "oneOf" and discriminated_extension(old, new, roots):
                # New disjoint discriminator variants preserve every old input.
                # General unions/structural lists remain immutable.
                after = {entry["$ref"]: entry for entry in new[key]}
                for entry in value:
                    errors.extend(compare(entry, after[entry["$ref"]], f"{path}.oneOf", roots))
            elif key == "enum":
                if not set(value).issubset(new[key]):
                    errors.append(f"{path}.enum: removed value")
            else:
                errors.extend(compare(value, new[key], f"{path}.{key}", roots))
        if "parameters" not in old and "parameters" in new:
            errors.extend(parameters([], new["parameters"], f"{path}.parameters"))
        if "required" not in old and isinstance(new.get("required"), list) and new["required"]:
            errors.append(f"{path}.required: added required fields")
    elif isinstance(old, list):
        if not isinstance(new, list) or len(old) != len(new):
            return [f"{path}: structural list changed"]
        for index, (before, after) in enumerate(zip(old, new, strict=True)):
            errors.extend(compare(before, after, f"{path}[{index}]", roots))
    elif old != new:
        errors.append(f"{path}: contract value changed")
    return errors


def discriminated_extension(old: dict[str,Any], new: dict[str,Any], roots: tuple[Any,Any]) -> bool:
    def valid(schema: dict[str,Any], root: Any) -> bool:
        discriminator = schema.get("discriminator", {})
        name, mapping = discriminator.get("propertyName"), discriminator.get("mapping", {})
        choices=schema.get("oneOf")
        if not isinstance(name,str) or not isinstance(mapping,dict) or not isinstance(choices,list):
            return False
        if not all(isinstance(entry,dict) and set(entry)=={"$ref"} for entry in choices):
            return False
        refs=[entry["$ref"] for entry in choices]
        if len(set(refs))!=len(refs) or set(refs)!=set(mapping.values()) or len(mapping)!=len(refs):
            return False
        for tag,ref in mapping.items():
            if not isinstance(ref,str) or not ref.startswith("#/"):
                return False
            target=root
            try:
                for part in ref[2:].split("/"):
                    target=target[part.replace("~1","/").replace("~0","~")]
                if name not in target.get("required",[]) or target["properties"][name].get("const")!=tag:
                    return False
            except (KeyError,TypeError):
                return False
        return True
    if not valid(old,roots[0]) or not valid(new,roots[1]):
        return False
    before,after=old["discriminator"],new["discriminator"]
    return before["propertyName"]==after["propertyName"] and all(after["mapping"].get(tag)==ref for tag,ref in before["mapping"].items())


def parameters(old: list[Any], new: Any, path: str) -> list[str]:
    if not isinstance(new, list):
        return [f"{path}: parameters changed type"]
    def identity(value: dict[str, Any]) -> tuple[Any, Any, Any]:
        return value.get("name"), value.get("in"), value.get("$ref")
    before = {identity(p): p for p in old}
    after = {identity(p): p for p in new}
    errors: list[str] = []
    if len(after) != len(new):
        errors.append(f"{path}: duplicate parameter")
    for key, value in before.items():
        if key not in after:
            errors.append(f"{path}.{key}: removed parameter")
        else:
            errors.extend(compare(value, after[key], f"{path}.{key}"))
    for key, value in after.items():
        if key not in before and (value.get("required") or "$ref" in value):
            errors.append(f"{path}.{key}: added required or unresolved parameter")
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
