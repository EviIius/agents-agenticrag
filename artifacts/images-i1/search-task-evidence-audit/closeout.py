"""Archive only regenerated test evidence; restore original bytes and verify health."""

import hashlib
import json
import subprocess
from pathlib import Path
from urllib.request import urlopen

import audit

ROOT, OUT = audit.ROOT, audit.OUT


def main():
    check = (OUT / "make-check.log").read_text()
    browser = (OUT / "make-e2e.log").read_text()
    assert "508 passed" in check and "39 passed" in check
    assert "473 passed" in browser and "3 skipped" in browser
    changes = subprocess.check_output(
        ["git", "diff", "--name-only", "cb5a1a4b", "--", "artifacts"],
        cwd=ROOT,
        text=True,
    ).splitlines()
    allowed = {".png", ".json"}
    retained = {}
    for name in changes:
        path = ROOT / name
        # Full browser/coverage suites overwrite their old generated evidence.
        # Retain fresh output, then restore the original tracked bytes.
        assert path.suffix in allowed and not name.startswith(
            (
                "artifacts/reliability/",
                "artifacts/model-comparison/",
                "artifacts/phase-8/",
            )
        ), name
        assert (
            path.suffix == ".png"
            or name == "artifacts/coverage.json"
            or path.name.startswith("axe-")
        ), name
        original = subprocess.check_output(
            ["git", "show", "cb5a1a4b:" + name], cwd=ROOT
        )
        destination = (
            OUT / "regenerated-test-evidence" / Path(name).relative_to("artifacts")
        )
        destination.parent.mkdir(parents=True, exist_ok=True)
        assert not destination.exists(), destination
        destination.write_bytes(path.read_bytes())
        retained[name] = {
            "fresh": str(destination.relative_to(ROOT)),
            "fresh_sha256": audit.sha(destination),
            "restored_sha256": hashlib.sha256(original).hexdigest(),
        }
        path.write_bytes(original)
        assert audit.sha(path) == retained[name]["restored_sha256"]
    preserved = audit.preserve_prior()
    product = subprocess.check_output(
        [
            "git",
            "diff",
            "--name-only",
            "cb5a1a4b",
            "--",
            "server",
            "web",
            "shared",
            "scripts",
            "image_worker",
            "transcribe",
        ],
        cwd=ROOT,
        text=True,
    ).splitlines()
    assert not product, product
    health = {}
    for address in (
        "http://127.0.0.1:8787/api/health",
        "https://jakes-mac-mini.tailc4d343.ts.net/api/health",
    ):
        with urlopen(address, timeout=15) as response:
            assert response.status == 200
            health[address] = response.status
    with urlopen("http://127.0.0.1:11434/api/version", timeout=15) as response:
        runtime = json.load(response)
    assert runtime["version"] == "0.35.0"
    check = (OUT / "make-check.log").read_text()
    browser = (OUT / "make-e2e.log").read_text()
    assert "508 passed" in check and "39 passed" in check
    assert "473 passed" in browser and "3 skipped" in browser
    audit.write(
        "closeout.json",
        {
            **preserved,
            "regenerated_evidence_preserved_and_originals_restored": retained,
            "product_diff": product,
            "health": health,
            "runtime": runtime,
            "native_calls": 0,
            "deployment": False,
            "research_image_workflow_calls": 0,
            "tests": {
                "audit": 29,
                "python": 508,
                "frontend": 39,
                "browser": 473,
                "browser_skips": 3,
            },
            "retained_failures": [
                "initial audit corpus-absence hypothesis",
                "initial lint preparation",
                "unchanged original baseline 24/25 and candidate 22/25",
            ],
        },
    )
    print(
        json.dumps(
            {
                **preserved,
                "restored_generated_files": len(retained),
                "healthy": True,
                "native_calls": 0,
            }
        )
    )


if __name__ == "__main__":
    main()
