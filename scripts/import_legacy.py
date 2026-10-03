#!/usr/bin/env python3
"""Run with: uv run --directory server python ../scripts/import_legacy.py."""
import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "server"))
from app.config import Settings  # noqa: E402
from app.db.core import Store, connect  # noqa: E402
from app.db.legacy import import_legacy  # noqa: E402

async def main() -> None:
    config = Settings()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=config.legacy_db)
    parser.add_argument("--data-dir", type=Path, default=config.data_dir)
    args = parser.parse_args()
    async with connect(args.data_dir) as db:
        imported, skipped = await import_legacy(Store(db), args.source)
    print(json.dumps({"imported": imported, "skipped": skipped}))

if __name__ == "__main__":
    asyncio.run(main())
