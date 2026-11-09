"""Compile the selected-container diagnostic. No native app/permission access."""

import argparse
import json
from pathlib import Path

from build_dynamic_reader import build

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--read-boundary", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.output, args.read_boundary, source_name="SelectedMetadata.swift")))
