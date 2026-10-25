"""TH1: palette and greeting preferences are stored on the Mac and validated."""

from typing import Any

import pytest


@pytest.mark.parametrize(
    "palette", ["cobalt", "lime", "paper", "ember", "orchid", "midnight", "mono", "aero"]
)
async def test_palette_and_greeting_round_trip_with_other_appearance(
    chat_app: Any, palette: str
) -> None:
    _, client, _ = chat_app
    body = {
        "appearance.theme": "dark",
        "appearance.palette": palette,
        "appearance.greeting": "surprise",
        "appearance.font": "serif",
    }
    response = await client.patch("/api/settings", json=body)
    assert response.status_code == 200
    saved = (await client.get("/api/bootstrap")).json()["settings"]
    assert {key: saved[key] for key in body} == body


@pytest.mark.parametrize(
    "body",
    [
        {"appearance.palette": "neon"},
        {"appearance.palette": None},
        {"appearance.greeting": "klingon"},
    ],
)
async def test_unknown_palette_or_greeting_is_rejected_without_saving(
    chat_app: Any, body: dict[str, Any]
) -> None:
    _, client, _ = chat_app
    response = await client.patch("/api/settings", json=body)
    assert response.status_code == 422
    assert not set(body) & set((await client.get("/api/settings")).json())
