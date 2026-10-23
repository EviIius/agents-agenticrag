"""Synthetic overlap/protection invariant, CPU only and no private inputs."""

import json
import sys
from pathlib import Path

from audit import delta, deny_native
from PIL import Image, ImageChops, ImageDraw

sys.addaudithook(deny_native)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "product"))
from masked_edit import composite, raster

source = Image.new("RGB", (768, 1024), "gray")
face = Image.new("L", source.size, 0)
ImageDraw.Draw(face).ellipse((200, 180, 568, 600), fill=255)
source.paste(Image.new("RGB", source.size, "tan"), (0, 0), face)
core = Image.new("L", source.size, 0)
ImageDraw.Draw(core).rectangle((300, 280, 470, 540), fill=255)
draw = ImageDraw.Draw(source)
draw.ellipse((320, 295, 340, 315), fill="black")
draw.ellipse((430, 295, 450, 315), fill="black")
draw.line((350, 440, 420, 440), fill="black", width=6)
selection = {
    "version": 1,
    "strokes": [
        {"radius": 0.14, "points": [[0.5, 0.23]]},
        {"operation": "erase", "radius": 0.10, "points": [[0.4, 0.31], [0.6, 0.31]]},
    ],
}
selected = raster(source.size, selection)
assert ImageChops.multiply(selected, core).getbbox() is None
output, proof = composite(source, Image.new("RGB", (1024, 1024), "red"), selection)
changed = delta(source, output)
assert ImageChops.multiply(changed, core).getbbox() is None
assert ImageChops.multiply(changed, ImageChops.invert(selected)).getbbox() is None
assert ImageChops.multiply(changed, face).histogram()[255] > 0
print(
    json.dumps(
        {
            "passed": True,
            "forehead_occlusion_allowed": True,
            "protected_features_changed": 0,
            "outside_changed_pixels": proof["outside_changed_pixels"],
            "native_calls": 0,
        }
    )
)
