import hashlib,json,subprocess
from pathlib import Path
root=Path('/Users/evilius/Documents/GitHub/agents-agenticrag')
folders=['server/app','server/tests','web/src','web/tests','scripts','shared']
paths=set(subprocess.check_output(['git','ls-files',*folders],cwd=root,text=True).splitlines())
paths.update(subprocess.check_output(['git','ls-files','--others','--exclude-standard',*folders],cwd=root,text=True).splitlines())
result={name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in sorted(paths) if (root/name).is_file()}
print(json.dumps(result,indent=2))
