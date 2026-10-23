"""CPU-only preparation and independent direct RGB acceptance audit."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image, ImageChops


def deny_native(event, args):
    if event == "import" and args[0].split(".")[0] in {
        "mlx",
        "mflux",
        "torch",
        "transformers",
    }:
        raise RuntimeError("Native import forbidden in CPU audit")
    if event.startswith("socket."):
        raise RuntimeError("Network forbidden in CPU audit")


sys.addaudithook(deny_native)


def read(path):
    with Image.open(path) as image:
        image.load()
        return image.convert("RGB")


def mask(path):
    with Image.open(path) as image:
        image.load()
        result = image.convert("L")
    counts = result.histogram()
    assert counts[0] + counts[255] == result.width * result.height
    return result


def delta(a, b):
    r, g, b = ImageChops.difference(a, b).split()
    return ImageChops.lighter(ImageChops.lighter(r, g), b).point(
        lambda n: 255 if n else 0
    )


def preflight(root):
    sys.path.insert(0, str(root / "worker"))
    from masked_edit import context
    from reference_contract import validate_reference

    request = json.loads((root / "flux/input.json").read_text())
    source = read(validate_reference(root / "flux/inputs", request["reference"]))
    canvas, selected, box, viewport = context(source, request["selection"])
    assert (
        ImageChops.difference(selected, mask(root / "head-mask.png")).getbbox() is None
    )
    core = mask(root / "protected-features.png")
    original_face = mask(root / "original-face.png")
    union = selected.copy()
    for part in ("front", "rear"):
        part_mask = mask(root / "retained" / f"{part}-mask.png")
        assert ImageChops.multiply(union, part_mask).getbbox() is None
        union = ImageChops.lighter(union, part_mask)
    assert ImageChops.multiply(union, core).getbbox() is None
    allowed = ImageChops.multiply(union, original_face)
    assert allowed.histogram()[255] > 0
    canvas.save(root / "context.png")
    union.save(root / "union.png")
    proof = {
        "native_calls": 0,
        "selected_pixels": selected.histogram()[255],
        "union_selected_pixels": union.histogram()[255],
        "protected_pixels": union.histogram()[0],
        "protected_feature_pixels": core.histogram()[255],
        "protected_feature_selected_pixels": 0,
        "original_face_pixels_allowed_for_occlusion": allowed.histogram()[255],
        "disjoint_regions": True,
        "box": box,
        "viewport": viewport,
    }
    (root / "cpu-preflight.json").write_text(json.dumps(proof, indent=2) + "\n")
    print(json.dumps({k: v for k, v in proof.items() if k not in ("box", "viewport")}))


def finish(root):
    # Only Pillow + frozen masks/data are used here. No compositor is imported.
    source = read(root / "flux/inputs/reference.png")
    output = read(root / "flux/working/image.png")
    export = read(root / "flux/working/export.png")
    selected = mask(root / "head-mask.png")
    core = mask(root / "protected-features.png")
    union = mask(root / "union.png")
    original_face = mask(root / "original-face.png")
    assert (
        ImageChops.multiply(
            delta(source, output), ImageChops.invert(selected)
        ).getbbox()
        is None
    )
    assert delta(output, export).getbbox() is None
    combined = output.copy()
    for part in ("front", "rear"):
        retained = read(root / "retained" / f"{part}.png")
        part_mask = mask(root / "retained" / f"{part}-mask.png")
        assert (
            ImageChops.multiply(
                delta(source, retained), ImageChops.invert(part_mask)
            ).getbbox()
            is None
        )
        combined.paste(retained, (0, 0), part_mask)
    changed = delta(source, combined)
    outside = ImageChops.multiply(changed, ImageChops.invert(union))
    protected_features = ImageChops.multiply(changed, core)
    assert outside.getbbox() is None and protected_features.getbbox() is None
    combined.save(root / "combined.png")
    box = json.loads((root / "cpu-preflight.json").read_text())["box"]
    combined.crop(box).save(root / "head-detail.png")
    proof = {
        "native_calls": 0,
        "outside_changed_pixels": outside.histogram()[255],
        "protected_pixels": union.histogram()[0],
        "protected_feature_pixels": core.histogram()[255],
        "protected_feature_changed_pixels": protected_features.histogram()[255],
        "old_face_outline_changed_pixels": ImageChops.multiply(
            changed, original_face
        ).histogram()[255],
        "old_face_outline_allowed_pixels": ImageChops.multiply(
            union, original_face
        ).histogram()[255],
        "head_export_matches_composite": True,
        "combined_png_bytes": (root / "combined.png").stat().st_size,
        "retained_glove_outputs_newly_generated": False,
    }
    (root / "pixel-audit.json").write_text(json.dumps(proof, indent=2) + "\n")
    print(json.dumps(proof))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("preflight", "finish"))
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    if args.action == "finish":
        frozen = json.loads((args.root / "frozen.json").read_text())
        assert (
            hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
            == frozen["files"]["worker/audit.py"]
        )
    {"preflight": preflight, "finish": finish}[args.action](args.root)
