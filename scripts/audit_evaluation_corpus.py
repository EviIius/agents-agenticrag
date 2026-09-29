"""Audit a frozen corpus and JSONL question set before comparing models."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from agenticrag.cli import _load_cases
from agenticrag.evaluation_audit import audit_evaluation_corpus


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", type=Path)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--strict", action="store_true", help="Exit unsuccessfully when v3 is not ready")
    args = parser.parse_args()
    report = audit_evaluation_corpus(args.database, _load_cases(args.dataset))
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.strict and not report["ready"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
