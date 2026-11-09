"""Compile/sign the version-two read-only helper. No permission or app access."""

import argparse
import json
from pathlib import Path

from build_dynamic_reader import build

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--read-boundary", required=True, type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            build(args.output, args.read_boundary, source_name="ReadOnlySnapshot.swift"), indent=2
        )
    )
