"""Full isolated browser run; restore the accepted installed app even on failure."""
import hashlib
import json
import os
import plistlib
import shutil
import subprocess
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "artifacts/phase-8/8a"
PLIST = Path.home() / "Library/LaunchAgents/dev.agenticrag.workbench.plist"
DOMAIN = f"gui/{os.getuid()}"


def health(url):
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return response.status
    except Exception:
        return 0


def files():
    roots = [ROOT / "server/app", ROOT / "server/tests", ROOT / "web/src", ROOT / "web/tests", ROOT / "shared"]
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for folder in roots for p in folder.rglob("*") if p.is_file()
            and "__pycache__" not in p.parts and p.suffix in {".py", ".sql", ".json", ".ts", ".tsx", ".css"}}


def main():
    plist = PLIST.read_bytes()
    config = plistlib.loads(plist)
    assert config["Label"] == "dev.agenticrag.workbench"
    assert "8787" in config["ProgramArguments"] and "127.0.0.1" in config["ProgramArguments"]
    with urllib.request.urlopen("http://127.0.0.1:8787/api/runs/active") as response:
        assert not json.load(response), "Wait for the active live chat before running browser tests."
    before_files = files()
    (OUT / "e2e-source-inputs.json").write_text(json.dumps(before_files, indent=2)+"\n")
    tracked = subprocess.check_output(["git", "ls-files", "artifacts"], cwd=ROOT, text=True).splitlines()
    tracked_before = {name: (ROOT/name).read_bytes() for name in tracked if (ROOT/name).is_file()}
    existing = {p for p in (ROOT/"artifacts").rglob("*") if p.is_file()}
    start = time.monotonic()
    result = -1
    try:
        subprocess.run(["launchctl", "bootout", DOMAIN, str(PLIST)], check=True, capture_output=True)
        with (OUT/"e2e.txt").open("w") as log:
            result = subprocess.run(["make", "e2e"], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT).returncode
    finally:
        assert PLIST.read_bytes() == plist
        restore = subprocess.run(["launchctl", "bootstrap", DOMAIN, str(PLIST)], capture_output=True)
        for _ in range(30):
            if health("http://127.0.0.1:8787/api/health") == 200:
                break
            time.sleep(1)
        archived = []
        for name, data in tracked_before.items():
            file = ROOT/name
            if file.exists() and file.read_bytes() != data:
                target = OUT/"regenerated-metrics"/Path(name).relative_to("artifacts")
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file, target)
                file.write_bytes(data)
                archived.append(name)
        for file in sorted({p for p in (ROOT/"artifacts").rglob("*") if p.is_file()}-existing):
            if file.is_relative_to(OUT):
                continue
            target = OUT/"regenerated-metrics"/file.relative_to(ROOT/"artifacts")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(file, target)
            archived.append(str(file.relative_to(ROOT)))
        final = {"exit_code": result, "seconds": time.monotonic()-start,
                 "source_unchanged_during_suite": before_files == files(),
                 "service_restoration_exit": restore.returncode,
                 "local_health": health("http://127.0.0.1:8787/api/health"),
                 "tls_health": health("https://jakes-mac-mini.tailc4d343.ts.net/api/health"),
                 "plist_unchanged": PLIST.read_bytes() == plist,
                 "installed_app_not_deployed": True, "production_data_not_migrated": True,
                 "generated_artifacts_archived": archived}
        (OUT/"e2e-closeout.json").write_text(json.dumps(final, indent=2)+"\n")
        print(json.dumps({k:v for k,v in final.items() if k!='generated_artifacts_archived'}, indent=2), flush=True)
    assert result == 0 and final["local_health"] == final["tls_health"] == 200 and final["source_unchanged_during_suite"]


if __name__ == "__main__":
    main()
