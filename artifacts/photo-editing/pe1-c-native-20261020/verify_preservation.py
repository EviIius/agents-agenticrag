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
expected = read(ROOT / 'artifacts/photo-editing/pe1-b-20261020/executed-source.json')['files']
prep = read(ROOT / 'artifacts/photo-editing/prep-20261019/private-preparation.json')
launches = [json.loads(line) for line in (PRIVATE / 'worker-launches.jsonl').read_text().splitlines()]
assert len(launches) == 6
assert sha(PRIVATE / 'worker-launches.jsonl') == sha(NATIVE / 'worker-launches.jsonl')
result = {
    'candidate_source': verify(ROOT, expected),
    'unchanged_B_evidence': verify(ROOT, {k: v for k, v in read(ROOT / 'artifacts/photo-editing/pe1-b-20261020/evidence-manifest.json')['files'].items() if k != 'AGENTS.md'}),
    'candidate_static': verify(ROOT / 'server/app/static', read(ROOT / 'artifacts/photo-editing/pe1-b-20261020/build-manifest.json')['files']),
    'approved_PE1C_image_invocations': 4,
    'approved_empty_message_preloads': 1,
    'frozen_C_preparation': verify(ROOT, read(ROOT / 'artifacts/photo-editing/pe1-c-prep-20261020/evidence-manifest.json')['files']),
    'executed_C_source': verify(ROOT, read(OUT / 'executed-source.json')['files']),
    'main_source': verify(MAIN, source),
    'installed_server': verify(BASE / 'app', {k: v for k, v in source.items() if k.startswith('server/app/')}),
    'installed_static': verify(BASE / 'app/server/app/static', static),
    'frozen_pe0_source': verify(ROOT, read(NATIVE / 'execution-manifest.json')['files']),
    'frozen_pe0_evidence': verify(NATIVE, read(NATIVE / 'evidence-manifest.json')['files']),
    'private_pe0_worker': verify(PRIVATE / 'worker', prep['source_copies']),
    'worker_selectors': verify(BASE / 'image-worker/product', prep['existing_selectors']),
    'main_commit': subprocess.check_output(['git', 'rev-parse', 'main'], cwd=MAIN, text=True).strip(),
    'frozen_pe0_worker_invocations': 6,
    'separate_private_user_edit_invocations': 1,
    'generation_worker_unchanged': sha(ROOT / 'image_worker/product/worker.py') == sha(BASE / 'image-worker/product/worker.py'),
}
# The separately authorized real-photo test is private. Publish counts only, no
# source/output paths, names, hashes, prompt, pixels or private ledger contents.
private_edit = BASE / 'qa/photo-hat-private-20261020'
assert (private_edit / 'attempt.json').is_file()
assert read(private_edit / 'result.json')['completed']
assert read(private_edit / 'result.json')['new_native_invocations'] == 1
assert read(private_edit / 'result.json')['original_preserved']
assert read(private_edit / 'approval.json')['maximum_native_invocations'] == 1
assert result['generation_worker_unchanged']
assert result['main_commit'] == 'c0d65ee02747f2834944fd6f60539b67b7d2f442'
assert hashlib.sha256(subprocess.check_output(['git', 'show', 'a6163e17:AGENTS.md'], cwd=ROOT)).hexdigest() == read(ROOT / 'artifacts/photo-editing/pe1-b-20261020/evidence-manifest.json')['files']['AGENTS.md']
result['B_prior_AGENTS_preserved_in_commit'] = 'a6163e17'
prior = read(ROOT / 'artifacts/production-followups/preservation-final.json')['stopped_trial_ledgers']
for name, relative in [('Hermes', 'hermes-h0-20261017/native-2'), ('PydanticAI', 'pydantic-p0-20261018/native'), ('N1', 'native-agent-n1-20261018'), ('C1', 'native-agent-c1-20261018')]:
    assert sha(BASE / 'qa' / relative / 'ledger.json') == prior[name]['sha256']
result['stopped_trial_ledgers'] = prior
native = BASE / 'qa/photo-editing-pe1-c-prep-20261020/native'
rows = [json.loads(line) for line in (native / 'launches.jsonl').read_text().splitlines()]
assert [(r['kind'], r['case']) for r in rows] == [('image','empty-heic'),('preload','resident-setup'),('image','resident-jpeg'),('image','cancel'),('image','recovery-heic')]
assert read(native / 'summary.json')['passed'] and not (native / 'HALTED').exists()
assert len(read(native / 'summary.json')['reaping']) == 4
assert all(all(row.values()) for row in read(native / 'summary.json')['reaping'])
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
