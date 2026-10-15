"""Exact current-profile admission without relaxing the original resource limits."""

from types import SimpleNamespace
from typing import Any, cast

import pytest
import respx

from app.errors import AppError
from app.images.engine import QUALIFIED_DIGEST, Engine
from app.providers.registry import Registry
from app.workflows.qualification import image_models

CURRENT_DIGEST = "09386c7af8487c073bfb845833462d30d0d48ad69428c301b909dc159c028b0a"


def resident(**changes: Any) -> dict[str, Any]:
    return {
        "name": "arbitrary-user-alias",
        "digest": CURRENT_DIGEST,
        "context_length": 32768,
        "size_vram": 19508609678,
        **changes,
    }


@respx.mock
async def test_current_profile_is_admitted_by_digest_with_no_management_request() -> None:
    respx.get("http://127.0.0.1:11434/api/ps").respond(200, json={"models": [resident()]})
    await Engine(None).admit()
    assert len(respx.calls) == 1
    assert respx.calls[0].request.method == "GET"


@pytest.mark.parametrize(
    "changes",
    [
        {"digest": "unknown-smaller-model", "size_vram": 1024},
        {"digest": [CURRENT_DIGEST]},
        {"context_length": 65536},
        {"context_length": 16384},
        {"size_vram": 21827095101},
        {"size_vram": 0},
        {"size_vram": "19508609678"},
    ],
)
@respx.mock
async def test_current_profile_keeps_all_original_admission_limits(changes: dict[str, Any]) -> None:
    respx.get("http://127.0.0.1:11434/api/ps").respond(200, json={"models": [resident(**changes)]})
    with pytest.raises(AppError, match="not qualified"):
        await Engine(None).admit()
    assert all(call.request.method == "GET" for call in respx.calls)


@respx.mock
async def test_two_individually_qualified_profiles_are_still_rejected() -> None:
    respx.get("http://127.0.0.1:11434/api/ps").respond(
        200, json={"models": [resident(), resident(digest=QUALIFIED_DIGEST)]}
    )
    with pytest.raises(AppError, match="not qualified"):
        await Engine(None).admit()


async def test_workflow_picker_and_engine_share_current_digest_admission() -> None:
    names = ["arbitrary-user-alias", "unqualified-copy", "other-context"]
    infos = [
        SimpleNamespace(connection_id="fake", model_id=name, context_length=context)
        for name, context in zip(names, [32768, 32768, 16384], strict=True)
    ]

    async def models() -> list[Any]:
        return infos

    async def metadata(*args: Any) -> dict[str, Any]:
        return {
            "models": [
                {"name": names[0], "digest": CURRENT_DIGEST},
                {"name": names[1], "digest": "unknown-smaller-model"},
                {"name": names[2], "digest": CURRENT_DIGEST},
            ]
        }

    async def adapter(*args: Any) -> Any:
        return SimpleNamespace(base_url="http://127.0.0.1:11434", json=metadata)

    registry = cast(Registry, SimpleNamespace(models=models, adapter=adapter))
    assert await image_models(registry) == [{"connection_id": "fake", "model_id": names[0]}]
