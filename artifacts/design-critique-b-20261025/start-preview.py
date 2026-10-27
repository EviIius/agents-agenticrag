"""Start an isolated synthetic review preview after Playwright releases its ports."""
import json
import os
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = Path.home() / ".local/share/workbench/qa/design-critique-b-20261025/preview"


def main():
    for port in (18080, 18787, 5173):
        with socket.socket() as check:
            check.settimeout(0.2)
            assert check.connect_ex(("127.0.0.1", port)), f"Port {port} is already owned"
    PRIVATE.mkdir(parents=True, exist_ok=True)
    commands = {
        "runtime": "uv run --directory server uvicorn tests.fake_runtime:app --host 127.0.0.1 --port 18080 --workers 1",
        "app": "uv run --directory server uvicorn tests.serve_app:app --host 127.0.0.1 --port 18787 --workers 1",
        "web": "npm run dev --prefix web -- --port 5173 --strictPort",
    }
    processes = {}
    for name, command in commands.items():
        with (PRIVATE / f"{name}.log").open("w") as output:
            process = subprocess.Popen(
                ["/bin/sh", "-c", ". scripts/tool-env.sh; exec " + command],
                cwd=ROOT,
                env={**os.environ, "WORKBENCH_E2E": "1"},
                stdout=output,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
        processes[name] = process.pid
    urls = ["http://127.0.0.1:18080/api/tags", "http://127.0.0.1:18787/api/health", "http://127.0.0.1:5173/design?chat-state"]
    for url in urls:
        for attempt in range(40):
            try:
                with urllib.request.urlopen(url, timeout=1) as response:
                    assert response.status == 200
                break
            except (OSError, AssertionError):
                if attempt == 39:
                    raise
                time.sleep(0.25)
    record = {"synthetic_only": True, "pids": processes, "urls": urls, "live_app_unchanged": True}
    (PRIVATE / "processes.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record))


if __name__ == "__main__":
    main()
