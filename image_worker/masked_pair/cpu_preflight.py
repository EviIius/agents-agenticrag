"""Check exact pair inputs, common context and manual face protection on CPU."""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ROOT / "worker"))


def audit(event, args):
    if event == "import" and args[0].split(".")[0] in {
        "mlx",
        "mflux",
        "torch",
        "transformers",
    }:
        raise RuntimeError("Native imports forbidden during preflight")
    if event.startswith("socket."):
        raise RuntimeError("Network forbidden")


sys.addaudithook(audit)
from masked_edit import context, read_rgb
from PIL import Image, ImageChops, ImageDraw
from reference_contract import validate_reference

requests = [(ROOT / c / "input.json").read_bytes() for c in ("flux", "qwen")]
assert requests[0] == requests[1]
request = json.loads(requests[0])
assert request["seed"] == 42
signatures = []
for case in ("flux", "qwen"):
    source = read_rgb(validate_reference(ROOT / case / "inputs", request["reference"]))
    canvas, mask, box, viewport = context(source, request["selection"])
    face = Image.new("L", source.size, 0)
    points = json.loads((ROOT / "regions.json").read_text())["face_polygon"]
    ImageDraw.Draw(face).polygon([tuple(p) for p in points], fill=255)
    expected = json.loads((ROOT / "previous-coverage.json").read_text())
    assert face.histogram()[255] == expected["face_region_pixels"]
    assert mask.histogram()[255] == expected["selected_pixels"]
    assert ImageChops.multiply(mask, face).getbbox() is None
    canvas.save(ROOT / case / "cpu-context.png")
    mask.save(ROOT / case / "cpu-mask.png")
    signature = {
        "context_sha256": hashlib.sha256(canvas.tobytes()).hexdigest(),
        "mask_sha256": hashlib.sha256(mask.tobytes()).hexdigest(),
        "box": box,
        "viewport": viewport,
        "selected_pixels": mask.histogram()[255],
        "manual_face_selected_pixels": 0,
    }
    signatures.append(signature)
assert signatures[0] == signatures[1]
(ROOT / "cpu-preflight.json").write_text(json.dumps(signatures[0], indent=2) + "\n")
print(
    json.dumps(
        {
            "passed": True,
            "identical_request_context_mask": True,
            "selected_pixels": signatures[0]["selected_pixels"],
            "manual_face_selected_pixels": 0,
            "native_calls": 0,
        }
    )
)
