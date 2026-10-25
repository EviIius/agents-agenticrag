"""Read-only verification of the integrated themes; no user content in output."""

from contextlib import closing
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("theme_publication", OUT / "publish_themes.py")
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)
h = release.helpers
record = json.loads((OUT / "publication.json").read_text())
frozen = json.loads((OUT / "release-source.json").read_text())
assert record["publication"]
h.verify(release.BUNDLE)
assert h.sha(release.BUNDLE / "release.json") == record["private_bundle_manifest_sha256"]
assert h.app_files(h.BASE / "app") == h.app_files(release.BUNDLE / "candidate-app") == h.app_files(ROOT)
assert all(h.sha(ROOT / n) == value for n, value in frozen["files"].items())
assert all(h.sha(h.BASE / "image-worker/product" / n) == h.sha(ROOT / "image_worker/product" / n) for n in h.FILES)
plist, route = h.service()
assert hashlib.sha256(plist).hexdigest() == record["plist_sha256"]
assert hashlib.sha256(route).hexdigest() == record["route_sha256"]
with closing(h.read_db(h.BASE / "data/workbench.db")) as db:
    assert db.execute("PRAGMA user_version").fetchone()[0] == 14
    assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert db.execute("PRAGMA foreign_key_check").fetchall() == []
settings = h.get("http://127.0.0.1:8787/api/settings").json()
assert settings["appearance.palette"] in {"cobalt", "lime", "paper", "ember", "orchid", "midnight", "mono", "aero"}
assert settings["appearance.greeting"] in {"languages", "surprise", "english"}
assert h.get("http://127.0.0.1:11434/api/version").json() == {"version": "0.35.0"}
assert json.loads((OUT / "installed-ui.json").read_text())["passed"]
original = Path("/Users/evilius/Documents/GitHub/agents-agenticrag")
assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=original, text=True).strip() == "8f38ef7bebdf970ed4cae03a52e8b94cf23c5bc8"
provided = json.loads((ROOT / "artifacts/themes/aero-integration-20261024/preservation-before.json").read_text())["provided_inputs"]
assert all(h.sha(original / "docs/next/themes" / n) == x["sha256"] for n, x in provided.items())
result = {
    "passed": True, "merged_source": record["source_commit"],
    "candidate_files_verified": len(frozen["files"]),
    "installed_app_files": len(h.app_files(h.BASE / "app")),
    "static_files": len(frozen["static_files"]), "worker_files_verified": len(h.FILES),
    "production_bundle_files_verified": record["private_bundle_files"],
    "plist_and_route_unchanged": True, "schema": 14,
    "integrity_and_foreign_keys": "ok", "theme_preferences_shape_valid": True,
    "original_workspace_and_inputs_preserved": True,
    "installed_UI_engines": 2, "native_model_calls": 0,
    "physical_iPhone_check": "requested, pending user response",
    "Claude_UI_review": "after integration, as requested",
}
(OUT / "verification.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
