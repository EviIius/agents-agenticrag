"""Catch the source-order and production-only forms of the Aero blur regression."""

import importlib
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
glass = importlib.import_module("check_glass_css")


@pytest.mark.parametrize("value", ["var(--aero-blur)", "blur(10px)", "none"])
def test_glass_guard_rejects_source_order_that_loses_standard_blur(value: str) -> None:
    unsafe = f".panel {{ backdrop-filter: {value}; -webkit-backdrop-filter: {value}; }}"
    assert len(glass.problems(unsafe, source=True)) == 1
    safe = f".panel {{ -webkit-backdrop-filter: {value}; backdrop-filter: {value}; }}"
    assert glass.problems(safe, source=True) == []
    assert glass.problems(safe) == []


def test_glass_guard_finds_missing_standard_declaration_in_built_nested_css() -> None:
    built = "@layer components{.panel{-webkit-backdrop-filter:blur(18px)}}"
    assert len(glass.problems(built)) == 1
    # A different rule's standard declaration must not hide the broken panel.
    assert len(glass.problems(built + ".other{backdrop-filter:blur(18px)}")) == 1
    assert glass.problems(".panel{backdrop-filter:blur(18px)}") == []


def test_glass_guard_ignores_comments_not_declarations() -> None:
    assert (
        len(
            glass.problems(
                ".panel { -webkit-backdrop-filter : blur(18px); /* backdrop-filter:blur(18px) */ }"
            )
        )
        == 1
    )
    assert glass.problems("/* .old{-webkit-backdrop-filter:blur(18px)} */ .new{color:red}") == []


def test_glass_source_declaration_order_in_every_first_party_stylesheet() -> None:
    failures = {
        str(path.relative_to(ROOT)): errors
        for path in sorted((ROOT / "web/src").rglob("*.css"))
        if (errors := glass.problems(path.read_text(), source=True))
    }
    assert failures == {}


def test_glass_build_guard_cli_rejects_missing_output_and_broken_css(tmp_path: Path) -> None:
    command = [sys.executable, str(ROOT / "scripts/check_glass_css.py"), str(tmp_path)]
    assert subprocess.run(command, capture_output=True, check=False).returncode == 2
    (tmp_path / "index.css").write_text(".panel{-webkit-backdrop-filter:blur(18px)}")
    assert subprocess.run(command, capture_output=True, check=False).returncode == 1
    (tmp_path / "index.css").write_text(".panel{backdrop-filter:blur(18px)}")
    assert subprocess.run(command, capture_output=True, check=False).returncode == 0
