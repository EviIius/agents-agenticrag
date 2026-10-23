"""Real CPU preservation and operation ordering; never import an image model."""

import json

import pytest
from test_masked_edit import ROOT, cpu


def test_protect_hole_preserves_original_and_repainting_is_ordered():
    result = cpu("""
from PIL import Image
from masked_edit import composite,raster
import json
source=Image.new('RGB',(768,1024),(45,87,133))
paint={'radius':.2,'points':[[.5,.5]]}
protect={'operation':'erase','radius':.07,'points':[[.5,.5]]}
selection={'version':1,'strokes':[paint,protect]}
mask=raster(source.size,selection)
assert mask.getpixel((384,512))==0 and mask.getpixel((484,512))==255
output,proof=composite(source,Image.new('RGB',(1024,1024),'red'),selection)
assert output.getpixel((384,512))==source.getpixel((384,512))
assert output.getpixel((484,512))!=source.getpixel((484,512))
assert proof['outside_changed_pixels']==0
selection['strokes'].append({'operation':'paint','radius':.025,'points':[[.5,.5]]})
mask=raster(source.size,selection)
assert mask.getpixel((384,512))==255 and mask.getpixel((424,512))==0
print(json.dumps(proof))
""")
    assert json.loads(result)["outside_changed_pixels"] == 0


def test_legacy_mask_matches_retained_native_trial_exactly():
    expected = json.loads(
        (
            ROOT / "artifacts/photo-editing/pe2-20261021/synthetic/metadata.json"
        ).read_text()
    )["composition"]["mask_sha256"]
    result = cpu("""
import hashlib,json
from masked_edit import raster
mask=raster((768,1024),{'version':1,'strokes':[{'radius':.15,'points':[[.5,.45]]}]})
print(json.dumps({'sha256':hashlib.sha256(mask.tobytes()).hexdigest(),'protected_pixels':mask.histogram()[0]}))
""")
    data = json.loads(result)
    assert data["sha256"] == expected
    assert data["protected_pixels"] == 744543


@pytest.mark.parametrize(
    "strokes",
    [
        [{"operation": "blur", "radius": 0.1, "points": [[0.5, 0.5]]}],
        [{"operation": None, "radius": 0.1, "points": [[0.5, 0.5]]}],
        [{"operation": "erase", "radius": 0.1, "points": [[0.5, 0.5]]}],
        [
            {"radius": 0.1, "points": [[0.5, 0.5]]},
            {"operation": "erase", "radius": 0.1, "points": [[0.5, 0.5]]},
        ],
    ],
)
def test_invalid_or_completely_protected_mask_refused_before_model_import(strokes):
    assert (
        cpu(
            """
import json
from masked_edit import raster
try: raster((768,1024),{'version':1,'strokes':json.loads(sys.argv[2])})
except ValueError: print('refused')
else: raise AssertionError('Unusable selection accepted')
""",
            json.dumps(strokes),
        ).strip()
        == "refused"
    )
