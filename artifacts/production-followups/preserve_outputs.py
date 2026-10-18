"""Archive fresh synthetic test evidence, then restore tracked historical outputs."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'artifacts/production-followups'
QA=Path.home()/'.local/share/workbench/qa/production-followups-20261018'
ARCHIVE=QA/'historical-generated'

def sha(p):
 return hashlib.sha256(p.read_bytes()).hexdigest()

before=json.loads((QA/'historical-before.json').read_text())['files']
tracked=set(subprocess.check_output(['git','ls-files','artifacts'],cwd=ROOT,text=True).splitlines())
changed=[]; new=[]; archived={}
for p in sorted((ROOT/'artifacts').rglob('*')):
 if not p.is_file() or 'production-followups' in p.parts or '__pycache__' in p.parts:
  continue
 name=str(p.relative_to(ROOT));digest=sha(p)
 if before.get(name)==digest:
  continue
 target=ARCHIVE/name
 target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():
  assert sha(target)==digest,'Never replace an earlier retained result'
 else:
  shutil.copy2(p,target)
 assert sha(target)==digest
 archived[name]=digest
 if name in tracked:
  original=subprocess.check_output(['git','show','HEAD:'+name],cwd=ROOT)
  assert hashlib.sha256(original).hexdigest()==before[name]
  changed.append(name)
 elif name not in before:
  new.append(name)
 else:
  raise AssertionError('Unexpected modified nontracked historical file')
# Keep current workflow copy screenshots easy to review on the candidate itself.
for width in (390,1440):
 for theme in ('light','dark'):
  for engine in ('chromium','webkit'):
   source=ROOT/f'artifacts/workflow-studio/ws-a/browser/home-populated-{width}-{theme}-{engine}-fake.png'
   if source.exists():
    destination=OUT/f'browser/workflow-home-{width}-{theme}-{engine}-fake.png'
    destination.parent.mkdir(exist_ok=True)
    shutil.copy2(source,destination)
for offset in range(0,len(changed),100):
 subprocess.run(['git','restore','--source=HEAD','--worktree','--',*changed[offset:offset+100]],cwd=ROOT,check=True)
for name in new:
 (ROOT/name).unlink()
for name,digest in before.items():
 if name in tracked:
  assert sha(ROOT/name)==digest,name
record={'changed_historical_outputs':len(changed),'new_historical_path_outputs':len(new),
 'preserved_tracked_historical_files':sum(n in tracked for n in before),
 'private_archive':'production-followups-20261018/historical-generated', 'archived_files':archived,
 'ignored_bytecode_excluded':sum(n not in tracked for n in before)}
(OUT/'historical-preservation.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:v for k,v in record.items() if k!='archived_files'},indent=2))
