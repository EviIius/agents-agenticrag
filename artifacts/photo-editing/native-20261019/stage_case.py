"""CPU staging for the six declared synthetic cases. Never load a native model."""
import importlib.abc
import json
import sys
from pathlib import Path


class NoNative(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'mlx', 'mflux', 'torch', 'transformers'}:
            raise RuntimeError('Native imports forbidden during input staging')


def audit(event, args):
    if event.startswith('socket.connect'):
        raise RuntimeError('Network forbidden during input staging')


sys.meta_path.insert(0, NoNative())
sys.addaudithook(audit)
root, case_id = Path(sys.argv[1]).resolve(), sys.argv[2]
sys.path.insert(0, str(root/'worker'))
from contracts import digest, load_request, normalize, write_new

spec=json.loads((root/'worker/trial.json').read_text())
case=next(c for c in spec['cases'] if c['id']==case_id)
request_case=next(c for c in spec['cases'] if c['id']==case.get('same_request_as',case_id))
job=root/'cases'/case_id
job.mkdir(mode=0o700,parents=True,exist_ok=True)
output=job/'output'
output.mkdir(mode=0o700,exist_ok=True)
manifest=job/'request.json'
if not manifest.exists():
    request={'mode':request_case['mode'],'prompt':request_case['prompt'],'seed':42}
    if request['mode']=='edit':
        (job/'inputs').mkdir(mode=0o700,exist_ok=False)
        if case_id=='mug':
            raise ValueError('Retained mug was prepared and frozen offline; do not reconstruct it')
        portrait=root/'cases/portrait/output/image.png'
        original_hash=digest(portrait)
        expected=json.loads((root/'cases/portrait/output/metadata.json').read_text())['sha256']
        if original_hash!=expected:
            raise ValueError('Retained portrait bytes changed')
        if case_id=='clothing':
            from PIL import Image
            with Image.open(portrait) as source:
                if source.size!=(1024,1024): raise ValueError('Unexpected base framing')
                derivative=source.convert('RGB').crop((128,0,896,1024)).transpose(Image.Transpose.ROTATE_90)
                exif=Image.Exif();exif[274]=6
                with (job/'inputs/original').open('xb') as stream:
                    derivative.save(stream,format='JPEG',quality=95,exif=exif)
            write_new(job/'inputs/derivative.json',(json.dumps({'source_sha256':original_hash,'operation':case['reference']},indent=2)+'\n').encode())
        else:
            write_new(job/'inputs/original',portrait.read_bytes())
        (job/'inputs/original').chmod(0o600)
        request['reference']=normalize(job)
    write_new(manifest,(json.dumps(request,indent=2)+'\n').encode())
request,reference=load_request(manifest,output)
if any(request[k]!=v for k,v in {'mode':request_case['mode'],'prompt':request_case['prompt'],'seed':42}.items()):
    raise ValueError('Staged request differs from frozen plan')
print(json.dumps({'case':case_id,'request_sha256':digest(manifest),'reference':request.get('reference'),'worker_invocations':0},indent=2))
