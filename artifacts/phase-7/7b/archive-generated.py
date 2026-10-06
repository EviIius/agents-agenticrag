"""Archive synthetic regenerated historical outputs; restore accepted evidence."""
from pathlib import Path
import hashlib,json,subprocess,shutil,tempfile,sys
root=Path(__file__).resolve().parents[3]
stage=sys.argv[1]
assert stage in {'preview-interrupted','tablet-failure','final'}
out=root/'artifacts/phase-7/7b'/('regenerated-'+stage);out.mkdir(exist_ok=True)
private=Path(tempfile.mkdtemp(prefix='workbench-7b-'+stage+'-'));items=[]
paths=subprocess.check_output(['git','diff','--name-only','--','artifacts'],cwd=root,text=True).splitlines()
old=[name for name in paths if not name.startswith('artifacts/phase-7/7b/')]
for name in old:
 source=root/name;relative=Path(name.removeprefix('artifacts/'))
 target=(private if source.suffix in {'.png','.gz','.webm'} else out)/relative
 target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
 items.append({'path':name,'archive':str(target) if private in target.parents else str(target.relative_to(root)),'sha256':hashlib.sha256(source.read_bytes()).hexdigest()})
if old:subprocess.run(['git','restore','--source=HEAD','--',*old],cwd=root,check=True)
(out/'archive.json').write_text(json.dumps({'stage':stage,'files':items},indent=2)+'\n')
print('Archived/restored historical outputs:',len(items))
