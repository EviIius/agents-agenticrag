"""Read-only PE1 preparation checks; only health/version HTTP GETs."""

import hashlib
import json
import subprocess
from pathlib import Path

import httpx

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
MAIN = Path('/Users/evilius/Documents/GitHub/agents-agenticrag')
BASE = Path.home() / '.local/share/workbench'
NATIVE = ROOT / 'artifacts/photo-editing/native-20261019'
PRIVATE = BASE / 'qa/photo-editing-pe0-prep-20261019'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(root, files):
    assert all((root / name).is_file() and sha(root / name) == digest for name, digest in files.items())
    return {'count': len(files), 'preserved': True}


source = json.loads((ROOT / 'artifacts/production-followups/executed-source.json').read_text())['files']
static = json.loads((ROOT / 'artifacts/production-followups/build-manifest.json').read_text())['files']
native = json.loads((NATIVE / 'execution-manifest.json').read_text())['files']
launches = [json.loads(line) for line in (PRIVATE / 'worker-launches.jsonl').read_text().splitlines()]
assert [row['case'] for row in launches] == ['portrait', 'background', 'clothing', 'mug', 'cancel', 'recovery']
assert sha(PRIVATE / 'worker-launches.jsonl') == sha(NATIVE / 'worker-launches.jsonl')
result = {
    'production_source': verify(ROOT, source),
    'main_source': verify(MAIN, source),
    'installed_server': verify(BASE / 'app', {k: v for k, v in source.items() if k.startswith('server/app/')}),
    'installed_static': verify(BASE / 'app/server/app/static', static),
    'frozen_pe0_executed_source': verify(ROOT, native),
    'worker_invocations': len(launches),
    'main_commit': subprocess.check_output(['git', 'rev-parse', 'main'], cwd=MAIN, text=True).strip(),
    'new_native_calls': 0,
}
assert result['main_commit'] == 'c0d65ee02747f2834944fd6f60539b67b7d2f442'
result['prior_native_evidence'] = verify(NATIVE, json.loads((NATIVE / 'evidence-manifest.json').read_text())['files'])
with httpx.Client(timeout=5, trust_env=False) as client:
    for label, url in [('local', 'http://127.0.0.1:8787/api/health'), ('https', 'https://jakes-mac-mini.tailc4d343.ts.net/api/health')]:
        response = client.get(url)
        response.raise_for_status()
        assert response.json()['ok']
        result[label + '_health'] = True
    response = client.get('http://127.0.0.1:11434/api/version')
    response.raise_for_status()
    assert response.json() == {'version': '0.35.0'}
    result['ollama_version'] = response.json()['version']
(OUT / 'preservation.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
