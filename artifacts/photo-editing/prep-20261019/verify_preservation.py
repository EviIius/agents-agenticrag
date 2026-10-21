"""Read-only PE0 preservation check. Health endpoints only, no model operations."""
import hashlib
import json
import subprocess
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent
MAIN = Path('/Users/evilius/Documents/GitHub/agents-agenticrag')
BASE = Path.home()/'.local/share/workbench'
QA = BASE/'qa/photo-editing-pe0-prep-20261019'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def verify(root, files):
    assert all((root/name).is_file() and sha(root/name)==digest for name,digest in files.items())
    return {'count':len(files),'preserved':True}


frozen=json.loads((ROOT/'artifacts/production-followups/executed-source.json').read_text())['files']
static=json.loads((ROOT/'artifacts/production-followups/build-manifest.json').read_text())['files']
result={
 'production_source':verify(ROOT,frozen),
 'main_source':verify(MAIN,frozen),
 'installed_server':verify(BASE/'app',{k:v for k,v in frozen.items() if k.startswith('server/app/')}),
 'installed_static':verify(BASE/'app/server/app/static',static),
 'main_commit':subprocess.check_output(['git','rev-parse','main'],cwd=MAIN,text=True).strip(),
 'native_calls':0,
 'blocked_native_attempts':len((QA/'native-guard.jsonl').read_text().splitlines()) if (QA/'native-guard.jsonl').exists() else 0,
 'native_approval_exists':(QA/'approval.json').exists(),
 'product_worker_unchanged':sha(ROOT/'image_worker/product/worker.py')==sha(BASE/'image-worker/product/worker.py'),
}
assert result['product_worker_unchanged'] and not result['native_approval_exists'] and result['blocked_native_attempts']==0
result['stopped_trial_ledgers']={}
prior=json.loads((ROOT/'artifacts/production-followups/preservation-final.json').read_text())['stopped_trial_ledgers']
for name,relative in [('Hermes','hermes-h0-20261017/native-2'),('PydanticAI','pydantic-p0-20261018/native'),('N1','native-agent-n1-20261018'),('C1','native-agent-c1-20261018')]:
 assert sha(BASE/'qa'/relative/'ledger.json')==prior[name]['sha256']
 result['stopped_trial_ledgers'][name]=prior[name]
assert subprocess.check_output(['git','rev-parse','codex/native-agent-loop'],cwd=ROOT,text=True).strip().startswith('376205a3')
with httpx.Client(timeout=5,trust_env=False) as client:
 for name,url in [('local','http://127.0.0.1:8787/api/health'),('https','https://jakes-mac-mini.tailc4d343.ts.net/api/health')]:
  response=client.get(url);response.raise_for_status();assert response.json()['ok'];result[name+'_health']=True
(OUT/'preservation-final.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
