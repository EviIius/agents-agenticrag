"""Promote verified environments, preserving originals and rolling back on error."""
import hashlib,json,os,plistlib,shutil,sqlite3,subprocess,time
from datetime import datetime,UTC
from pathlib import Path

ROOT=Path('/Users/evilius/Documents/GitHub/agents-agenticrag')
BASE=Path.home()/'.local/share/workbench'
OUT=ROOT/'artifacts/phase-7/candidate'
PLIST=Path.home()/'Library/LaunchAgents/dev.agenticrag.workbench.plist'
DOMAIN=f'gui/{os.getuid()}'
SERVICE=f'{DOMAIN}/dev.agenticrag.workbench'
ENGINE=BASE/'app/transcribe/.python'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def launch(*args):return subprocess.run(['launchctl',*args],capture_output=True,text=True)
bootstrap_attempts=[]
def bootstrap():
 for _ in range(40):
  call=launch('bootstrap',DOMAIN,str(PLIST))
  bootstrap_attempts.append({'returncode':call.returncode,'stderr':call.stderr.strip()})
  if call.returncode==0:return
  time.sleep(.5)
 raise RuntimeError('Launchd bootstrap failed after retries')

def health():
 import httpx
 for _ in range(50):
  try:
   with httpx.Client(timeout=2) as client:
    result={name:client.get(url).status_code for name,url in [('local','http://127.0.0.1:8787/api/health'),('tailscale','https://jakes-mac-mini.tailc4d343.ts.net/api/health')]}
   if result=={'local':200,'tailscale':200}:return result
  except httpx.HTTPError:pass
  time.sleep(.2)
 raise RuntimeError('Runtime health did not recover')

text=(OUT/'e2e.txt').read_text()
assert '403 passed' in text and '3 skipped' in text and 'failed' not in text.splitlines()[-1]
assert json.loads((OUT/'service-restored.json').read_text())['local']==200
before_plist=digest(PLIST);before_engine=digest(ENGINE)
plist=plistlib.loads(PLIST.read_bytes());args=plist['ProgramArguments']
assert plist['Label']=='dev.agenticrag.workbench'
assert args[args.index('--host')+1]=='127.0.0.1'
assert args[args.index('--port')+1]=='8787'
assert args[args.index('--workers')+1]=='1'
for filename in ['probe-development.json','probe-installed-source.json']:
 assert json.loads((OUT/filename).read_text())['status']=='passed'
assert json.loads((OUT/'engine-interpreter.json').read_text())['engine_uses_server_environment'] is False
source_paths=subprocess.check_output(['git','ls-files','server/app'],cwd=ROOT,text=True).splitlines()
source_paths=[n for n in source_paths if not n.startswith('server/app/static/')]
assert all(digest(ROOT/n)==digest(BASE/'app'/n) for n in source_paths)
for target,candidate in [(ROOT/'server/.venv',BASE/'tools/library-probe/development/.venv'),(BASE/'app/server/.venv',BASE/'tools/library-probe/installed-candidate/.venv')]:
 assert target.is_dir() and not target.is_symlink() and candidate.is_dir() and not candidate.is_symlink(),'Already promoted or unexpected environment layout'
stamp=datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')
fallback=BASE/'tools/library-probe'/f'framework-fallback-{stamp}'
fallback.mkdir(mode=0o700)
for name in ['pyproject.toml','uv.lock']:
 shutil.copy2(BASE/'app/server'/name,fallback/name)
backup=BASE/'data/backups'/f'workbench-before-library-runtime-{stamp}.db'
backup.touch(mode=0o600)
with sqlite3.connect((BASE/'data/workbench.db').as_uri()+'?mode=ro',uri=True) as source,sqlite3.connect(backup) as dest:
 assert source.execute('PRAGMA user_version').fetchone()[0]==7
 source.backup(dest)
 assert dest.execute('PRAGMA quick_check').fetchone()[0]=='ok'
backup.chmod(0o600)
roles=[('development',ROOT/'server/.venv',BASE/'tools/library-probe/development/.venv'),('installed',BASE/'app/server/.venv',BASE/'tools/library-probe/installed-candidate/.venv')]
changed=[]
result={'database_backup_created_before_switch':True,'backup_path':str(backup),'fallback_root':str(fallback),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'schema':7,'production_source_files_unchanged':len(source_paths),'moves':[]}
stopped=launch('bootout',SERVICE)
assert stopped.returncode==0,'Existing service did not stop'
for _ in range(100):
 listener=subprocess.run(['lsof','-t','-iTCP:8787','-sTCP:LISTEN'],capture_output=True,text=True)
 if not listener.stdout.strip():break
 time.sleep(.2)
try:
 for role,target,candidate in roles:
  old=fallback/role/'.venv';old.parent.mkdir(mode=0o700)
  assert target.is_dir() and not target.is_symlink() and candidate.is_dir() and not candidate.is_symlink()
  target.rename(old)
  changed.append((target,candidate,old))
  candidate.rename(target)
  candidate.symlink_to(target,target_is_directory=True)
  result['moves'].append({'role':role,'target':str(target),'candidate_alias':str(candidate),'previous_environment':str(old)})
 for name in ['pyproject.toml','uv.lock']:
  shutil.copy2(ROOT/'server'/name,BASE/'app/server'/name)
 bootstrap()
 result['health']=health()
 for role,target,candidate in roles:
  data=subprocess.check_output([str(target/'bin/python'),str(ROOT/'scripts/probe_library.py'),'--server-dir',str(target.parent),'--model','qwen3-embedding:0.6b'],cwd=ROOT,text=True)
  probe=json.loads(data)
  (OUT/f'probe-active-{role}.json').write_text(json.dumps(probe,indent=2)+'\n')
  assert probe['status']=='passed',f'{role} active probe blocked'
 assert digest(PLIST)==before_plist and digest(ENGINE)==before_engine
 assert all(digest(ROOT/n)==digest(BASE/'app'/n) for n in source_paths)
 import httpx
 with httpx.Client(timeout=15) as client:
  response=client.get('http://127.0.0.1:8787/api/transcription/status')
  response.raise_for_status()
  payload=response.json()
  result['transcription_response_http_status']=response.status_code
  result['transcription_engine_ready']=payload['ready']
  assert payload['ready'],'Transcription engine not ready'
 result['health_after_probes']=health()
 result.update({'status':'passed','launchd_plist_unchanged':True,'transcription_interpreter_selection_unchanged':True,'all_application_source_unchanged':True,'old_environments_preserved':True,'metadata_updated_to_approved_frozen_lock':True})
except BaseException as exc:
 launch('bootout',SERVICE)
 for target,candidate,old in reversed(changed):
  if candidate.is_symlink():candidate.unlink()
  if target.exists():target.rename(candidate)
  if old.exists():old.rename(target)
 for name in ['pyproject.toml','uv.lock']:
  shutil.copy2(fallback/name,BASE/'app/server'/name)
 bootstrap()
 result.update({'status':'rolled_back','error_type':type(exc).__name__,'error':str(exc),'rollback_health':health()})
 result['bootstrap_attempts']=bootstrap_attempts
 (OUT/'promotion.json').write_text(json.dumps(result,indent=2)+'\n')
 raise
result['bootstrap_attempts']=bootstrap_attempts
(OUT/'promotion.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['status','health','health_after_probes','schema','old_environments_preserved']}))
