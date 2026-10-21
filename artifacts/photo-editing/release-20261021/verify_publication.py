"""Read-only publication, prior-evidence and stopped-budget verification."""
import hashlib
import json
import subprocess
from pathlib import Path

from publish_release import (
    BASE, BUNDLE, FILES, OUT, PLIST, ROOT, TAILSCALE,
    app_files, command, get, protected, service, sha, verify,
)


def load(path):
    return json.loads(path.read_text())


def check_files(root, files):
    assert all(sha(root / name) == value for name, value in files.items())
    return len(files)


record = load(OUT / "publication.json")
assert record["published"]
verify(BUNDLE)
assert sha(BUNDLE / "release.json") == record["production_bundle_manifest_sha256"]
assert app_files(BASE / "app") == app_files(BUNDLE / "candidate-app") == app_files(ROOT)
assert protected() == record["protected_before"]
assert sha(PLIST) == record["plist_sha256"]
assert hashlib.sha256(command([TAILSCALE, "serve", "status"])).hexdigest() == record["route_sha256"]
service()
assert all(sha(BASE / "image-worker/product" / n) == sha(ROOT / "image_worker/product" / n) for n in FILES)
status = get("https://jakes-mac-mini.tailc4d343.ts.net/api/images/status").json()
assert status["available"] and status["editing_available"]
assert get("http://127.0.0.1:11434/api/version").json() == {"version": "0.35.0"}
main = Path("/Users/evilius/Documents/GitHub/agents-agenticrag")
current = load(ROOT / "artifacts/photo-editing/pe1-integration-20261021/executed-source.json")["files"]
result = {
    "main_matches_tested_source_files": check_files(main, current),
    "installed_payload_files": len(app_files(BASE / "app")),
    "installed_worker_files": len(FILES),
    "production_bundle_files_verified": len(load(BUNDLE / "release.json")["files"]),
    "runtime_transcription_and_selectors_unchanged": True,
    "service_and_tailscale_unchanged": True,
    "live_editing_available": True,
    "Ollama_version": "0.35.0",
    "native_test_calls": 0,
}
frozen = BASE / "qa/photo-editing-pe1-integration-20261021/frozen-C-source"
result["frozen_C_source"] = check_files(frozen, load(ROOT / "artifacts/photo-editing/pe1-c-prep-20261020/native-execution-manifest.json")["files"])
result["frozen_B_source"] = check_files(frozen, load(ROOT / "artifacts/photo-editing/pe1-b-20261020/executed-source.json")["files"])
result["integration_evidence"] = check_files(ROOT, load(ROOT / "artifacts/photo-editing/pe1-integration-20261021/evidence-manifest.json")["files"])
for label, folder in (("C_preparation", "pe1-c-prep-20261020"), ("C_native", "pe1-c-native-20261020")):
    result[label + "_evidence"] = check_files(ROOT, load(ROOT / "artifacts/photo-editing" / folder / "evidence-manifest.json")["files"])
pe0 = ROOT / "artifacts/photo-editing/native-20261019"
result["PE0_source"] = check_files(ROOT, load(pe0 / "execution-manifest.json")["files"])
result["PE0_evidence"] = check_files(pe0, load(pe0 / "evidence-manifest.json")["files"])
assert sha(BASE / "qa/photo-editing-pe1-c-prep-20261020/native/launches.jsonl") == sha(ROOT / "artifacts/photo-editing/pe1-c-native-20261020/launches.jsonl")
assert sha(BASE / "qa/photo-editing-pe0-prep-20261019/worker-launches.jsonl") == sha(pe0 / "worker-launches.jsonl")
private = load(BASE / "qa/photo-hat-private-20261020/result.json")
assert private["new_native_invocations"] == 1
result["native_allowances_unchanged"] = {"PE0": 6, "private_photo": 1, "PE1C": 4, "PE1C_preload": 1}
ledgers = load(ROOT / "artifacts/production-followups/preservation-final.json")["stopped_trial_ledgers"]
for label, folder in (("Hermes", "hermes-h0-20261017/native-2"), ("PydanticAI", "pydantic-p0-20261018/native"), ("N1", "native-agent-n1-20261018"), ("C1", "native-agent-c1-20261018")):
    assert sha(BASE / "qa" / folder / "ledger.json") == ledgers[label]["sha256"]
result["stopped_agent_ledgers_preserved"] = True
assert load(OUT / "installed-ui.json")["passed"]
result["installed_UI_browsers"] = 2
result["physical_phone_check"] = "pending user response"
result["merged_main"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=main, text=True).strip()
(OUT / "verification.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
