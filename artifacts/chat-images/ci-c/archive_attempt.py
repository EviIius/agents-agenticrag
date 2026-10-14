"""Keep test failures/source and every available synthetic recording before reruns."""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).parent
name=sys.argv[1]
target=OUT/'attempts'/name
assert not target.exists()
target.mkdir(parents=True)
video_root=Path.home()/'.local/share/workbench/qa/chat-images/ci-c/videos'/name
records=[]
source=ROOT/'web/test-results'
for path in sorted(source.rglob('*')):
    if not path.is_file():continue
    dest=(video_root if path.suffix=='.webm' else target/'browser')/path.relative_to(source)
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(path,dest)
    records.append({'path':str(dest),'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
    if path.suffix=='.webm':path.unlink()
changed=subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=ROOT,text=True).splitlines()
changed+=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines()
for artifact in set(changed):
    path=ROOT/artifact
    if path.is_file() and artifact.startswith('artifacts/') and not artifact.startswith('artifacts/chat-images/ci-c/'):
        dest=target/'regenerated'/artifact
        if dest.suffix=='.png' and 'fake' not in dest.name:dest=dest.with_name(dest.stem+'-fake.png')
        dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,dest)
for name in set(changed):
    path=ROOT/name
    if path.is_file() and name.startswith(('web/src/','web/tests/','server/app/','server/tests/','scripts/')):
        dest=target/'source'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,dest)
(target/'retained-files.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps({'attempt':sys.argv[1],'retained_browser_files':len(records),'videos_outside_git':sum(r['path'].endswith('.webm') for r in records)}))
