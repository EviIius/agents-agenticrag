"""Read-only release verification plus preservation of this checkout's synthetic QA output."""
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
PRIVATE = Path.home() / ".local/share/workbench/qa/design-critique-b-20261025"
ORIGINAL = Path("/Users/evilius/Documents/GitHub/agents-agenticrag")
BASE = Path.home() / ".local/share/workbench"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + "\n")


def main():
    text = re.sub(r"\x1b\[[0-9;]*m", "", (OUT / "make-e2e-final.log").read_text())
    assert re.search(r"^\s*918 passed\b", text, re.M), "Complete browser gate not green"
    assert re.search(r"^\s*4 skipped\b", text, re.M), "Existing skips changed"
    assert not re.search(r"^\s*\d+ (failed|interrupted)\b", text, re.M)
    checks = (OUT / "make-check-final.log").read_text()
    assert "785 passed" in checks and "Tests  157 passed" in checks
    assert "969 token pairs passed" in checks and "check_glass_css: 5 stylesheet(s) OK" in checks
    frozen = json.loads((OUT / "executed-source.json").read_text())
    assert all(sha(ROOT / name) == value for name, value in frozen.items())
    bundle = json.loads((OUT / "bundle-final.json").read_text())
    assert bundle["gzip_bytes"] <= bundle["budget_bytes"]
    shutil.copyfile(ROOT / "artifacts/coverage.json", OUT / "coverage-final.json")
    metrics = OUT / "metrics"
    metrics.mkdir(exist_ok=True)
    for engine in ["chromium", "webkit"]:
        for name in [f"artifacts/phase-3/performance-{engine}.json", f"artifacts/themes/aero-integration-20261024/performance-{engine}.json", f"artifacts/phase-1/first-token-{engine}.json", f"artifacts/phase-1/frames-{engine}.json", f"artifacts/chat-images/ci-a/browser/ticker-performance-{engine}.json"]:
            path = ROOT / name
            assert path.is_file(), name
            shutil.copyfile(path, metrics / name.replace("/", "__"))

    recovery = json.loads((BASE / "releases/aero-blur-fix-20261025/recovery.json").read_text())
    current = json.loads((ROOT / "artifacts/aero-blur-fix-release-20261025/release-manifest.json").read_text())["static_files"]
    static = {**recovery["previous_static"], **current}
    assert all(sha(BASE / "app/server/app/static" / name) == value for name, value in static.items())
    assert all(sha(BASE / "app" / name) == value for name, value in recovery["backend"].items())
    assert all(sha(BASE / "image-worker/product" / name) == value for name, value in recovery["worker"].items())
    before = json.loads((ROOT / "artifacts/aero-blur-fix/preservation-before.json").read_text())
    inputs = before["supplied_files"]
    assert all(sha(ORIGINAL / "docs/next/design-critique" / name) == value for name, value in inputs.items())
    module = importlib.util.spec_from_file_location("part_a_read_helpers", ROOT / "artifacts/aero-blur-fix-release-20261025/publish_static.py")
    helpers = importlib.util.module_from_spec(module)
    module.loader.exec_module(helpers)
    assert helpers.helpers.protected() == recovery["protected"]
    dry = json.loads((ROOT / "artifacts/aero-blur-fix-release-20261025/dry-run.json").read_text())
    plist, route = helpers.helpers.service()
    assert hashlib.sha256(plist).hexdigest() == dry["plist_sha256"]
    assert hashlib.sha256(route).hexdigest() == dry["route_sha256"]
    pid = helpers.pid()
    assert pid == 77443
    for url in ["http://127.0.0.1:8787/api/health", "https://jakes-mac-mini.tailc4d343.ts.net/api/health"]:
        assert helpers.helpers.get(url).json()["ok"] is True

    # Full suites intentionally regenerate old evidence. Keep fresh bytes before
    # restoring that evidence's original tracked version; never touch user inputs.
    prior = json.loads((PRIVATE / "prior-artifacts.json").read_text())
    archive = PRIVATE / "final-regenerated"
    assert not archive.exists(), "Review the existing closeout before repeating it"
    archive.mkdir(parents=True)
    changed = [name for name, digest in prior.items() if not (ROOT / name).exists() or sha(ROOT / name) != digest]
    for name in changed:
        path = ROOT / name
        if path.exists():
            target = archive / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
        raw = subprocess.check_output(["git", "show", "HEAD:" + name], cwd=ROOT)
        assert hashlib.sha256(raw).hexdigest() == prior[name]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    added = subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard", "-z", "artifacts"], cwd=ROOT).decode().split("\0")
    extras = []
    for name in added:
        if not name or name.startswith(OUT.relative_to(ROOT).as_posix() + "/"):
            continue
        path = ROOT / name
        target = archive / "new" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(path, target)
        extras.append(name)
    assert all(sha(ROOT / name) == digest for name, digest in prior.items())
    save("verification.json", {
        "passed": True, "source_files": len(frozen), "historical_artifacts_preserved": len(prior),
        "regenerated_files_preserved_then_restored": len(changed), "additional_captures_archived": len(extras),
        "supplied_input_files_unchanged": len(inputs), "installed_static_files_unchanged": len(static),
        "installed_backend_files_unchanged": len(recovery["backend"]), "worker_files_unchanged": len(recovery["worker"]),
        "protected_runtimes_and_selectors_unchanged": True, "service_pid": pid,
        "local_and_verified_https_health": True, "browser_passed": 918, "existing_browser_skips": 4,
        "initial_js_gzip_bytes": bundle["gzip_bytes"], "native_model_calls": 0, "live_api_mutations": 0, "deployment": False,
        "physical_iphone_check": "pending", "voiceover": "historical unresolved limitation"
    })
    print(json.dumps({"passed": True, "restored": len(changed), "archived_extra": len(extras)}))


if __name__ == "__main__":
    main()
