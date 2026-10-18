"""Offline C1 evidence/preservation audit. Metadata GETs only; no inference."""
import hashlib
import fcntl
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'server'))
import httpx
from experiments.native_c1.controller import Ledger, Refused

OUT = ROOT / 'artifacts/agent-loop/c1'
BASE = Path.home() / '.local/share/workbench'
QA = BASE / 'qa/native-agent-c1-20261018'
MAIN = Path('/Users/evilius/Documents/GitHub/agents-agenticrag')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify(root, files):
    bad = [name for name, digest in files.items() if not (root/name).is_file() or sha(root/name) != digest]
    assert not bad, bad
    return {'count': len(files), 'preserved': True}

frozen = json.loads((OUT/'frozen.json').read_text())
result = json.loads((OUT/'S1-H01/result.json').read_text())
requests = json.loads((OUT/'S1-H01/requests.json').read_text())
raw = [json.loads(line) for line in (OUT/'S1-H01/upstream-01.ndjson').read_text().splitlines()]
assert ''.join(row.get('message',{}).get('content','') for row in raw) == result['message']['content']
assert raw[-1]['done'] and len(requests) == 1
assert requests[0]['body']['messages'][0]['content'] == frozen['wire_systems']['web']
assert requests[0]['body']['messages'][1]['content'] == result['original_case']['question']
assert [t['function']['name'] for t in requests[0]['body']['tools']] == ['web_search','read_page','calculate']
prior = json.loads((ROOT/'artifacts/agent-loop/n1/S1-H01/requests.json').read_text())[0]['body']
current = requests[0]['body']
assert {k:v for k,v in prior.items() if k!='messages'} == {k:v for k,v in current.items() if k!='messages'}
assert prior['messages'][1:] == current['messages'][1:]
ledger = Ledger(QA/'ledger.json')
state = json.loads(ledger.path.read_text())
assert state['calls'] == 1 and state['stopped'] and state['active'] is None
assert set(state['tasks']) == {'S1-H01'}
for action in (lambda: ledger.begin('S1-H02'), lambda: ledger.admit('S1-H01')):
    try:
        action()
        raise AssertionError('Post-stop action was allowed')
    except Refused:
        pass
assert json.loads(ledger.path.read_text()) == state
assert (OUT/'ledger-latest.json').read_bytes() == ledger.path.read_bytes()

source = json.loads((ROOT/'artifacts/image-memory-recovery/executed-source.json').read_text())['files']
static = json.loads((ROOT/'artifacts/image-memory-recovery/build-manifest.json').read_text())['files']
old_coverage = json.loads((ROOT/'artifacts/agent-loop/coverage-v1/preservation-final.json').read_text())
old_n1 = BASE/'qa/native-agent-n1-20261018/ledger.json'
assert sha(old_n1) == frozen['old_N1_ledger_sha256']
ledgers = {}
for name, path in {
    'Hermes': BASE/'qa/hermes-h0-20261017/native-2/ledger.json',
    'PydanticAI': BASE/'qa/pydantic-p0-20261018/native/ledger.json',
    'N1': old_n1,
}.items():
    key = {'Hermes':'hermes','PydanticAI':'pydantic'}.get(name)
    expected = old_coverage['old_ledgers'][key]['sha256'] if key else frozen['old_N1_ledger_sha256']
    assert sha(path) == expected
    ledgers[name] = {'sha256':expected,'preserved':True,'calls':json.loads(path.read_text())['calls']}

before = frozen['admission']['swap_baseline_mib']
samples = result['samples']
with (BASE/'data/native.lock').open('a+') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    fcntl.flock(lock, fcntl.LOCK_UN)

wire = {
    'native_calls':1, 'remaining_tasks_unrun':11, 'stopped':state['stopped'],
    'manual_passes':0, 'attempted_tasks':1, 'raw_text_equals_persisted_text':True,
    'wire_candidate_exact':True, 'other_wire_fields_equal_N1':True,
    'source_records_retrieved':0, 'tool_calls':0,
    'coverage_status':result['coverage']['status'],
    'seconds':result['seconds'], 'sample_count':len(samples),
    'swap_baseline_mib':before, 'max_swap_growth_mib':max(s['swap_mib']-before for s in samples),
    'max_model_bytes':max(sum(m.get('size_vram') or 0 for m in s['models']) for s in samples),
    'max_health_ms':max(s['health_ms'] for s in samples),
    'prompt_eval_count':raw[-1]['prompt_eval_count'],
    'post_stop_begin_and_admit_refused':True, 'shared_native_capacity_released':True,
    'answer_gain_established':False, 'qualified':False,
}
(OUT/'summary.json').write_text(json.dumps(wire,indent=2)+'\n')
preservation = {
    'frozen_executed_source':verify(ROOT, frozen['files']),
    'old_N1_source':verify(ROOT, json.loads((ROOT/'artifacts/agent-loop/n1/frozen.json').read_text())['files']),
    'main_source':verify(MAIN,source),
    'installed_server':verify(BASE/'app',{k:v for k,v in source.items() if k.startswith('server/app/')}),
    'installed_static':verify(BASE/'app/server/app/static',static),
    'main_commit':subprocess.check_output(['git','rev-parse','main'],cwd=MAIN,text=True).strip(),
    'old_ledgers':ledgers,
    'C1_ledger_sha256':sha(ledger.path),
    'dependencies':old_coverage['dependencies'],
}
for name,digest in preservation['dependencies'].items():
    assert sha(ROOT/name) == digest
with httpx.Client(timeout=5,trust_env=False) as client:
    for name,url in [('local_health','http://127.0.0.1:8787/api/health'),('https_health','https://jakes-mac-mini.tailc4d343.ts.net/api/health')]:
        response=client.get(url);response.raise_for_status();preservation[name]=response.json();assert response.json()['ok']
(OUT/'preservation-final.json').write_text(json.dumps(preservation,indent=2)+'\n')

data=OUT/'S1-H01/data'
if data.exists():
    archive=QA/'synthetic-databases/S1-H01'
    assert not archive.exists()
    shutil.copytree(data,archive)
    files={str(p.relative_to(data)):sha(p) for p in data.rglob('*') if p.is_file()}
    verify(archive,files)
    (OUT/'synthetic-data-archive.json').write_text(json.dumps({'location':'private C1 QA/synthetic-databases/S1-H01','files':files},indent=2)+'\n')
    shutil.rmtree(data)
print(json.dumps(wire,indent=2))
