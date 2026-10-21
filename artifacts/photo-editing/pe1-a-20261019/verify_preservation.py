"""Read-only release-boundary audit; no native calls or product-data writes."""

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


def read(path):
    return json.loads(path.read_text())


def verify(root, files):
    assert all((root / name).is_file() and sha(root / name) == digest for name, digest in files.items())
    return {'count': len(files), 'preserved': True}


source = read(ROOT / 'artifacts/production-followups/executed-source.json')['files']
static = read(ROOT / 'artifacts/production-followups/build-manifest.json')['files']
expected = read(OUT / 'executed-source.json')['files']
prep = read(ROOT / 'artifacts/photo-editing/prep-20261019/private-preparation.json')
launches = [json.loads(line) for line in (PRIVATE / 'worker-launches.jsonl').read_text().splitlines()]
assert len(launches) == 6
assert sha(PRIVATE / 'worker-launches.jsonl') == sha(NATIVE / 'worker-launches.jsonl')
result = {
    'candidate_source': verify(ROOT, expected),
    'main_source': verify(MAIN, source),
    'installed_server': verify(BASE / 'app', {k: v for k, v in source.items() if k.startswith('server/app/')}),
    'installed_static': verify(BASE / 'app/server/app/static', static),
    'frozen_pe0_source': verify(ROOT, read(NATIVE / 'execution-manifest.json')['files']),
    'frozen_pe0_evidence': verify(NATIVE, read(NATIVE / 'evidence-manifest.json')['files']),
    'private_pe0_worker': verify(PRIVATE / 'worker', prep['source_copies']),
    'worker_selectors': verify(BASE / 'image-worker/product', prep['existing_selectors']),
    'main_commit': subprocess.check_output(['git', 'rev-parse', 'main'], cwd=MAIN, text=True).strip(),
    'native_worker_invocations': 6, 'new_native_calls': 0,
    'generation_worker_unchanged': sha(ROOT / 'image_worker/product/worker.py') == sha(BASE / 'image-worker/product/worker.py'),
}
assert result['generation_worker_unchanged']
assert result['main_commit'] == 'c0d65ee02747f2834944fd6f60539b67b7d2f442'
prior = read(ROOT / 'artifacts/production-followups/preservation-final.json')['stopped_trial_ledgers']
for name, relative in [('Hermes', 'hermes-h0-20261017/native-2'), ('PydanticAI', 'pydantic-p0-20261018/native'), ('N1', 'native-agent-n1-20261018'), ('C1', 'native-agent-c1-20261018')]:
    assert sha(BASE / 'qa' / relative / 'ledger.json') == prior[name]['sha256']
result['stopped_trial_ledgers'] = prior
with httpx.Client(timeout=5, trust_env=False) as client:
    for label, url in [('local', 'http://127.0.0.1:8787/api/health'), ('https', 'https://jakes-mac-mini.tailc4d343.ts.net/api/health')]:
        response = client.get(url)
        response.raise_for_status()
        assert response.json()['ok']
        result[label + '_health'] = True
    version = client.get('http://127.0.0.1:11434/api/version')
    version.raise_for_status()
    assert version.json() == {'version': '0.35.0'}
    result['ollama_version'] = '0.35.0'
(OUT / 'preservation.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
