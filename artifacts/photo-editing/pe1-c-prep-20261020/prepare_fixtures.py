"""Prepare synthetic CPU-only inputs; no native imports or model calls."""
import hashlib
import json
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PRIVATE = Path.home() / '.local/share/workbench/qa/photo-editing-pe1-c-prep-20261020'
FIXTURES = PRIVATE / 'fixtures'
FIXTURES.mkdir(mode=0o700, exist_ok=False)
python = (PRIVATE / 'codec-home/.python').read_text().strip()
source = ROOT / 'artifacts/photo-editing/native-20261019/cases/clothing/reference.png'
code = r'''
import importlib.abc,sys
from pathlib import Path
class NoNative(importlib.abc.MetaPathFinder):
 def find_spec(self,name,*args):
  if name.split('.')[0] in {'mlx','mflux','torch','transformers'}:raise RuntimeError('Native imports forbidden')
sys.meta_path.insert(0,NoNative())
from PIL import Image
source,root=map(Path,sys.argv[1:])
with Image.open(source) as image:
 image.convert('RGB').resize((2560,2560),Image.Resampling.LANCZOS).save(root/'large-synthetic.png')
 portrait=image.convert('RGB').resize((960,1280),Image.Resampling.LANCZOS)
 exif=Image.Exif();exif[274]=6;exif[315]='Synthetic QA; no private photo'
 portrait.save(root/'oriented-synthetic.jpeg',quality=92,exif=exif)
'''
subprocess.run([python, '-c', code, str(source), str(FIXTURES)], check=True, timeout=30)
subprocess.run(['/usr/bin/sips', '-s', 'format', 'heic', str(FIXTURES / 'large-synthetic.png'), '--out', str(FIXTURES / 'large-synthetic.heic')], check=True, capture_output=True, timeout=30)
for file in FIXTURES.iterdir(): file.chmod(0o600)
files = {p.name: {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size} for p in sorted(FIXTURES.iterdir())}
manifest = {'synthetic_only': True, 'model_calls': 0, 'source': str(source.relative_to(ROOT)), 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'files': files, 'tools': ['existing image interpreter / Pillow (CPU)', '/usr/bin/sips'], 'expected': {'large-synthetic.heic': {'original_dimensions': [2560,2560], 'working_dimensions': [2048,2048]}, 'oriented-synthetic.jpeg': {'original_dimensions': [960,1280], 'exif_orientation': 6, 'working_dimensions': [1280,960]}}}
(OUT / 'fixture-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'synthetic_fixtures':len(files),'model_calls':0}))
