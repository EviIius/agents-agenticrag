"""Post-suite audit. Does not modify production, budgets or frozen trial evidence."""
import hashlib
import json
import subprocess
from pathlib import Path
import httpx

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
BASE=Path.home()/'.local/share/workbench'
MAIN=Path('/Users/evilius/Documents/GitHub/agents-agenticrag')
FROZEN=BASE/'qa/photo-editing-pe1-integration-20261021/frozen-C-source'

def read(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def verify(root,files):
 for name,digest in files.items():assert sha(root/name)==digest,name
 return {'count':len(files),'preserved':True}

prior=read(ROOT/'artifacts/photo-editing/pe1-c-prep-20261020/native-execution-manifest.json')['files']
allowed={'server/app/images/engine.py','server/tests/test_photo_references.py','scripts/install_image_worker.py','scripts/deploy.py'}
changed={name for name,digest in prior.items() if sha(ROOT/name)!=digest}
assert changed==allowed.intersection(prior),changed
source=read(ROOT/'artifacts/production-followups/executed-source.json')['files']
B=read(ROOT/'artifacts/photo-editing/pe1-b-20261020/evidence-manifest.json')['files']
original_agents=subprocess.check_output(['git','show','a6163e17:AGENTS.md'],cwd=ROOT)
assert hashlib.sha256(original_agents).hexdigest()==B['AGENTS.md']
result={
 'current_source':verify(ROOT,read(OUT/'executed-source.json')['files']),
 'frozen_executed_C_source':verify(FROZEN,prior),
 'only_authorized_existing_source_deltas':sorted(changed),
 'B_source_preserved':verify(FROZEN,read(ROOT/'artifacts/photo-editing/pe1-b-20261020/executed-source.json')['files']),
 'B_evidence':verify(ROOT,{k:v for k,v in B.items() if k!='AGENTS.md' and k not in allowed}),
 'C_preparation_evidence':verify(ROOT,read(ROOT/'artifacts/photo-editing/pe1-c-prep-20261020/evidence-manifest.json')['files']),
 'C_native_evidence':verify(ROOT,read(ROOT/'artifacts/photo-editing/pe1-c-native-20261020/evidence-manifest.json')['files']),
 'main_source':verify(MAIN,source),
 'installed_server':verify(BASE/'app',{k:v for k,v in source.items() if k.startswith('server/app/')}),
 'installed_static':verify(BASE/'app/server/app/static',read(ROOT/'artifacts/production-followups/build-manifest.json')['files']),
 'candidate_static_unchanged':verify(ROOT/'server/app/static',read(ROOT/'artifacts/photo-editing/pe1-b-20261020/build-manifest.json')['files']),
 'PE0_source':verify(ROOT,read(ROOT/'artifacts/photo-editing/native-20261019/execution-manifest.json')['files']),
 'PE0_evidence':verify(ROOT/'artifacts/photo-editing/native-20261019',read(ROOT/'artifacts/photo-editing/native-20261019/evidence-manifest.json')['files']),
 'main_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=MAIN,text=True).strip(),
 'native_calls_this_checkpoint':0,
}
assert result['main_commit']=='c0d65ee02747f2834944fd6f60539b67b7d2f442'
prep=read(ROOT/'artifacts/photo-editing/prep-20261019/private-preparation.json')
result['installed_worker_selectors']=verify(BASE/'image-worker/product',prep['existing_selectors'])
assert sha(ROOT/'image_worker/product/worker.py')==sha(BASE/'image-worker/product/worker.py')
result['installed_generation_worker_unchanged']=True
native=BASE/'qa/photo-editing-pe1-c-prep-20261020/native'
assert sha(native/'launches.jsonl')==sha(ROOT/'artifacts/photo-editing/pe1-c-native-20261020/launches.jsonl')
assert len((native/'launches.jsonl').read_text().splitlines())==5
pe0=BASE/'qa/photo-editing-pe0-prep-20261019/worker-launches.jsonl'
assert sha(pe0)==sha(ROOT/'artifacts/photo-editing/native-20261019/worker-launches.jsonl')
assert len(pe0.read_text().splitlines())==6
private_edit=BASE/'qa/photo-hat-private-20261020'
assert read(private_edit/'result.json')['new_native_invocations']==1
result['unchanged_prior_budgets']={'PE0_images':6,'private_edit_images':1,'PE1C_images':4,'PE1C_preloads':1}
ledgers=read(ROOT/'artifacts/production-followups/preservation-final.json')['stopped_trial_ledgers']
for name,folder in [('Hermes','hermes-h0-20261017/native-2'),('PydanticAI','pydantic-p0-20261018/native'),('N1','native-agent-n1-20261018'),('C1','native-agent-c1-20261018')]:
 assert sha(BASE/'qa'/folder/'ledger.json')==ledgers[name]['sha256']
result['stopped_trial_ledgers_preserved']=True
bundle=BASE/'qa/photo-editing-pe1-integration-20261021/bundle'
assert sha(bundle/'original.plist')==read(bundle/'release.json')['original_plist_sha256']
# Find the same service by its saved label; never print private plist contents.
import plistlib
label=read(bundle/'release.json')['service']['label']
matches=[p for p in (Path.home()/'Library/LaunchAgents').glob('*.plist') if plistlib.loads(p.read_bytes()).get('Label')==label]
assert len(matches)==1 and sha(matches[0])==sha(bundle/'original.plist')
result['original_service_plist_unchanged']=True
with httpx.Client(timeout=5,trust_env=False) as client:
 for name,url in [('local','http://127.0.0.1:8787/api/health'),('https','https://jakes-mac-mini.tailc4d343.ts.net/api/health')]:
  response=client.get(url);response.raise_for_status();assert response.json()['ok'];result[name+'_healthy']=True
 response=client.get('http://127.0.0.1:11434/api/version');response.raise_for_status();assert response.json()=={'version':'0.35.0'}
result['Ollama_version']='0.35.0'
(OUT/'preservation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
