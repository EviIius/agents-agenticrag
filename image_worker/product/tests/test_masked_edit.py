"""Actual CPU mask/worker tests; native generation is replaced, never invoked."""

import asyncio
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from test_photo_edit_offline import HERE, PYTHON, finish, job, spawn

ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "server"))
from app.images.codec import ReferenceCodec  # noqa: E402
from app.images.files import sanitize_export, validate  # noqa: E402

SELECTION = {"version": 1, "strokes": [
    {"radius": 0.08, "points": [[0.3, 0.2], [0.35, 0.25]]},
    {"radius": 0.05, "points": [[0.7, 0.8]]},
]}


def cpu(code, *arguments):
    guard = """
import importlib.abc,sys
class NoNative(importlib.abc.MetaPathFinder):
 def find_spec(self,fullname,path=None,target=None):
  if fullname.split('.')[0] in {'mlx','mflux','torch','transformers'}: raise RuntimeError('Native forbidden')
sys.meta_path.insert(0,NoNative())
def audit(event,args):
 if event.startswith('socket.connect'): raise RuntimeError('Network forbidden')
sys.addaudithook(audit)
sys.path.insert(0,sys.argv[1])
"""
    return subprocess.run([str(PYTHON), "-c", guard + code, str(HERE), *map(str, arguments)],
                          capture_output=True, text=True, check=True).stdout


@pytest.mark.parametrize("size", [(768, 1024), (1024, 512), (2048, 1536)])
def test_composite_preserves_all_unselected_pixels_and_proportions(size):
    result = cpu("""
import json
from PIL import Image,ImageChops
from masked_edit import composite,raster
w,h=map(int,sys.argv[2:]);source=Image.new('RGB',(w,h),(91,137,203))
# A small single-channel change must be noticed, including blue=1.
source.putpixel((0,0),(91,137,204))
selection={'version':1,'strokes':[{'radius':.08,'points':[[.5,.4],[.6,.5]]}]}
result,proof=composite(source,Image.new('RGB',(1024,1024),'red'),selection)
mask=raster(source.size,selection)
diff=ImageChops.difference(source,result)
assert ImageChops.multiply(diff.getchannel('R'),ImageChops.invert(mask)).getbbox() is None
assert ImageChops.multiply(diff.getchannel('G'),ImageChops.invert(mask)).getbbox() is None
assert ImageChops.multiply(diff.getchannel('B'),ImageChops.invert(mask)).getbbox() is None
assert result.size==source.size and result.getpixel((0,0))==source.getpixel((0,0))
assert proof['changed_pixels']>0 and proof['outside_changed_pixels']==0
print(json.dumps(proof))
""", *size)
    assert json.loads(result)["reference_dimensions"] == list(size)


@pytest.mark.parametrize("selection", [
    {}, {"version": 2, "strokes": []},
    {"version": 1, "strokes": [{"radius": 0, "points": [[0.5, 0.5]]}]},
    {"version": 1, "strokes": [{"radius": 0.1, "points": [[-1, 0.5]]}]},
    {"version": 1, "strokes": [{"radius": 0.1, "points": [[float("nan"), 0.5]]}]},
    {"version": 1, "strokes": [{"radius": 0.1, "points": [[0.5, 0.5]] * 129}]},
])
def test_invalid_masks_stop_before_native_import(selection):
    assert cpu("""
import json
from masked_edit import selection_valid
try: selection_valid(json.loads(sys.argv[2]))
except ValueError: print('refused')
else: raise AssertionError('Invalid selection accepted')
""", json.dumps(selection)).strip() == "refused"


async def masked_job(tmp_path):
    root, request = await job(tmp_path)
    request["selection"] = SELECTION
    (root / "input.json").write_text(json.dumps(request))
    code, events = await asyncio.to_thread(finish, spawn(root))
    assert code == 0 and events[-1]["type"] == "finished"
    home = tmp_path / "home"
    (home / "masked_edit.py").write_bytes((HERE / "masked_edit.py").read_bytes())
    return root, request, ReferenceCodec(home)


@pytest.mark.asyncio
async def test_worker_crop_composite_independent_check_and_export(tmp_path):
    root, request, checker = await masked_job(tmp_path)
    proof = await checker.verify_composite(root)
    assert proof["outside_changed_pixels"] == 0 and proof["changed_pixels"] > 0
    assert proof["reference_dimensions"] == [768, 1024]
    output = root / "working"
    assert not (output / ".selected-reference.png").exists()
    assert (output / "native.png").is_file()
    validate(output, request)
    sanitize_export(output)
    assert not checker.processes
    cpu("""
from pathlib import Path
from PIL import Image,ImageChops
p=Path(sys.argv[2]);a=Image.open(p/'image.png');b=Image.open(p/'export.png')
assert a.size==(768,1024) and ImageChops.difference(a,b).getbbox() is None
assert not b.info
""", output)


@pytest.mark.asyncio
async def test_independent_check_rejects_changed_protected_pixel_even_with_updated_hash(tmp_path):
    root, request, checker = await masked_job(tmp_path)
    cpu("""
import hashlib,json
from pathlib import Path
from PIL import Image
p=Path(sys.argv[2]);im=Image.open(p/'image.png');im.load();im.putpixel((0,0),(0,0,1));im.save(p/'image.png')
m=json.loads((p/'metadata.json').read_text());m['sha256']=hashlib.sha256((p/'image.png').read_bytes()).hexdigest();(p/'metadata.json').write_text(json.dumps(m))
""", root / "working")
    validate(root / "working", request)  # Ordinary hash/PNG validation alone cannot catch it.
    with pytest.raises(Exception, match="preservation check"):
        await checker.verify_composite(root)
    assert not checker.processes


@pytest.mark.asyncio
async def test_native_png_is_hash_bound(tmp_path):
    root, request, _ = await masked_job(tmp_path)
    path = root / "working/native.png"
    path.write_bytes(path.read_bytes() + b"changed")
    with pytest.raises(ValueError):
        validate(root / "working", request)
