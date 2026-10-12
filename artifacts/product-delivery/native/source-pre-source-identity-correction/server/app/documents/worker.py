"""Private subprocess protocol. Never send document contents to stdout or logs."""

import json
import logging
import sys
from dataclasses import asdict
from pathlib import Path

from ..errors import AppError
from .extract import extract


def main() -> None:
    logging.disable(logging.CRITICAL)
    source, suffix, output = sys.argv[1:]
    target = Path(output)
    try:
        result = asdict(extract(Path(source), suffix))
    except AppError as exc:
        result = {"error": exc.code}
    with target.open("x", encoding="utf-8") as destination:
        target.chmod(0o600)
        json.dump(result, destination, ensure_ascii=False)


if __name__ == "__main__":
    main()
