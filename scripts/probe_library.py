"""Phase 7-0 on isolated data; output metadata and timings, never text or vectors.

Use --server-dir to select checkout or installed application source. Run with
each candidate interpreter. Never pass the production data folder to this tool.
"""

import argparse
import asyncio
import hashlib
import importlib.metadata
import ipaddress
import json
import math
import platform
import random
import sqlite3
import statistics
import sys
import tempfile
from pathlib import Path
from time import perf_counter
from urllib.parse import urlsplit

import httpx
import sqlite_vec


async def probe(server_dir: Path, model: str, runtime: str) -> dict[str, object]:
    host = urlsplit(runtime).hostname or ""
    if not ipaddress.ip_address(host).is_loopback:
        raise ValueError("The probe requires a loopback embedding runtime")
    sys.path.insert(0, str(server_dir.resolve()))
    from app.db.core import connect

    extension = Path(sqlite_vec.loadable_path()).with_suffix(".dylib")
    result: dict[str, object] = {
        "python": platform.python_version(),
        "python_executable": sys.executable,
        "sqlite": sqlite3.sqlite_version,
        "sqlite_vec_package": importlib.metadata.version("sqlite-vec"),
        "extension_sha256": hashlib.sha256(extension.read_bytes()).hexdigest(),
        "db_helper_sha256": hashlib.sha256(
            (server_dir / "app/db/core.py").read_bytes()
        ).hexdigest(),
        "database": "isolated temporary synthetic",
        "status": "passed",
    }
    with sqlite3.connect(":memory:") as db:
        try:
            db.enable_load_extension(True)
            try:
                db.load_extension(sqlite_vec.loadable_path())
            finally:
                db.enable_load_extension(False)
            result["step_1"] = {
                "status": "passed",
                "vec_version": db.execute("SELECT vec_version()").fetchone()[0],
            }
        except (AttributeError, sqlite3.Error) as exc:
            return result | {
                "status": "blocked",
                "step_1": {"status": "blocked", "error": str(exc)},
            }

    with tempfile.TemporaryDirectory(prefix="workbench-library-synthetic-") as name:
        root = Path(name)
        root.chmod(0o700)
        async with connect(root) as db:
            try:
                await db.enable_load_extension(True)
                try:
                    await db.load_extension(sqlite_vec.loadable_path())
                finally:
                    await db.enable_load_extension(False)
                async with db.execute(
                    "SELECT vec_version(), (SELECT user_version FROM pragma_user_version)"
                ) as cursor:
                    row = await cursor.fetchone()
                assert row
                result["step_2"] = {
                    "status": "passed",
                    "vec_version": row[0],
                    "schema": row[1],
                    "extension_loading_disabled_after_load": True,
                }
            except (AttributeError, sqlite3.Error) as exc:
                return result | {
                    "status": "blocked",
                    "step_2": {"status": "blocked", "error": str(exc)},
                }
            await db.execute(
                "CREATE VIRTUAL TABLE probe_vectors USING vec0("
                "embedding FLOAT[768] distance_metric=cosine)"
            )
            rng = random.Random(700)
            started = perf_counter()
            await db.executemany(
                "INSERT INTO probe_vectors(rowid, embedding) VALUES (?, ?)",
                (
                    (n, sqlite_vec.serialize_float32([rng.uniform(-1, 1) for _ in range(768)]))
                    for n in range(1, 20001)
                ),
            )
            await db.commit()
            insert_seconds = perf_counter() - started
            times = []
            for _ in range(50):
                query = sqlite_vec.serialize_float32([rng.uniform(-1, 1) for _ in range(768)])
                started = perf_counter()
                async with db.execute(
                    "SELECT rowid, distance FROM probe_vectors "
                    "WHERE embedding MATCH ? AND k = 40 ORDER BY distance",
                    (query,),
                ) as cursor:
                    rows = await cursor.fetchall()
                times.append((perf_counter() - started) * 1000)
                assert len(rows) == 40 and len({row[0] for row in rows}) == 40
                assert all(1 <= row[0] <= 20000 and math.isfinite(row[1]) for row in rows)
                assert [row[1] for row in rows] == sorted(row[1] for row in rows)
            result["step_3"] = {
                "status": "passed",
                "vectors": 20000,
                "dimensions": 768,
                "queries": 50,
                "k": 40,
                "metric": "cosine",
                "seed": 700,
                "insert_seconds": insert_seconds,
                "query_ms": times,
                "p50_ms": statistics.median(times),
                "p95_ms": sorted(times)[math.ceil(0.95 * len(times)) - 1],
                "timing_includes_async_execute_and_fetch": True,
                "valid_sorted_unique_results": True,
            }
    result["temporary_data_removed"] = not root.exists()

    async with httpx.AsyncClient(base_url=runtime, timeout=60, follow_redirects=False) as client:
        response = await client.post("/api/show", json={"model": model})
        response.raise_for_status()
        show = response.json()
        assert "embedding" in show.get("capabilities", [])
        info = show["model_info"]
        architecture = info["general.architecture"]
        context = info[f"{architecture}.context_length"]
        passage = (
            "This synthetic orchard workshop has lanterns, gates and fictional meeting notes. " * 50
        )[:3000]
        assert len(passage) == 3000
        started = perf_counter()
        response = await client.post(
            "/api/embed", json={"model": model, "input": passage, "truncate": False}
        )
        response.raise_for_status()
        embedded = response.json()
        elapsed = perf_counter() - started
        vectors = embedded["embeddings"]
        assert (
            len(vectors) == 1 and vectors[0] and all(math.isfinite(value) for value in vectors[0])
        )
        assert 0 < embedded["prompt_eval_count"] <= context
        result["step_4"] = {
            "status": "passed",
            "model": model,
            "reported_capabilities": show["capabilities"],
            "reported_context_length": context,
            "input_characters": len(passage),
            "truncate": False,
            "http_status": response.status_code,
            "prompt_eval_count": embedded["prompt_eval_count"],
            "returned_dimensions": len(vectors[0]),
            "finite_vector": True,
            "elapsed_seconds": elapsed,
            "total_duration_ns": embedded.get("total_duration"),
            "load_duration_ns": embedded.get("load_duration"),
            "embedding_requests": 1,
        }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-dir", type=Path, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--runtime", default="http://127.0.0.1:11434")
    args = parser.parse_args()
    result = asyncio.run(probe(args.server_dir, args.model, args.runtime))
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
