import json
from pathlib import Path

import httpx
import pytest

from app.config import Settings
from app.db.core import connect
from app.main import create_app
from tests.fake_runtime import create_fake_runtime


@pytest.mark.asyncio
async def test_migration_is_idempotent_and_private(tmp_path: Path) -> None:
    for _ in range(2):
        async with connect(tmp_path) as db:
            async with db.execute("PRAGMA user_version") as cursor:
                assert await cursor.fetchone() == (1,)
            async with db.execute("PRAGMA journal_mode") as cursor:
                assert await cursor.fetchone() == ("wal",)
            async with db.execute("PRAGMA foreign_keys") as cursor:
                assert await cursor.fetchone() == (1,)
            async with db.execute("SELECT name FROM sqlite_master WHERE type='table'") as cursor:
                tables = {row[0] for row in await cursor.fetchall()}
            assert {"chats", "messages", "connections", "settings"} <= tables
            assert not {"projects", "agents"} & tables
    assert (tmp_path / "workbench.db").stat().st_mode & 0o777 == 0o600


@pytest.mark.asyncio
async def test_health_spa_cache_and_security(tmp_path: Path) -> None:
    (tmp_path / "index.html").write_text("<html>Workbench fixture</html>")
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets/app-AbCd1234.js").write_text("export {};")
    app = create_app(Settings(data_dir=tmp_path / "data", dev=True), tmp_path)
    async with (
        app.router.lifespan_context(app),
        httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://localhost"
        ) as client,
    ):
        health = await client.get("/api/health")
        assert health.status_code == 200 and health.json()["ok"]
        assert "script-src 'self'" in health.headers["content-security-policy"]
        assert health.headers["x-frame-options"] == "DENY"
        for path in ("/", "/c/fixture", "/design", "/index.html"):
            response = await client.get(path)
            assert "Workbench fixture" in response.text
            assert response.headers["cache-control"] == "no-cache"
        assert "immutable" in (await client.get("/assets/app-AbCd1234.js")).headers["cache-control"]
        assert (await client.get("/api/no-such-route")).status_code == 404
        assert (
            await client.get("/api/health", headers={"host": "evil.example"})
        ).status_code == 403
        assert (
            await client.post("/api/unknown", headers={"origin": "https://evil.example"})
        ).json()["error"]["code"] == "origin_not_allowed"
        assert (
            await client.get("/api/health", headers={"host": "evil@localhost"})
        ).status_code == 403


@pytest.mark.asyncio
async def test_owner_lock_and_production_design(tmp_path: Path) -> None:
    (tmp_path / "index.html").write_text("fixture")
    app = create_app(
        Settings(
            data_dir=tmp_path,
            allowed_hosts="workbench.example.ts.net",
            tailscale_owner="owner@example.com",
        ),
        tmp_path,
    )
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="https://workbench.example.ts.net"
    ) as client:
        assert (await client.get("/api/health")).status_code == 403
        assert (
            await client.get("/api/health", headers={"tailscale-user-login": "other@example.com"})
        ).status_code == 403
        assert (
            await client.get("/api/health", headers={"tailscale-user-login": "owner@example.com"})
        ).status_code == 200
        assert (
            await client.get("/design", headers={"tailscale-user-login": "owner@example.com"})
        ).status_code == 404


@pytest.mark.asyncio
async def test_fake_protocols_and_capture() -> None:
    app = create_fake_runtime()
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://fake"
    ) as client:
        assert all(
            model["name"].startswith("fake-")
            for model in (await client.get("/api/tags")).json()["models"]
        )
        for endpoint in ("/api/chat", "/v1/chat/completions"):
            body = {
                "model": "fake-reasoning",
                "messages": [{"role": "user", "content": "#think"}],
                "stream": True,
            }
            response = await client.post(endpoint, json=body)
            assert "Fake reasoning" in response.text
            if endpoint == "/api/chat":
                answer = "".join(
                    json.loads(line)["message"].get("content", "")
                    for line in response.text.splitlines()
                )
            else:
                answer = "".join(
                    json.loads(line.removeprefix("data: "))["choices"][0]["delta"].get(
                        "content", ""
                    )
                    for line in response.text.splitlines()
                    if line.startswith("data: {")
                )
            assert "Fake runtime reply" in answer
            assert app.state.captures[-1] == body
            if endpoint == "/api/chat":
                assert json.loads(response.text.splitlines()[-1])["done"]
            else:
                assert response.text.endswith("data: [DONE]\n\n")
        error = await client.post(
            "/api/chat", json={"messages": [{"role": "user", "content": "#error:503"}]}
        )
        assert error.status_code == 503


@pytest.mark.asyncio
async def test_migration_rolls_back_failed_script(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.db import core

    migrations = tmp_path / "migrations"
    migrations.mkdir()
    (migrations / "001_broken.sql").write_text(
        "CREATE TABLE should_rollback (id TEXT); INVALID SQL;"
    )
    monkeypatch.setattr(core, "MIGRATIONS", migrations)
    import aiosqlite

    with pytest.raises(aiosqlite.OperationalError):
        async with connect(tmp_path):
            pass
    async with aiosqlite.connect(tmp_path / "workbench.db") as db:
        async with db.execute("PRAGMA user_version") as cursor:
            assert await cursor.fetchone() == (0,)
        async with db.execute(
            "SELECT name FROM sqlite_master WHERE name='should_rollback'"
        ) as cursor:
            assert await cursor.fetchone() is None


@pytest.mark.asyncio
async def test_host_and_origin_edge_cases(tmp_path: Path) -> None:
    app = create_app(Settings(data_dir=tmp_path))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://localhost"
    ) as client:
        for host in (
            "localhost.evil",
            "localhost:bad",
            "evil@localhost",
            "localhost/path",
            "",
            "localhost?evil",
        ):
            response = await client.get("/api/health", headers={"host": host})
            assert response.status_code == 403
            assert response.headers["x-content-type-options"] == "nosniff"
        assert (await client.get("/api/health", headers={"host": "[::1]:8787"})).status_code == 200
        for method in ("POST", "PUT", "DELETE", "OPTIONS"):
            assert (
                await client.request(
                    method, "/api/missing", headers={"origin": "https://evil.example"}
                )
            ).status_code == 403
        # API/CLI requests may omit Origin; same-origin writes reach the actual route.
        assert (await client.post("/api/missing")).status_code == 405
        assert (
            await client.post("/api/missing", headers={"origin": "http://localhost"})
        ).status_code == 405


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "directive, expected",
    [
        ("#cite", "【3†L1】"),
        ('#planner:{"search":false}', '{"search":false}'),
        ("#image?", "True"),
        ("#long:3", "token0 token1 token2"),
    ],
)
async def test_fake_scripted_replies(directive: str, expected: str) -> None:
    app = create_fake_runtime()
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://fake"
    ) as client:
        response = await client.post(
            "/api/chat",
            json={
                "messages": [{"role": "user", "content": directive, "images": ["fixture"]}],
                "stream": False,
            },
        )
        assert expected in response.json()["message"]["content"]
