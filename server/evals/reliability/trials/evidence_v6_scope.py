"""Use retained generic data framing to isolate the actual task."""

import importlib.util
from pathlib import Path


def task_outside_quotes(text: str) -> str:
    location = Path(__file__).parent / "v7/app/runs/untrusted.py"
    spec = importlib.util.spec_from_file_location("_scope_quoted_material", location)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    separated: str | None = module.quoted_request(text)
    return separated.split("\n\nUser task outside that material:\n", 1)[1] if separated else text
