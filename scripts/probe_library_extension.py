"""First Library prerequisite; synthetic in-memory DB, metadata-only output.

Run separately in the checkout and installed app interpreter. A nonzero exit is
the Phase 7-0 stop condition; do not continue to vector or embedding benchmarks.
"""

import hashlib
import importlib.metadata
import json
import platform
import sqlite3
import sys
from pathlib import Path

import sqlite_vec


def main() -> int:
    extension = Path(sqlite_vec.loadable_path()).with_suffix(".dylib")
    result = {
        "python": platform.python_version(),
        "python_executable": sys.executable,
        "sqlite": sqlite3.sqlite_version,
        "sqlite_vec_package": importlib.metadata.version("sqlite-vec"),
        "extension_sha256": hashlib.sha256(extension.read_bytes()).hexdigest(),
        "database": "synthetic in-memory",
        "step": 1,
        "status": "passed",
    }
    with sqlite3.connect(":memory:") as db:
        try:
            db.enable_load_extension(True)
            try:
                db.load_extension(sqlite_vec.loadable_path())
            finally:
                db.enable_load_extension(False)
            result["vec_version"] = db.execute("SELECT vec_version()").fetchone()[0]
        except (AttributeError, sqlite3.Error) as exc:
            result["status"] = "blocked"
            result["error_type"] = type(exc).__name__
            result["error"] = str(exc)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
