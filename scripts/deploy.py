#!/usr/bin/env python3
"""Install Workbench using the existing launchd identity and Tailscale route."""

import argparse
import json
import os
import plistlib
import shutil
import signal
import sqlite3
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from string import Template
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
BASE = Path.home() / ".local/share/workbench"


def run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, check=True, text=True, **kwargs)


def existing_service() -> tuple[Path, dict]:
    matches = []
    for path in (Path.home() / "Library/LaunchAgents").glob("*agenticrag*.plist"):
        data = plistlib.loads(path.read_bytes())
        if (
            "agenticrag" in data.get("ProgramArguments", [])
            and "serve" in data.get("ProgramArguments", [])
        ) or "app.main:app" in data.get("ProgramArguments", []):
            matches.append((path, data))
    if len(matches) != 1:
        raise RuntimeError(
            "Expected exactly one existing Workbench launchd plist; choose its identity before deploying."
        )
    path, data = matches[0]
    args = data.get("ProgramArguments", [])
    if "--host" in args and args[args.index("--host") + 1] != "127.0.0.1":
        raise RuntimeError("Existing bind differs from 127.0.0.1; deployment stopped.")
    if "--port" in args and args[args.index("--port") + 1] != "8787":
        raise RuntimeError("Existing port differs from 8787; deployment stopped.")
    return path, data


def install_engine(source: Path, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    # Whitelist public engine source, never watched recordings or logs.
    for name in ["bin", "localtranscribe", "tests"]:
        run(
            [
                "rsync",
                "-a",
                "--delete",
                "--exclude=__pycache__/",
                str(source / name) + "/",
                str(target / name) + "/",
            ]
        )
    for name in [
        "README.md",
        "config.example.json",
        "glossary.example.txt",
        "install.sh",
        "uninstall.sh",
    ]:
        shutil.copy2(source / name, target / name)
    first_config = not (target / "config.json").exists()
    for name in ["models", "config.json", "glossary.txt", ".python"]:
        src, dest = source / name, target / name
        if src.exists() and not dest.exists():
            if src.is_dir():
                shutil.copytree(src, dest)
            else:
                dest.touch(mode=0o600)
                shutil.copyfile(src, dest)
                dest.chmod(0o600)
    # Model/glossary paths inside the source repo now refer to the installed copy.
    config_file = target / "config.json"
    if config_file.exists():
        config = json.loads(config_file.read_text())
        if first_config:
            # Give the installed engine empty private workspace folders. Do not
            # point it at the original watcher's recording collection.
            runtime = target / "runtime"
            runtime.mkdir(mode=0o700, exist_ok=True)
            config["data_dir"] = str(runtime)
            for folder in ["inbox", "done", "failed", "logs"]:
                config[folder + "_dir"] = None
                (runtime / folder).mkdir(mode=0o700, exist_ok=True)
        for key in ["model", "vad_model", "glossary"]:
            value = config.get(key)
            if isinstance(value, str):
                path = Path(value).expanduser()
                if path.is_absolute() and path.is_relative_to(source):
                    config[key] = str(target / path.relative_to(source))
        config_file.write_text(json.dumps(config, indent=2) + "\n")
        config_file.chmod(0o600)
    # The watcher is separate; Workbench's installed engine needs no recordings.
    run([str(target / "bin/transcribe"), "doctor", "--json"], capture_output=True)


def backup_database(data: Path) -> None:
    directory = data / "backups"
    directory.mkdir(parents=True, exist_ok=True)
    source = data / "workbench.db"
    if source.exists():
        name = "workbench-" + datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ") + ".db"
        destination = directory / name
        destination.touch(mode=0o600)
        with (
            sqlite3.connect(source.as_uri() + "?mode=ro", uri=True) as db,
            sqlite3.connect(destination) as copy,
        ):
            db.backup(copy)
        destination.chmod(0o600)
        for old in sorted(directory.glob("workbench-*.db"))[:-10]:
            old.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply", action="store_true", help="Install and restart; default prints the plan only."
    )
    parser.add_argument("--engine-source", type=Path, default=ROOT / "transcribe")
    parser.add_argument("--preview-pid", type=int)
    args = parser.parse_args()
    plist, old = existing_service()
    previous_plist = plist.read_bytes()
    import httpx

    tailscale = Path("/Applications/Tailscale.app/Contents/MacOS/Tailscale")
    route = run([str(tailscale), "serve", "status"], capture_output=True).stdout
    if "http://127.0.0.1:8787" not in route:
        raise RuntimeError("Tailscale route differs from 127.0.0.1:8787; deployment stopped.")
    env = old.get("EnvironmentVariables", {})
    hosts = env.get("WORKBENCH_ALLOWED_HOSTS", env.get("AGENTICRAG_ALLOWED_HOSTS", ""))
    if not hosts:
        raise RuntimeError("Existing allowed hosts are missing; deployment stopped.")
    source = args.engine_source.expanduser().resolve(strict=True)
    print(
        json.dumps(
            {
                "label": old["Label"],
                "bind": "127.0.0.1:8787",
                "installed_app": str(BASE / "app"),
                "installed_engine": str(BASE / "app/transcribe"),
                "old_data": "read-only import only",
                "apply": args.apply,
            }
        )
    )
    if not args.apply:
        return
    run(["make", "build"], cwd=ROOT)
    backup_database(BASE / "data")
    logs = BASE / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    for name in ["workbench.log"]:
        path = logs / name
        path.touch(mode=0o600, exist_ok=True)
        path.chmod(0o600)
    backup = BASE / "data/backups/launchd-before-phase3.plist"
    if not backup.exists():
        backup.write_bytes(plist.read_bytes())
        backup.chmod(0o600)
    app = BASE / "app"
    (app / "server").mkdir(parents=True, exist_ok=True)
    run(
        [
            "rsync",
            "-a",
            "--delete",
            "--exclude=.venv/",
            "--exclude=tests/",
            "--exclude=evals/",
            "--exclude=__pycache__/",
            str(ROOT / "server") + "/",
            str(app / "server") + "/",
        ]
    )
    run(["rsync", "-a", "--delete", str(ROOT / "shared") + "/", str(app / "shared") + "/"])
    uv = shutil.which("uv")
    if not uv:
        raise RuntimeError("uv is required.")
    run([uv, "sync", "--frozen", "--no-dev"], cwd=app / "server")
    engine = app / "transcribe"
    install_engine(source, engine)
    values = {
        "LABEL": old["Label"],
        "PYTHON": str(app / "server/.venv/bin/python"),
        "SERVER": str(app / "server"),
        "DATA": str(BASE / "data"),
        "HOSTS": hosts,
        "OWNER": env.get("WORKBENCH_TAILSCALE_OWNER", ""),
        "ENGINE": str(engine),
        "LOG": str(logs / "workbench.log"),
        "PATH": os.environ["PATH"],
    }
    rendered = Template((ROOT / "deploy/launchd.plist.template").read_text()).substitute(
        {k: escape(v) for k, v in values.items()}
    )
    plistlib.loads(rendered.encode())
    domain = f"gui/{os.getuid()}"
    if args.preview_pid:
        command = run(
            ["ps", "-p", str(args.preview_pid), "-o", "args="], capture_output=True
        ).stdout
        if "-m uvicorn app.main:app --host 127.0.0.1 --port 8787 --workers 1" not in command:
            raise RuntimeError("Preview PID is not the expected Workbench server; stopped.")
        os.kill(args.preview_pid, signal.SIGTERM)
        for _ in range(50):
            try:
                os.kill(args.preview_pid, 0)
            except ProcessLookupError:
                break
            time.sleep(0.1)
    subprocess.run(["launchctl", "bootout", domain, str(plist)], capture_output=True)
    plist.write_text(rendered)
    plist.chmod(0o600)
    try:
        run(["launchctl", "bootstrap", domain, str(plist)])
        for _ in range(50):
            try:
                with httpx.Client(timeout=2) as client:
                    response = client.get("http://127.0.0.1:8787/api/health")
                    if response.status_code == 200:
                        print("Workbench launchd health: HTTP 200")
                        return
            except httpx.HTTPError:
                pass
            time.sleep(0.2)
        raise RuntimeError("New service did not become healthy.")
    except BaseException:
        subprocess.run(["launchctl", "bootout", domain, str(plist)], capture_output=True)
        plist.write_bytes(previous_plist)
        plist.chmod(0o600)
        subprocess.run(["launchctl", "bootstrap", domain, str(plist)], capture_output=True)
        raise


if __name__ == "__main__":
    main()
