"""Generate API types from the app factory; --check rejects a stale checked-in contract."""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
from app.main import create_app  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    destination = ROOT / "web/src/lib/api-types.ts"
    with tempfile.TemporaryDirectory() as temporary:
        schema = Path(temporary) / "openapi.json"
        output = Path(temporary) / "api-types.ts"
        schema.write_text(json.dumps(create_app().openapi()))
        subprocess.run(["node", str(ROOT / "web/node_modules/openapi-typescript/bin/cli.js"), str(schema), "--output", str(output)], check=True)
        generated = output.read_text()
        if args.check:
            if not destination.exists() or generated != destination.read_text():
                raise SystemExit("API types are stale. Run make api-types.")
            print("API contract: up to date.")
        else:
            destination.write_text(generated)


if __name__ == "__main__":
    main()
