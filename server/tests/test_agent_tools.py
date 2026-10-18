import json
from typing import Any

import pytest

from app.runs.agent_tools import MODELS, Tools, calculate, public_url


@pytest.mark.parametrize(
    "name,args",
    [
        ("web_search", {"query": ""}),
        ("web_search", {"query": " "}),
        ("web_search", {"query": "x" * 201}),
        ("web_search", {"query": 7}),
        ("web_search", {"query": "ok", "extra": "refused"}),
        ("library_search", {"query": None}),
        ("read_page", {"url": "https://example.test"}),
        ("read_page", {"url": "x" * 2049, "focus": "ok"}),
        ("read_page", {"url": "https://example.test", "focus": "x" * 501}),
        ("calculate", {"expression": "x" * 201}),
    ],
)
def test_pydantic_contract_is_strict(name: str, args: dict[str, Any]) -> None:
    with pytest.raises(ValueError):
        MODELS[name].model_validate_json(json.dumps(args))


def test_schemas_come_from_argument_models_and_scopes_are_exclusive() -> None:
    web, library = Tools("web", {}), Tools("library", {})
    assert web.names == ["web_search", "read_page", "calculate"]
    assert library.names == ["library_search", "calculate"]
    for tools in [web, library]:
        for schema in tools.schemas():
            function = schema["function"]
            assert function["parameters"] == MODELS[function["name"]].model_json_schema()
            assert function["parameters"]["additionalProperties"] is False


@pytest.mark.parametrize(
    "expression",
    [
        "__import__('os')",
        "open('fake')",
        "name",
        "[1]",
        "2**900",
        "1/0",
        "1e999",
        "99999999999999999",
        "(",
    ],
)
def test_calculator_rejects_code_and_unbounded_values(expression: str) -> None:
    with pytest.raises((ValueError, ArithmeticError, SyntaxError)):
        calculate(expression)


def test_calculator_original_arithmetic_and_scope_state_are_preserved() -> None:
    assert calculate("(120*3 + 180*2)/12") == 60
    assert calculate("-3 + +2 * (7 % 4) // 2") == 0
    tools = Tools("web", {}, user_urls=["https://user.example.test/page"])
    tools.allow("https://search-result.example.test/page")
    next_run = tools.for_run()
    assert public_url("https://user.example.test/page") in next_run.allowed_urls
    assert public_url("https://search-result.example.test/page") not in next_run.allowed_urls


@pytest.mark.parametrize(
    "url",
    [
        "http://example.test",
        "https://localhost",
        "https://127.0.0.1",
        "https://[::1]",
        "https://10.1.2.3",
        "https://name.local",
        "https://user:password@example.test",
        "https://example.test:8443",
    ],
)
def test_public_url_literal_guard(url: str) -> None:
    with pytest.raises(ValueError):
        public_url(url)


def test_private_query_matching_and_recording_policy() -> None:
    tools = Tools("web", {}, private_context=["Private One TWO three four five six seven eight"])
    with pytest.raises(ValueError, match="private"):
        tools.validate(
            "web_search", json.dumps({"query": "one two three four five six seven eight"})
        )
    assert tools.validate("web_search", '{"query":"ordinary public query"}')
    tools.block_web = True
    with pytest.raises(ValueError, match="recording"):
        tools.validate("web_search", '{"query":"ordinary public query"}')
