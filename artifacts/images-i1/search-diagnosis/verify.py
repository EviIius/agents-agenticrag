"""Read-only closeout: frozen source, retained reports and earlier evidence bytes."""

import hashlib
import json
import subprocess
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = json.loads((OUT / "manifest.json").read_text())
    baseline = ROOT / "tmp/images-i1/search-diagnosis/baseline"
    for folder, name in ((ROOT, "files"), (baseline, "baseline_files")):
        for path, expected in manifest[name].items():
            assert sha(folder / path) == expected, path
    ordered = json.loads((OUT / "ordered-results.json").read_text())
    assert len(ordered["runs"]) == len(ordered["declared_order"]) == 8
    for expected, run in zip(ordered["declared_order"], ordered["runs"], strict=True):
        assert expected == [run["label"], run["arm"], run["focused"]]
        assert sha(ROOT / run["report"]) == run["report_sha256"]
        assert run["exit_code"] == 1
    assert subprocess.check_output(
        ["git", "rev-parse", "--show-object-format"], cwd=ROOT, text=True
    ).strip() == "sha1"
    tree = subprocess.check_output([
        "git", "ls-tree", "-r", "-z", "897056f", "--", "artifacts", "server/evals/web/reports"
    ], cwd=ROOT)
    previous = 0
    for row in tree.split(b"\0"):
        if not row:
            continue
        head, name = row.split(b"\t", 1)
        mode, kind, expected = head.split()
        assert mode in (b"100644", b"100755") and kind == b"blob", name
        data = (ROOT / name.decode()).read_bytes()
        digest = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        assert digest == expected.decode(), name
        previous += 1
    production_diff = subprocess.check_output([
        "git", "diff", "--name-only", "897056f", "--", "server/app", "web/src",
        "shared", "image_worker", "transcribe", "scripts/deploy.py"
    ], cwd=ROOT, text=True).splitlines()
    assert not production_diff, production_diff
    health = {}
    for label, url in (
        ("local", "http://127.0.0.1:8787/api/health"),
        ("normally_verified_https", "https://jakes-mac-mini.tailc4d343.ts.net/api/health"),
    ):
        status = subprocess.check_output([
            "curl", "--silent", "--show-error", "--fail", "--max-time", "15",
            "--noproxy", "*", "--output", "/dev/null", "--write-out", "%{http_code}", url
        ], text=True)
        health[label] = status == "200"
        assert health[label]
    with urlopen("http://127.0.0.1:11434/api/version", timeout=10) as response:
        runtime = json.load(response)
    assert runtime["version"] == "0.35.0"
    result = {
        "frozen_candidate_harness_cases_corpus_files_verified": len(manifest["files"]),
        "accepted_package_files_verified": len(manifest["baseline_files"]),
        "declared_native_runs_completed": len(ordered["runs"]),
        "all_native_reports_remain_failed": True,
        "earlier_tracked_evidence_files_byte_preserved": previous,
        "production_source_changes_this_diagnosis": production_diff,
        "health": health,
        "health_tls_verification": "curl default certificate verification; no insecure flag or trust change",
        "runtime": runtime,
        "no_release_or_service_restart": True,
        "limits": "Checks compare frozen files and retained reports; no production data or private recording text inspected."
    }
    (OUT / "verification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
