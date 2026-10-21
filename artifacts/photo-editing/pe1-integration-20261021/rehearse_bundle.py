"""Real prepared app/worker/data/backup rehearsal; inference/network forbidden."""
import hashlib
import importlib.util
import json
import os
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
BASE=Path.home()/'.local/share/workbench'
PRIVATE=BASE/'qa/photo-editing-pe1-integration-20261021'
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'server')]
from prepare_photo_release import prepare, verify, inventory
from app.images.backup import restore


def load(name):
 spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/f'{name}.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


CHILD=r'''
import asyncio,hashlib,json,socket,sys
from pathlib import Path
from uuid import uuid4
source,data,worker,label,ids_file,fixture=map(Path,sys.argv[1:])
label=str(label)
sys.path.insert(0,str(source/'server'))
def blocked(*a,**k):raise RuntimeError('Network forbidden in release rehearsal')
socket.socket.connect=blocked;socket.socket.connect_ex=blocked
original=asyncio.create_subprocess_exec
async def cpu_only(*args,**kwargs):
 allowed=(args and str(args[0])=='/usr/bin/sips') or (len(args)>1 and str(args[1])==str(worker/'reference_codec.py'))
 if not allowed:raise RuntimeError('GPU/model process forbidden in release rehearsal')
 return await original(*args,**kwargs)
asyncio.create_subprocess_exec=cpu_only
import app.main
assert Path(app.main.__file__).resolve().is_relative_to(source.resolve())
from app.config import Settings
from app.schemas import ImageStatus
from app.images.engine import Engine
import httpx
calls=[]
class Capture:
 def __init__(self,*args):pass
 def status(self):return ImageStatus(available=True,editing_available=True)
 async def run(self,*args):raise AssertionError('Plain generation forbidden')
 async def run_edit(self,manifest,scratch,progress):
  spec=json.loads(manifest.read_text());assert spec['mode']=='edit' and spec['reference']
  assert (manifest.parent/'inputs/original').is_file()
  calls.append({'method':'run_edit','reference_bound':True})
  raise ValueError('Synthetic capture, no native work')
async def main():
 ids=json.loads(ids_file.read_text())
 from app.images import jobs
 if label!='baseline13':
  assert Engine(worker).status().editing_available
  jobs.Engine=Capture
 application=__import__('app.main',fromlist=['create_app']).create_app(Settings(data_dir=data,dev=False,image_home=worker if label!='baseline13' else None,transcribe_home=None,legacy_db=data/'missing.db',allowed_hosts=''))
 async with application.router.lifespan_context(application),httpx.AsyncClient(transport=httpx.ASGITransport(application),base_url='http://localhost') as client:
  assert (await client.get('/api/health')).json()['ok']
  if label=='baseline13':
   assert (await application.state.store.one('PRAGMA user_version'))['user_version']==13
   chat=(await client.post('/api/chats',json={})).json()
   assert (await client.patch('/api/chats/'+chat['id'],json={'title':'Fake pre-upgrade chat'})).status_code==200
   ids_file.write_text(json.dumps({'chat':chat['id']}))
   print(json.dumps({'old_schema_seeded':13,'network_blocked':True,'native_calls':0}));return
  assert (await application.state.store.one('PRAGMA user_version'))['user_version']==14
  assert Engine.qualified_edit([])
  assert application.state.images.engine.status().editing_available
  if label=='upgrade13':
   chat=await client.get('/api/chats/'+ids['chat']);assert chat.status_code==200
   assert chat.json()['chat']['title']=='Fake pre-upgrade chat'
   print(json.dumps({'schema13_upgraded_to14':True,'old_chat_preserved':True,'native_calls':0}));return
  await asyncio.gather(*list(application.state.images.tasks.values()))
  queued=await application.state.images.get(ids['queued']['job']);assert queued.state=='failed'
  startup_calls=len(calls)
  assert startup_calls==(1 if label=='candidate' else 0)
  old=ids['complete']
  assert (await client.get('/api/images/jobs/'+old['job']+'/output/png')).status_code==200
  if label=='compatibility':
   assert await application.state.store.one('SELECT id FROM chats WHERE id=?',(ids['new_chat'],))
   assert await application.state.store.one('SELECT id FROM image_references WHERE id=?',(ids['new_ref'],))
  else:
   cid=(await client.post('/api/chats',json={})).json()['id'];ids['new_chat']=cid
   assert (await client.patch('/api/chats/'+cid,json={'title':'Fake after-candidate chat'})).status_code==200
   raw=fixture.read_bytes();r=await client.post(f'/api/chats/{cid}/image-references',files={'file':('fake-input.heic',raw,'image/heic')});assert r.status_code==201,r.text
   ids['new_ref']=r.json()['id'];ref=application.state.images.references.path(ids['new_ref'])
   assert (ref/'original').read_bytes()==raw
   assert not application.state.images.references.codec.processes and not application.state.images.references.uploads.processes
   ids_file.write_text(json.dumps(ids))
  application.state.images.engine=Capture()
  result=await client.post('/api/chats/'+old['chat']+'/messages/'+old['message']+'/images/retry',json={'request_key':uuid4().hex,'seeds':[99]})
  assert result.status_code==202,result.text
  new=result.json()['assistant']['images'][0]
  assert new['mode']=='edit' and new['reference']['id']
  await asyncio.gather(*list(application.state.images.tasks.values()))
  assert calls==[{'method':'run_edit','reference_bound':True}]*(startup_calls+1)
  assert not application.state.images.capacity.busy
 print(json.dumps({'label':label,'staged_source_imported':True,'schema':14,'queued_edit_resume_kept_reference':True,'startup_fake_edit_attempts':startup_calls,'reference_retry_retained':True,'current_chat_and_inputs_kept':True,'actual_cpu_upload_checked':label=='candidate','network_blocked':True,'native_calls':0}))
asyncio.run(main())
'''


def run(source,data,worker,label,ids,fixture):
 result=subprocess.run([sys.executable,'-c',CHILD,str(source),str(data),str(worker),label,str(ids),str(fixture)],cwd=source/'server',env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True,timeout=60)
 (OUT/(label+'.txt')).write_text(result.stdout+result.stderr)
 assert result.returncode==0,result.stderr
 return json.loads(result.stdout)


seed=PRIVATE/'seed'
if not seed.exists():shutil.copytree(BASE/'qa/photo-editing-pe1-c-prep-20261020/rollback-seed',seed)
ids=PRIVATE/'rehearsal-ids.json';shutil.copy2(BASE/'qa/photo-editing-pe1-c-prep-20261020/rollback-ids.json',ids)
plist,_=load('deploy').existing_service()
bundle=PRIVATE/'bundle'
if bundle.exists():
 verify(bundle);manifest=json.loads((bundle/'release.json').read_text())
else:manifest=prepare(bundle,seed,BASE/'app',BASE/'image-worker/product',plist)
verify(bundle)
copy=PRIVATE/'current-data'
finishing='--finish' in sys.argv
if not finishing:shutil.copytree(bundle/'data-snapshot',copy)
fixture=ROOT/'server/tests/fixtures/images/fake-synthetic.heic'
immutable={str(p.relative_to(bundle/'data-snapshot')):hashlib.sha256(p.read_bytes()).hexdigest() for d in ['images','image-references'] for p in (bundle/'data-snapshot'/d).rglob('*') if p.is_file() and p.name in ['original','reference.png','reference.json','input.json','image.png','export.png','metadata.json']}
if finishing:
 results=[json.loads((OUT/(name+'.txt')).read_text().splitlines()[0]) for name in ['candidate','compatibility']]
else:results=[run(bundle/'candidate-app',copy,bundle/'worker','candidate',ids,fixture),run(bundle/'compatibility-app',copy,bundle/'worker','compatibility',ids,fixture)]
for name,digest in immutable.items():assert hashlib.sha256((copy/name).read_bytes()).hexdigest()==digest
restored=PRIVATE/('paired-restored-final' if finishing else 'paired-restored');restored_outputs=restore(bundle/'paired-backup/auto-release.db',restored)
assert restored_outputs==1
restored_json_manifests=0
for name,digest in immutable.items():
 if Path(name).name=='input.json':
  assert json.loads((restored/name).read_text())==json.loads((bundle/'data-snapshot'/name).read_text());restored_json_manifests+=1
 else:assert hashlib.sha256((restored/name).read_bytes()).hexdigest()==digest
old=BASE/'qa/photo-editing-pe1-c-prep-20261020/previous-source'
old_data=PRIVATE/'schema13';old_ids=PRIVATE/'schema13-ids.json';old_ids.write_text('{}')
results.append(run(old,old_data,bundle/'worker','baseline13',old_ids,fixture))
results.append(run(bundle/'candidate-app',old_data,bundle/'worker','upgrade13',old_ids,fixture))
report={'passed':True,'native_calls':0,'bundle_files':len(manifest['files']),'dependency_files_unchanged':True,'source_app_and_worker_unchanged':True,'original_plist_preserved':True,'immutable_reference_output_files_preserved':len(immutable),'paired_backup_restored_outputs':restored_outputs,'restored_manifests_semantically_identical':restored_json_manifests,'previous_backend_archive_only':True,'full_old_backend_rollback_prohibited':True,'results':results}
(OUT/'bundle-rehearsal.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
