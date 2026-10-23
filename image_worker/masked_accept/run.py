"""Run exactly one frozen, approved acceptance case; no automatic case continuation."""

import argparse
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "server"))
from app.capacity import Capacity
from app.images.codec import ReferenceCodec
from app.images.engine import Engine
from control import digest, run_case


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=["flux"])
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    if digest(Path(__file__)) != digest(args.root / "worker/run.py"):
        raise ValueError("Launcher differs from frozen source")
    capacity = Capacity(Path.home() / ".local/share/workbench/data/native.lock")
    engine = Engine(None, capacity)
    codec = ReferenceCodec(args.root / "worker")
    try:
        await run_case(args.root, args.case, capacity, engine, codec)
    finally:
        await codec.close()


if __name__ == "__main__":
    asyncio.run(main())
