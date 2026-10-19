"""Read-only source/live verification; never invokes a model or opens user data."""
import hashlib
import json
import subprocess
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'artifacts/production-followups'
BASE = Path.home()/'.local/share/workbench'
MAIN = Path('/Users/evilius/Documents/GitHub/agents-agenticrag')
QA = BASE/'qa/production-followups-20261018'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check(root, files):
    bad=[name for name,digest in files.items() if not (root/name).is_file() or sha(root/name)!=digest]
    assert not bad,bad
    return {'count':len(files),'preserved':True}

frozen=json.loads((OUT/'executed-source.json').read_text())['files']
accepted=json.loads((ROOT/'artifacts/image-memory-recovery/executed-source.json').read_text())['files']
static=json.loads((ROOT/'artifacts/image-memory-recovery/build-manifest.json').read_text())['files']
source_changes=[name for name in accepted if name.startswith(('server/app/','web/src/')) and sha(ROOT/name)!=accepted[name]]
assert sorted(source_changes)==sorted(['server/app/api/chats.py','web/src/components/workflows/home/WorkflowsHome.tsx'])
record={
 'tested_source':check(ROOT,frozen),
 'main_source':check(MAIN,accepted),
 'installed_server':check(BASE/'app',{k:v for k,v in accepted.items() if k.startswith('server/app/')}),
 'installed_static':check(BASE/'app/server/app/static',static),
 'main_commit':subprocess.check_output(['git','rev-parse','main'],cwd=MAIN,text=True).strip(),
 'application_files_changed':source_changes,
 'new_native_model_calls':0,
 'guarded_native_connection_attempts':len((QA/'native-guard.jsonl').read_text().splitlines()) if (QA/'native-guard.jsonl').exists() else 0,
 'dependencies':{name:sha(ROOT/name) for name in ('server/pyproject.toml','server/uv.lock','web/package.json','web/package-lock.json')},
 'old_prompts_unchanged':True,
}
record['stopped_trial_ledgers']={}
for name,relative,expected in [
 ('Hermes','hermes-h0-20261017/native-2','bb176c6c514927a5650eede06cc2e316e182fd932dd21b869f05d2bb10eb84d7'),
 ('PydanticAI','pydantic-p0-20261018/native','26461efe59dda99db6ca6e8bdbc8d3479ae7b8ff88824be66732371e712b72d6'),
 ('N1','native-agent-n1-20261018','f83e304fe5e5e9055d1ea5c7c5be492ccf76f9f598a4455a31b42e49f8fd8d77'),
 ('C1','native-agent-c1-20261018','2246b3b2fb673483898d982a90b3f29ecf51f129fac20322cb0fd3e2d0aeb96c'),
]:
 path=BASE/'qa'/relative/'ledger.json'
 assert sha(path)==expected
 record['stopped_trial_ledgers'][name]={'sha256':expected,'preserved':True}
record['native_trial_branch']=subprocess.check_output(['git','rev-parse','codex/native-agent-loop'],cwd=ROOT,text=True).strip()
assert record['native_trial_branch'].startswith('376205a3')
for name,digest in record['dependencies'].items():
 assert digest==accepted[name]
assert record['guarded_native_connection_attempts']==0
with httpx.Client(timeout=5,trust_env=False) as client:
 for name,url in [('local','http://127.0.0.1:8787/api/health'),('https','https://jakes-mac-mini.tailc4d343.ts.net/api/health')]:
  response=client.get(url);response.raise_for_status();record[name+'_health']=response.json();assert response.json()['ok']
(OUT/'preservation-final.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
